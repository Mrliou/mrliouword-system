#ifndef MRLIOU_CONFIG_H
#define MRLIOU_CONFIG_H

/* ------------------------------------------------------------------ */
/* Mr.liou AI Local Server — compile-time configuration               */
/* Edit this header and recompile to change runtime behaviour.        */
/* ------------------------------------------------------------------ */

/* Network */
#define MRLIOU_PORT           7890
#define MRLIOU_BACKLOG        16
#define MRLIOU_BUF_SIZE       8192

/* Data directory and plain-text state files */
#define MRLIOU_DATA_DIR       "./data"
#define MRLIOU_MEMORY_FILE    "./data/memory.txt"
#define MRLIOU_GROWTH_FILE    "./data/growth.log"
#define MRLIOU_SERVER_LOG     "./data/server.log"

/* Engine limits */
#define MRLIOU_MAX_MEMORY     1024   /* max stored memory entries */
#define MRLIOU_MAX_GROWTH     256    /* max growth snapshots kept */
#define MRLIOU_MAX_TEXT       2048   /* max text field length */
#define MRLIOU_MAX_KEY        128    /* max key/label length */
#define MRLIOU_MAX_KEYWORDS   32     /* max keywords extracted per input */
#define MRLIOU_MAX_ROUTES     32     /* max registered HTTP routes */

/* Identity */
#define MRLIOU_VERSION        "1.0.0"
#define MRLIOU_NAME           "Mr.liou AI"
#define MRLIOU_DESCRIPTION    "Local reasoning, learning, growth and generation service"

/* Behaviour */
#define MRLIOU_PERSIST_ON_WRITE  1   /* 1 = flush memory to disk after every write */

#endif /* MRLIOU_CONFIG_H */
