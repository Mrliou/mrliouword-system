#ifndef MRLIOU_GENERATION_H
#define MRLIOU_GENERATION_H

#include "mrliou_defs.h"

/* ------------------------------------------------------------------ */
/* Generation module — response composition                           */
/* Combines reasoning results with memory to produce a final output.  */
/* ------------------------------------------------------------------ */

/* Initialise the generation engine.  Returns 0. */
int generation_init(void);

/* Generate a response for the given input using the supplied reasoning
   result as context.  Fills *result.  Returns 0 on success. */
int generation_compose(const char *input,
                       const ReasoningResult *reasoning,
                       GenerationResult *result);

/* Free resources. */
void generation_shutdown(void);

#endif /* MRLIOU_GENERATION_H */
