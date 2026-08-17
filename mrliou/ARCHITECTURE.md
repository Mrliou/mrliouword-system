# Mr.liou AI — Core Architecture

**Version:** 1.0.0  
**Language:** C (C99, POSIX)  
**Runtime:** Local HTTP server — no cloud dependency  

---

## 1. Overview

Mr.liou AI is a locally runnable, C-language service providing five core capabilities:

| Capability | Module | Description |
|---|---|---|
| Reasoning | `reasoning.c` | Intent detection, keyword extraction, memory-backed inference |
| Thinking | `router.c` `/think` | Full reasoning + generation pipeline |
| Learning | `learning.c` | Knowledge extraction from text, memory update |
| Growth | `growth.c` | Capability snapshot log, evolution tracking |
| Generation | `generation.c` | Response composition from reasoning context |

All state is stored in **plain text files** under `data/` — no JSON runtime config, no cloud connection required.

---

## 2. Module Map

```
mrliou/
├── config.h          — compile-time constants (port, paths, limits)
├── mrliou_defs.h     — core struct definitions
│
├── main.c            — entry point, signal handling, server start
│
├── server.h/c        — POSIX TCP socket HTTP/1.1 listener
├── router.h/c        — request dispatch, engine orchestration
│
├── reasoning.h/c     — intent / keyword / inference engine
├── learning.h/c      — text absorption, memory update
├── growth.h/c        — capability snapshot append-log
├── generation.h/c    — response composition
├── memory.h/c        — key-value store (plain text persistence)
│
├── Makefile          — build instructions
└── data/             — runtime state (created on first run)
    ├── memory.txt    — knowledge store: KEY|VALUE|WEIGHT|TIMESTAMP
    └── growth.log    — evolution log: VERSION|TOTAL|RLVL|GQUAL|TS|NOTES
```

---

## 3. Build and Run

### Requirements
- GCC (or Clang) with C99 support
- POSIX-compatible OS (Linux, macOS)

### Build
```bash
cd mrliou
make
```

### Run
```bash
./mrliou-server           # default port 7890
./mrliou-server 8080      # custom port
```

The server creates the `data/` directory on first run.

---

## 4. HTTP API

All endpoints use plain text (`text/plain`) request and response bodies.  
Response format: `KEY: VALUE` lines (one per line).

### `GET /health`
Quick liveness check.
```
STATUS: ok
SERVICE: Mr.liou AI
VERSION: 1.0.0
MEMORY_ENTRIES: 12
GROWTH_VERSION: 3
REQUESTS_HANDLED: 47
```

### `GET /status`
Full system status including memory and growth reports.

### `POST /reason`
Analyse input text.  Body: plain text input.
```
STATUS: ok
MODULE: reasoning
INTENT: question
KEYWORDS: Mr liou AI purpose
INFERENCE: <memory-backed inference>
CONFIDENCE: 0.70
EVIDENCE: mrliou_purpose, C_language
```

### `POST /think`
Full reasoning + generation pipeline.  Body: plain text prompt.

### `POST /learn`
Absorb text into memory.  Body: one or more lines of:
- `key=value` — explicit named fact
- `key: value` — alternate separator
- free text sentence — auto-keyed by first content words
```
STATUS: ok
MODULE: learning
ENTRIES_ADDED: 3
ENTRIES_UPDATED: 1
SUMMARY: absorbed: +3 new, ~1 updated (total memory: 15)
GROWTH_VERSION: 4
REASONING_LEVEL: 0.3150
```

### `GET /grow`
Return the current growth snapshot.

### `POST /generate`
Generate a response.  Body: plain text prompt.

### `GET /memory/query?key=<k>`
Look up a memory entry by key (exact or substring search).

### `POST /memory/query`
Look up a memory entry.  Body: key string.

### `POST /memory/store`
Store a memory entry.  Body: `key=value`.

---

## 5. Data Flow

```
Input text
    │
    ▼
[ Learning Engine ]  ──► memory.txt (plain text)
    │                         │
    ▼                         ▼
[ Reasoning Engine ] ◄── memory_search()
    │   intent / keywords / inference / confidence
    ▼
[ Generation Engine ]
    │   strategy: recall+answer / infer+ask-back / plan+execute / recall+expand
    ▼
[ Growth Engine ]    ──► growth.log (plain text)
    │
    ▼
Response (plain text key=value)
```

### Closed-loop cycle
Every `/learn` call:
1. Absorbs new knowledge into `memory.txt`
2. Records a growth snapshot into `growth.log`
3. Incrementally raises `REASONING_LEVEL` and `GENERATION_QUALITY`

This means **every interaction that teaches the system improves subsequent reasoning and generation quality** — the system grows over time.

---

## 6. Internal Struct Types

Defined in `mrliou_defs.h`:

| Struct | Purpose |
|---|---|
| `MemoryEntry` | One knowledge unit: key, value, weight, timestamp |
| `GrowthSnapshot` | Capability state at a point in time |
| `ReasoningResult` | Output of reasoning analysis |
| `LearningResult` | Summary of what was absorbed |
| `GenerationResult` | Composed output text + strategy |
| `HttpRequest` | Parsed HTTP request |
| `HttpResponse` | HTTP response to send |
| `SystemState` | Runtime counters and levels |

---

## 7. Configuration

All configuration is in `config.h` (native C header — no JSON, no YAML).  
Change values and recompile:

```c
#define MRLIOU_PORT           7890       /* listen port */
#define MRLIOU_MAX_MEMORY     1024       /* max memory entries */
#define MRLIOU_MEMORY_FILE    "./data/memory.txt"
#define MRLIOU_GROWTH_FILE    "./data/growth.log"
#define MRLIOU_PERSIST_ON_WRITE  1       /* flush to disk after every write */
```

---

## 8. Design Principles

1. **C-first** — core logic in C99 with zero external library dependencies
2. **Plain-text state** — no JSON, no database required; files are human-readable and diffable
3. **Closed-loop growth** — every learning cycle updates capability metrics
4. **POSIX sockets** — real TCP listener, not a mock or sandbox
5. **Single-file modules** — each capability (reasoning, memory, learning, growth, generation) is self-contained in its own `.c`/`.h` pair
6. **No placeholders** — all module functions perform real operations

---

## 9. Extending the System

- **Add a new module**: create `mymodule.h` + `mymodule.c`, add a route handler in `router.c`, add the `.o` to `Makefile`
- **Add threading**: replace `server_run()` single-accept loop with `pthread_create` per client
- **Add TLS**: wrap the socket layer with OpenSSL or mbedTLS
- **Add SQLite**: swap `memory.c` plain-text backend for SQLite (same header interface)
- **Add vector search**: extend `memory_search()` with embedding-based similarity
