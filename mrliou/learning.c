/* ------------------------------------------------------------------ */
/* Mr.liou AI — learning module                                       */
/* Extracts facts from input text and stores them in memory.          */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>
#include <time.h>
#include "learning.h"
#include "memory.h"
#include "config.h"

/* ---- helpers ----------------------------------------------------- */

/* Trim leading/trailing whitespace in-place */
static void trim(char *s)
{
    int len = (int)strlen(s);
    while (len > 0 && isspace((unsigned char)s[len - 1])) s[--len] = '\0';
    int start = 0;
    while (s[start] && isspace((unsigned char)s[start])) start++;
    if (start > 0) memmove(s, s + start, (size_t)(len - start + 1));
}

/* Try to parse a "key=value" or "key: value" pair.
   Returns 1 if parsed, 0 otherwise. */
static int parse_kv(const char *line, char *key, int klen, char *val, int vlen)
{
    const char *sep = strchr(line, '=');
    if (!sep) sep = strchr(line, ':');
    if (!sep) return 0;

    int ks = (int)(sep - line);
    if (ks <= 0 || ks >= klen) return 0;

    strncpy(key, line, (size_t)ks);
    key[ks] = '\0';
    trim(key);
    if (strlen(key) == 0) return 0;

    strncpy(val, sep + 1, (size_t)(vlen - 1));
    val[vlen - 1] = '\0';
    trim(val);
    if (strlen(val) == 0) return 0;

    return 1;
}

/* Derive an auto-key from a sentence: take the first 4 non-stop words
   and join them with underscores. */
static const char *STOP[] = {
    "a","an","the","is","are","was","were","be","been","being",
    "have","has","had","do","does","did","will","would","could",
    "should","this","that","and","or","but","it","i","you","we",
    NULL
};

static int is_stop_lrn(const char *w)
{
    for (int i = 0; STOP[i]; i++)
        if (strcasecmp(w, STOP[i]) == 0) return 1;
    return 0;
}

static void make_auto_key(const char *sentence, char *key, int klen)
{
    char buf[MRLIOU_MAX_TEXT];
    strncpy(buf, sentence, MRLIOU_MAX_TEXT - 1);
    buf[MRLIOU_MAX_TEXT - 1] = '\0';

    key[0] = '\0';
    int parts = 0;
    char *tok = strtok(buf, " \t\n\r.,!?;:\"'()[]");
    while (tok && parts < 4) {
        char lower[MRLIOU_MAX_KEY];
        strncpy(lower, tok, MRLIOU_MAX_KEY - 1);
        lower[MRLIOU_MAX_KEY - 1] = '\0';
        for (int i = 0; lower[i]; i++)
            lower[i] = (char)tolower((unsigned char)lower[i]);

        if (strlen(lower) > 1 && !is_stop_lrn(lower)) {
            int remaining = klen - (int)strlen(key) - 1;
            if (remaining > 0) {
                if (parts > 0 && remaining > 1) {
                    strncat(key, "_", 1);
                    remaining--;
                }
                if (remaining > 0) {
                    /* use memcpy to avoid the strncat truncation warning */
                    size_t kpos  = strlen(key);
                    size_t llen  = strlen(lower);
                    if ((int)llen > remaining) llen = (size_t)remaining;
                    memcpy(key + kpos, lower, llen);
                    key[kpos + llen] = '\0';
                }
            }
            parts++;
        }
        tok = strtok(NULL, " \t\n\r.,!?;:\"'()[]");
    }
    if (key[0] == '\0') {
        strncpy(key, "fact", (size_t)(klen - 1));
        key[klen - 1] = '\0';
    }
}

/* ---- public API -------------------------------------------------- */

int learning_init(void)
{
    return 0;
}

int learning_absorb(const char *input, LearningResult *result)
{
    if (!input || !result) return -1;
    memset(result, 0, sizeof(*result));

    char key[MRLIOU_MAX_KEY];
    char val[MRLIOU_MAX_TEXT];

    /* Process line-by-line — each line may be a separate fact */
    char buf[MRLIOU_MAX_TEXT * 2];
    strncpy(buf, input, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';

    char *line = strtok(buf, "\n\r");
    while (line) {
        trim(line);
        if (strlen(line) < 2) { line = strtok(NULL, "\n\r"); continue; }

        MemoryEntry existing;
        int was_update = 0;

        if (parse_kv(line, key, sizeof(key), val, sizeof(val))) {
            /* explicit key=value or key: value */
            was_update = memory_get(key, &existing);
            memory_store(key, val, 0.8f);
        } else {
            /* free text — derive auto key from sentence */
            make_auto_key(line, key, sizeof(key));
            was_update = memory_get(key, &existing);
            memory_store(key, line, 0.6f);
            strncpy(val, line, sizeof(val) - 1);
            val[sizeof(val) - 1] = '\0';
        }

        if (was_update)
            result->entries_updated++;
        else
            result->entries_added++;

        line = strtok(NULL, "\n\r");
    }

    snprintf(result->summary, sizeof(result->summary),
             "absorbed: +%d new, ~%d updated (total memory: %d)",
             result->entries_added, result->entries_updated, memory_count());

    return 0;
}

void learning_shutdown(void)
{
    /* nothing to release */
}
