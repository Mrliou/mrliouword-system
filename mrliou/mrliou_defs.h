#ifndef MRLIOU_DEFS_H
#define MRLIOU_DEFS_H

/* ------------------------------------------------------------------ */
/* Mr.liou AI — core type definitions                                 */
/* All internal engine state is represented by the structs below.     */
/* ------------------------------------------------------------------ */

#include <stddef.h>
#include <time.h>
#include "config.h"

/* ---- Memory entry -------------------------------------------------
   Persistent knowledge unit stored in memory.txt as:
   KEY|VALUE|WEIGHT|TIMESTAMP
   ------------------------------------------------------------------ */
typedef struct {
    char    key[MRLIOU_MAX_KEY];
    char    value[MRLIOU_MAX_TEXT];
    float   weight;         /* relevance / confidence 0.0–1.0 */
    time_t  timestamp;
} MemoryEntry;

/* ---- Growth snapshot ----------------------------------------------
   Appended to growth.log after every learning cycle.
   One line per snapshot: VERSION|LEARNED|REASON_LVL|GEN_QUAL|TS|NOTES
   ------------------------------------------------------------------ */
typedef struct {
    int     version;
    int     total_learned;
    float   reasoning_level;    /* 0.0–1.0, increases with cycles */
    float   generation_quality; /* 0.0–1.0, improves over time */
    time_t  timestamp;
    char    notes[MRLIOU_MAX_KEY];
} GrowthSnapshot;

/* ---- Reasoning result --------------------------------------------- */
typedef struct {
    char    intent[256];            /* question / command / statement */
    char    keywords[MRLIOU_MAX_TEXT]; /* space-separated keyword list */
    char    inference[MRLIOU_MAX_TEXT];/* derived conclusion */
    float   confidence;             /* 0.0–1.0 */
    char    evidence[MRLIOU_MAX_TEXT]; /* supporting memory keys used */
} ReasoningResult;

/* ---- Learning result ---------------------------------------------- */
typedef struct {
    int     entries_added;
    int     entries_updated;
    char    summary[MRLIOU_MAX_TEXT];
} LearningResult;

/* ---- Generation result -------------------------------------------- */
typedef struct {
    char    output[MRLIOU_MAX_TEXT * 2];
    char    strategy[256];   /* e.g. "recall+expand", "infer+compose" */
    float   quality;         /* 0.0–1.0 */
} GenerationResult;

/* ---- HTTP request (parsed) ---------------------------------------- */
typedef struct {
    char    method[16];
    char    path[256];
    char    body[MRLIOU_BUF_SIZE];
    int     body_len;
} HttpRequest;

/* ---- HTTP response ------------------------------------------------ */
typedef struct {
    int     status_code;
    char    content_type[64];
    char    body[MRLIOU_BUF_SIZE];
    int     body_len;
} HttpResponse;

/* ---- Route handler type ------------------------------------------- */
typedef void (*RouteHandler)(const HttpRequest *req, HttpResponse *resp);

/* ---- Route entry -------------------------------------------------- */
typedef struct {
    char            method[16];
    char            path[256];
    RouteHandler    handler;
} Route;

/* ---- System state ------------------------------------------------- */
typedef struct {
    int             memory_count;
    int             growth_version;
    float           reasoning_level;
    float           generation_quality;
    long            requests_handled;
    time_t          started_at;
} SystemState;

#endif /* MRLIOU_DEFS_H */
