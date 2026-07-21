#ifndef MRLIOU_GROWTH_H
#define MRLIOU_GROWTH_H

#include "mrliou_defs.h"

/* ------------------------------------------------------------------ */
/* Growth module — capability snapshots and evolution log             */
/* Backed by a plain-text append-only file (data/growth.log).         */
/* Log format per line:                                               */
/*   VERSION|TOTAL_LEARNED|REASON_LVL|GEN_QUAL|TIMESTAMP|NOTES        */
/* ------------------------------------------------------------------ */

/* Initialise and load growth history from disk.  Returns 0. */
int  growth_init(void);

/* Record a growth event.  Pass notes describing what changed.
   Increments the internal version counter and appends to the log.
   Returns 0 on success. */
int  growth_record(int total_learned, float reasoning_level,
                   float gen_quality,  const char *notes);

/* Return the current growth version (number of snapshots taken). */
int  growth_version(void);

/* Fill a plain-text status report into buf (max len bytes).
   Returns bytes written. */
int  growth_report(char *buf, int len);

/* Free resources. */
void growth_shutdown(void);

#endif /* MRLIOU_GROWTH_H */
