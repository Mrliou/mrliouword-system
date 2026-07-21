#ifndef MRLIOU_LEARNING_H
#define MRLIOU_LEARNING_H

#include "mrliou_defs.h"

/* ------------------------------------------------------------------ */
/* Learning module — knowledge extraction and memory update           */
/* ------------------------------------------------------------------ */

/* Initialise the learning engine.  Returns 0 on success. */
int learning_init(void);

/* Absorb text: extract facts and store them in memory.
   The input may be a raw sentence, a key=value pair, or free text.
   Fills *result with what was added / updated.
   Returns 0 on success. */
int learning_absorb(const char *input, LearningResult *result);

/* Free resources. */
void learning_shutdown(void);

#endif /* MRLIOU_LEARNING_H */
