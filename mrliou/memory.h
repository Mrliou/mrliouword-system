#ifndef MRLIOU_MEMORY_H
#define MRLIOU_MEMORY_H

#include "mrliou_defs.h"

/* ------------------------------------------------------------------ */
/* Memory module — persistent key-value knowledge store              */
/* Backed by a plain-text file (data/memory.txt).                    */
/* File format: one record per line — KEY|VALUE|WEIGHT|TIMESTAMP     */
/* ------------------------------------------------------------------ */

/* Initialise the in-memory table and load from disk if the file
   already exists.  Returns 0 on success, -1 on error. */
int  memory_init(void);

/* Store or update a memory entry.
   If the key already exists its value and weight are overwritten.
   Returns 0 on success. */
int  memory_store(const char *key, const char *value, float weight);

/* Retrieve the most-recent entry whose key matches exactly.
   Returns 1 if found and fills *out, 0 if not found. */
int  memory_get(const char *key, MemoryEntry *out);

/* Search entries whose key or value contains substring.
   Writes up to max results into out[].  Returns count found. */
int  memory_search(const char *substring, MemoryEntry *out, int max);

/* Return the total number of stored entries. */
int  memory_count(void);

/* Flush current table to disk.  Called automatically when
   MRLIOU_PERSIST_ON_WRITE is set.  Returns 0 on success. */
int  memory_persist(void);

/* Load table from disk, replacing the current in-memory table.
   Returns 0 on success. */
int  memory_load(void);

/* Free all in-memory state (called at shutdown). */
void memory_shutdown(void);

/* Fill a plain-text report into buf (max len bytes).
   Returns number of bytes written. */
int  memory_report(char *buf, int len);

#endif /* MRLIOU_MEMORY_H */
