#ifndef MRLIOU_REASONING_H
#define MRLIOU_REASONING_H

#include "mrliou_defs.h"

/* ------------------------------------------------------------------ */
/* Reasoning module — intent parsing, keyword extraction, inference   */
/* ------------------------------------------------------------------ */

/* Initialise the reasoning engine (call once at startup).
   Returns 0 on success. */
int reasoning_init(void);

/* Analyse input text.
   Fills *result with intent, keywords, inference chain, and a
   confidence score derived from memory lookups.
   Returns 0 on success. */
int reasoning_analyse(const char *input, ReasoningResult *result);

/* Free any resources held by the reasoning engine. */
void reasoning_shutdown(void);

#endif /* MRLIOU_REASONING_H */
