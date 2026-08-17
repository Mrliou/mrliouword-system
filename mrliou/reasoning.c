/* ------------------------------------------------------------------ */
/* Mr.liou AI — reasoning module                                      */
/* Intent detection, keyword extraction, memory-backed inference.     */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>
#include "reasoning.h"
#include "memory.h"
#include "config.h"

/* ---- question words used for intent detection -------------------- */
static const char *QUESTION_WORDS[] = {
    "what","who","where","when","why","how","which","whose",
    "是什麼","為什麼","怎麼","哪裡","誰","什麼",
    NULL
};

/* ---- common stop-words (skip during keyword extraction) ---------- */
static const char *STOP_WORDS[] = {
    "a","an","the","is","are","was","were","be","been","being",
    "have","has","had","do","does","did","will","would","could",
    "should","may","might","shall","can","need","dare","ought",
    "to","of","in","on","at","by","for","with","from","into",
    "through","during","including","until","against","among",
    "i","you","he","she","it","we","they","me","him","her",
    "us","them","my","your","his","its","our","their",
    "this","that","these","those","and","or","but","if",
    "because","as","while","although","before","after","since",
    NULL
};

static int is_stop(const char *word)
{
    for (int i = 0; STOP_WORDS[i]; i++) {
        if (strcasecmp(word, STOP_WORDS[i]) == 0) return 1;
    }
    return 0;
}

static int is_question_word(const char *word)
{
    for (int i = 0; QUESTION_WORDS[i]; i++) {
        if (strcasecmp(word, QUESTION_WORDS[i]) == 0) return 1;
    }
    return 0;
}

/* Detect intent from the input text.
   Returns "question", "command", or "statement". */
static const char *detect_intent(const char *input)
{
    /* check for question mark */
    /* check for question mark (ASCII and UTF-8 fullwidth ？ = 0xEF 0xBC 0x9F) */
    if (strchr(input, '?') || strstr(input, "\xef\xbc\x9f")) return "question";

    /* tokenise and look for question words */
    char buf[MRLIOU_MAX_TEXT];
    strncpy(buf, input, MRLIOU_MAX_TEXT - 1);
    buf[MRLIOU_MAX_TEXT - 1] = '\0';

    char *tok = strtok(buf, " \t\n\r.,!?;:");
    while (tok) {
        if (is_question_word(tok)) return "question";
        tok = strtok(NULL, " \t\n\r.,!?;:");
    }

    /* check for imperative-like start (common command verbs) */
    const char *cmd_verbs[] = {
        "tell","show","give","list","find","search","explain",
        "describe","create","generate","learn","store","remember",
        "analyse","analyze","think","reason",
        "告訴","顯示","給我","列出","找","搜尋","解釋","建立","生成","記住",
        NULL
    };
    char first[MRLIOU_MAX_KEY];
    strncpy(first, input, MRLIOU_MAX_KEY - 1);
    first[MRLIOU_MAX_KEY - 1] = '\0';
    char *space = strchr(first, ' ');
    if (space) *space = '\0';
    for (int i = 0; cmd_verbs[i]; i++) {
        if (strcasecmp(first, cmd_verbs[i]) == 0) return "command";
    }

    return "statement";
}

/* Extract up to MRLIOU_MAX_KEYWORDS non-stop-word tokens from input.
   Writes them space-separated into *out (max out_len bytes). */
static void extract_keywords(const char *input, char *out, int out_len)
{
    char buf[MRLIOU_MAX_TEXT];
    strncpy(buf, input, MRLIOU_MAX_TEXT - 1);
    buf[MRLIOU_MAX_TEXT - 1] = '\0';

    char tmp[MRLIOU_MAX_KEY];
    int  written = 0;
    int  kcount  = 0;
    out[0]       = '\0';

    char *tok = strtok(buf, " \t\n\r.,!?;:\"'()[]{}");
    while (tok && kcount < MRLIOU_MAX_KEYWORDS) {
        /* lowercase copy for stop-word check */
        strncpy(tmp, tok, MRLIOU_MAX_KEY - 1);
        tmp[MRLIOU_MAX_KEY - 1] = '\0';
        for (int i = 0; tmp[i]; i++) tmp[i] = (char)tolower((unsigned char)tmp[i]);

        if (strlen(tmp) > 1 && !is_stop(tmp)) {
            int need = (int)strlen(tok) + (kcount > 0 ? 1 : 0);
            if (written + need < out_len) {
                if (kcount > 0) { strcat(out, " "); written++; }
                strcat(out, tok);
                written += (int)strlen(tok);
                kcount++;
            }
        }
        tok = strtok(NULL, " \t\n\r.,!?;:\"'()[]{}");
    }
}

/* Build an inference by searching memory for each keyword. */
static void build_inference(const char *keywords, char *inference, int inf_len,
                             char *evidence, int ev_len, float *confidence)
{
    char kw_buf[MRLIOU_MAX_TEXT];
    strncpy(kw_buf, keywords, MRLIOU_MAX_TEXT - 1);
    kw_buf[MRLIOU_MAX_TEXT - 1] = '\0';

    MemoryEntry hits[8];
    int total_hits = 0;

    inference[0] = '\0';
    evidence[0]  = '\0';

    char *tok = strtok(kw_buf, " ");
    while (tok) {
        int n = memory_search(tok, hits, 8);
        for (int i = 0; i < n && total_hits < 8; i++, total_hits++) {
            /* append evidence key */
            if (strlen(evidence) + strlen(hits[i].key) + 2 < (size_t)ev_len) {
                if (total_hits > 0) strncat(evidence, ", ", ev_len - strlen(evidence) - 1);
                strncat(evidence, hits[i].key, ev_len - strlen(evidence) - 1);
            }
            /* append a sentence from each memory value */
            int inf_remaining = inf_len - (int)strlen(inference) - 1;
            if (inf_remaining > 10) {
                strncat(inference, hits[i].value, (size_t)inf_remaining - 1);
                if (i < n - 1)
                    strncat(inference, " | ", (size_t)(inf_len - (int)strlen(inference) - 1));
            }
        }
        tok = strtok(NULL, " ");
    }

    if (total_hits == 0) {
        strncpy(inference, "(no relevant memory found — ready to learn)", inf_len - 1);
        *confidence = 0.1f;
    } else {
        *confidence = total_hits > 4 ? 0.9f : 0.3f + total_hits * 0.1f;
    }
}

/* ---- public API -------------------------------------------------- */

int reasoning_init(void)
{
    /* nothing to allocate — uses memory module via memory_search */
    return 0;
}

int reasoning_analyse(const char *input, ReasoningResult *result)
{
    if (!input || !result) return -1;

    memset(result, 0, sizeof(*result));

    strncpy(result->intent,
            detect_intent(input),
            sizeof(result->intent) - 1);

    extract_keywords(input,
                     result->keywords,
                     sizeof(result->keywords));

    build_inference(result->keywords,
                    result->inference, sizeof(result->inference),
                    result->evidence,  sizeof(result->evidence),
                    &result->confidence);

    return 0;
}

void reasoning_shutdown(void)
{
    /* nothing to release */
}
