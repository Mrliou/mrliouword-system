/* ------------------------------------------------------------------ */
/* Mr.liou AI — generation module                                     */
/* Composes text output from reasoning context + memory.              */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "generation.h"
#include "memory.h"
#include "config.h"

/* ---- strategy selection ------------------------------------------ */
/* Choose a composition strategy based on intent and confidence. */
static const char *pick_strategy(const char *intent, float confidence)
{
    if (strcmp(intent, "question") == 0) {
        return confidence > 0.5f ? "recall+answer" : "infer+ask-back";
    }
    if (strcmp(intent, "command") == 0) {
        return "plan+execute";
    }
    return confidence > 0.4f ? "recall+expand" : "infer+compose";
}

/* ---- public API -------------------------------------------------- */

int generation_init(void)
{
    return 0;
}

int generation_compose(const char *input,
                       const ReasoningResult *reasoning,
                       GenerationResult *result)
{
    if (!input || !reasoning || !result) return -1;
    memset(result, 0, sizeof(*result));

    const char *strategy = pick_strategy(reasoning->intent, reasoning->confidence);
    strncpy(result->strategy, strategy, sizeof(result->strategy) - 1);

    /* --- build the output text ------------------------------------ */
    char *out    = result->output;
    int   outlen = (int)sizeof(result->output);
    int   pos    = 0;

    /* header line */
    pos += snprintf(out + pos, (size_t)(outlen - pos),
                    "[Mr.liou AI — strategy: %s]\n\n", strategy);

    /* Echo the detected intent */
    pos += snprintf(out + pos, (size_t)(outlen - pos),
                    "Intent   : %s\n", reasoning->intent);
    pos += snprintf(out + pos, (size_t)(outlen - pos),
                    "Keywords : %s\n",
                    reasoning->keywords[0] ? reasoning->keywords : "(none)");
    pos += snprintf(out + pos, (size_t)(outlen - pos),
                    "Confidence: %.0f%%\n\n",
                    (double)(reasoning->confidence * 100.0f));

    /* if we have memory-backed inference, present it */
    if (reasoning->inference[0]) {
        pos += snprintf(out + pos, (size_t)(outlen - pos),
                        "Based on memory:\n%s\n\n", reasoning->inference);
        if (reasoning->evidence[0]) {
            pos += snprintf(out + pos, (size_t)(outlen - pos),
                            "Evidence keys: %s\n\n", reasoning->evidence);
        }
    }

    /* generate a composed response depending on strategy */
    if (strcmp(strategy, "recall+answer") == 0) {
        pos += snprintf(out + pos, (size_t)(outlen - pos),
                        "Answer: %s", reasoning->inference);
    } else if (strcmp(strategy, "infer+ask-back") == 0) {
        pos += snprintf(out + pos, (size_t)(outlen - pos),
                        "I don't have enough memory to answer fully.\n"
                        "You can teach me with: POST /learn  body: key=value\n"
                        "Or provide more context in your input.\n");
    } else if (strcmp(strategy, "plan+execute") == 0) {
        pos += snprintf(out + pos, (size_t)(outlen - pos),
                        "Command acknowledged.\n"
                        "Executing based on available knowledge.\n");
        if (reasoning->inference[0])
            pos += snprintf(out + pos, (size_t)(outlen - pos),
                            "Result: %s\n", reasoning->inference);
    } else {
        /* recall+expand or infer+compose */
        pos += snprintf(out + pos, (size_t)(outlen - pos),
                        "Composed response:\n");
        if (reasoning->inference[0]) {
            pos += snprintf(out + pos, (size_t)(outlen - pos),
                            "%s\n", reasoning->inference);
        } else {
            pos += snprintf(out + pos, (size_t)(outlen - pos),
                            "No matching memory found for: \"%s\"\n"
                            "Use POST /learn to add knowledge.\n", input);
        }
    }

    /* quality heuristic: based on how much memory was consulted */
    result->quality = reasoning->confidence;

    return 0;
}

void generation_shutdown(void)
{
    /* nothing to release */
}
