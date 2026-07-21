/* ------------------------------------------------------------------ */
/* Mr.liou AI — memory module                                         */
/* Persistent key-value knowledge store backed by plain-text file.   */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include "memory.h"
#include "config.h"

/* ---- internal storage -------------------------------------------- */
static MemoryEntry g_table[MRLIOU_MAX_MEMORY];
static int         g_count = 0;

/* ---- helpers ----------------------------------------------------- */

static void ensure_data_dir(void)
{
    struct stat st;
    if (stat(MRLIOU_DATA_DIR, &st) != 0) {
        /* best-effort directory creation */
#ifdef _WIN32
        _mkdir(MRLIOU_DATA_DIR);
#else
        mkdir(MRLIOU_DATA_DIR, 0755);
#endif
    }
}

/* Escape pipe characters in string so they don't break the file format */
static void escape_pipe(const char *src, char *dst, int dst_len)
{
    int j = 0;
    for (int i = 0; src[i] && j < dst_len - 1; i++) {
        if (src[i] == '|') {
            if (j < dst_len - 2) { dst[j++] = '\\'; dst[j++] = '|'; }
        } else {
            dst[j++] = src[i];
        }
    }
    dst[j] = '\0';
}

/* Unescape \\| sequences produced by escape_pipe */
static void unescape_pipe(const char *src, char *dst, int dst_len)
{
    int j = 0;
    for (int i = 0; src[i] && j < dst_len - 1; i++) {
        if (src[i] == '\\' && src[i + 1] == '|') {
            dst[j++] = '|';
            i++;
        } else {
            dst[j++] = src[i];
        }
    }
    dst[j] = '\0';
}

/* ---- public API -------------------------------------------------- */

int memory_init(void)
{
    ensure_data_dir();
    g_count = 0;
    return memory_load();
}

int memory_store(const char *key, const char *value, float weight)
{
    if (!key || !value) return -1;

    /* update existing entry */
    for (int i = 0; i < g_count; i++) {
        if (strncmp(g_table[i].key, key, MRLIOU_MAX_KEY) == 0) {
            strncpy(g_table[i].value, value, MRLIOU_MAX_TEXT - 1);
            g_table[i].value[MRLIOU_MAX_TEXT - 1] = '\0';
            g_table[i].weight    = weight;
            g_table[i].timestamp = time(NULL);
#if MRLIOU_PERSIST_ON_WRITE
            memory_persist();
#endif
            return 0;
        }
    }

    /* add new entry */
    if (g_count >= MRLIOU_MAX_MEMORY) return -1;

    strncpy(g_table[g_count].key,   key,   MRLIOU_MAX_KEY - 1);
    strncpy(g_table[g_count].value, value, MRLIOU_MAX_TEXT - 1);
    g_table[g_count].key[MRLIOU_MAX_KEY - 1]    = '\0';
    g_table[g_count].value[MRLIOU_MAX_TEXT - 1]  = '\0';
    g_table[g_count].weight    = weight;
    g_table[g_count].timestamp = time(NULL);
    g_count++;

#if MRLIOU_PERSIST_ON_WRITE
    memory_persist();
#endif
    return 0;
}

int memory_get(const char *key, MemoryEntry *out)
{
    if (!key || !out) return 0;
    for (int i = 0; i < g_count; i++) {
        if (strncmp(g_table[i].key, key, MRLIOU_MAX_KEY) == 0) {
            *out = g_table[i];
            return 1;
        }
    }
    return 0;
}

int memory_search(const char *substring, MemoryEntry *out, int max)
{
    if (!substring || !out || max <= 0) return 0;
    int found = 0;
    for (int i = 0; i < g_count && found < max; i++) {
        if (strstr(g_table[i].key,   substring) ||
            strstr(g_table[i].value, substring)) {
            out[found++] = g_table[i];
        }
    }
    return found;
}

int memory_count(void)
{
    return g_count;
}

int memory_persist(void)
{
    ensure_data_dir();
    FILE *fp = fopen(MRLIOU_MEMORY_FILE, "w");
    if (!fp) return -1;

    char ek[MRLIOU_MAX_KEY * 2];
    char ev[MRLIOU_MAX_TEXT * 2];

    for (int i = 0; i < g_count; i++) {
        escape_pipe(g_table[i].key,   ek, sizeof(ek));
        escape_pipe(g_table[i].value, ev, sizeof(ev));
        fprintf(fp, "%s|%s|%.4f|%ld\n",
                ek, ev,
                (double)g_table[i].weight,
                (long)g_table[i].timestamp);
    }
    fclose(fp);
    return 0;
}

int memory_load(void)
{
    FILE *fp = fopen(MRLIOU_MEMORY_FILE, "r");
    if (!fp) return 0; /* no file yet — that is fine */

    char line[MRLIOU_MAX_KEY + MRLIOU_MAX_TEXT * 2 + 64];
    g_count = 0;

    while (fgets(line, sizeof(line), fp) && g_count < MRLIOU_MAX_MEMORY) {
        /* strip trailing newline */
        int len = (int)strlen(line);
        while (len > 0 && (line[len-1] == '\n' || line[len-1] == '\r'))
            line[--len] = '\0';

        /* split on unescaped | */
        char *fields[4];
        int   nf = 0;
        char *p  = line;

        fields[nf++] = p;
        while (*p && nf < 4) {
            if (*p == '\\' && *(p+1) == '|') { p += 2; continue; }
            if (*p == '|') { *p = '\0'; fields[nf++] = p + 1; }
            p++;
        }
        if (nf < 4) continue;

        char ukey[MRLIOU_MAX_KEY];
        char uval[MRLIOU_MAX_TEXT];
        unescape_pipe(fields[0], ukey, sizeof(ukey));
        unescape_pipe(fields[1], uval, sizeof(uval));

        /* unescape_pipe already null-terminates; copy with memcpy to avoid
           the strncpy same-size truncation warning */
        size_t klen = strlen(ukey);
        if (klen >= MRLIOU_MAX_KEY) klen = MRLIOU_MAX_KEY - 1;
        memcpy(g_table[g_count].key, ukey, klen);
        g_table[g_count].key[klen] = '\0';

        size_t vlen = strlen(uval);
        if (vlen >= MRLIOU_MAX_TEXT) vlen = MRLIOU_MAX_TEXT - 1;
        memcpy(g_table[g_count].value, uval, vlen);
        g_table[g_count].value[vlen] = '\0';

        g_table[g_count].weight    = (float)atof(fields[2]);
        g_table[g_count].timestamp = (time_t)atol(fields[3]);
        g_count++;
    }
    fclose(fp);
    return 0;
}

void memory_shutdown(void)
{
    memory_persist();
    g_count = 0;
}

int memory_report(char *buf, int len)
{
    if (!buf || len <= 0) return 0;
    int written = snprintf(buf, (size_t)len,
        "MODULE: memory\n"
        "TOTAL_ENTRIES: %d\n"
        "MAX_ENTRIES: %d\n"
        "FILE: %s\n",
        g_count, MRLIOU_MAX_MEMORY, MRLIOU_MEMORY_FILE);
    return written < len ? written : len - 1;
}
