/* ------------------------------------------------------------------ */
/* Mr.liou AI — growth module                                         */
/* Append-only capability snapshot log in plain text.                 */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include "growth.h"
#include "config.h"

static int            g_version = 0;
static GrowthSnapshot g_latest;

static void ensure_data_dir(void)
{
    struct stat st;
    if (stat(MRLIOU_DATA_DIR, &st) != 0) {
#ifdef _WIN32
        _mkdir(MRLIOU_DATA_DIR);
#else
        mkdir(MRLIOU_DATA_DIR, 0755);
#endif
    }
}

/* ---- public API -------------------------------------------------- */

int growth_init(void)
{
    ensure_data_dir();
    memset(&g_latest, 0, sizeof(g_latest));
    g_version = 0;

    /* Load the last line of the growth log to restore state */
    FILE *fp = fopen(MRLIOU_GROWTH_FILE, "r");
    if (!fp) return 0;

    char line[512];
    char last[512];
    last[0] = '\0';
    while (fgets(line, sizeof(line), fp)) {
        strncpy(last, line, sizeof(last) - 1);
        last[sizeof(last) - 1] = '\0';
    }
    fclose(fp);

    if (last[0] == '\0') return 0;

    /* strip trailing newline */
    int len = (int)strlen(last);
    while (len > 0 && (last[len-1] == '\n' || last[len-1] == '\r'))
        last[--len] = '\0';

    /* parse VERSION|TOTAL|RLVL|GQUAL|TS|NOTES */
    char *fields[6];
    int   nf = 0;
    char *p  = last;
    fields[nf++] = p;
    while (*p && nf < 6) {
        if (*p == '|') { *p = '\0'; fields[nf++] = p + 1; }
        p++;
    }
    if (nf >= 6) {
        g_version                  = atoi(fields[0]);
        g_latest.version           = g_version;
        g_latest.total_learned     = atoi(fields[1]);
        g_latest.reasoning_level   = (float)atof(fields[2]);
        g_latest.generation_quality= (float)atof(fields[3]);
        g_latest.timestamp         = (time_t)atol(fields[4]);
        strncpy(g_latest.notes, fields[5], sizeof(g_latest.notes) - 1);
        g_latest.notes[sizeof(g_latest.notes) - 1] = '\0';
    }
    return 0;
}

int growth_record(int total_learned, float reasoning_level,
                  float gen_quality,  const char *notes)
{
    ensure_data_dir();

    g_version++;
    g_latest.version            = g_version;
    g_latest.total_learned      = total_learned;
    g_latest.reasoning_level    = reasoning_level;
    g_latest.generation_quality = gen_quality;
    g_latest.timestamp          = time(NULL);
    if (notes) {
        strncpy(g_latest.notes, notes, sizeof(g_latest.notes) - 1);
        g_latest.notes[sizeof(g_latest.notes) - 1] = '\0';
    }

    FILE *fp = fopen(MRLIOU_GROWTH_FILE, "a");
    if (!fp) return -1;
    fprintf(fp, "%d|%d|%.4f|%.4f|%ld|%s\n",
            g_version, total_learned,
            (double)reasoning_level, (double)gen_quality,
            (long)g_latest.timestamp,
            notes ? notes : "");
    fclose(fp);
    return 0;
}

int growth_version(void)
{
    return g_version;
}

int growth_report(char *buf, int len)
{
    if (!buf || len <= 0) return 0;

    char ts_buf[32];
    struct tm *tm_info = localtime(&g_latest.timestamp);
    if (tm_info)
        strftime(ts_buf, sizeof(ts_buf), "%Y-%m-%d %H:%M:%S", tm_info);
    else
        strncpy(ts_buf, "(unknown)", sizeof(ts_buf) - 1);

    return snprintf(buf, (size_t)len,
        "MODULE: growth\n"
        "VERSION: %d\n"
        "TOTAL_LEARNED: %d\n"
        "REASONING_LEVEL: %.4f\n"
        "GENERATION_QUALITY: %.4f\n"
        "LAST_UPDATED: %s\n"
        "LAST_NOTES: %s\n",
        g_latest.version,
        g_latest.total_learned,
        (double)g_latest.reasoning_level,
        (double)g_latest.generation_quality,
        ts_buf,
        g_latest.notes[0] ? g_latest.notes : "(none)");
}

void growth_shutdown(void)
{
    /* append-only log needs no flush */
}
