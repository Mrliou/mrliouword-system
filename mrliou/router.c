/* ------------------------------------------------------------------ */
/* Mr.liou AI — router module                                         */
/* Maps HTTP method+path to handler functions and orchestrates the    */
/* five engine modules: reasoning, learning, growth, generation,      */
/* memory.                                                             */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "router.h"
#include "memory.h"
#include "reasoning.h"
#include "learning.h"
#include "growth.h"
#include "generation.h"
#include "config.h"

/* ---- system state tracked by the router -------------------------- */
static SystemState g_state;

/* ---- helpers ----------------------------------------------------- */

static void ok_response(HttpResponse *resp, const char *body)
{
    resp->status_code = 200;
    strncpy(resp->content_type, "text/plain", sizeof(resp->content_type) - 1);
    strncpy(resp->body, body, sizeof(resp->body) - 1);
    resp->body[sizeof(resp->body) - 1] = '\0';
    resp->body_len = (int)strlen(resp->body);
}

static void err_response(HttpResponse *resp, int code, const char *msg)
{
    resp->status_code = code;
    strncpy(resp->content_type, "text/plain", sizeof(resp->content_type) - 1);
    snprintf(resp->body, sizeof(resp->body),
             "STATUS: error\nCODE: %d\nMESSAGE: %s\n", code, msg);
    resp->body_len = (int)strlen(resp->body);
}

/* ---- route handlers ---------------------------------------------- */

/* GET /health */
static void handle_health(const HttpRequest *req, HttpResponse *resp)
{
    (void)req;
    char buf[512];
    snprintf(buf, sizeof(buf),
             "STATUS: ok\n"
             "SERVICE: %s\n"
             "VERSION: %s\n"
             "MEMORY_ENTRIES: %d\n"
             "GROWTH_VERSION: %d\n"
             "REQUESTS_HANDLED: %ld\n",
             MRLIOU_NAME, MRLIOU_VERSION,
             memory_count(), growth_version(),
             g_state.requests_handled);
    ok_response(resp, buf);
}

/* GET /status */
static void handle_status(const HttpRequest *req, HttpResponse *resp)
{
    (void)req;
    char mbuf[512], gbuf[512];
    memory_report(mbuf, sizeof(mbuf));
    growth_report(gbuf, sizeof(gbuf));

    char ts[32];
    struct tm *tm_info = localtime(&g_state.started_at);
    if (tm_info) strftime(ts, sizeof(ts), "%Y-%m-%d %H:%M:%S", tm_info);
    else strncpy(ts, "(unknown)", sizeof(ts) - 1);

    char buf[MRLIOU_BUF_SIZE];
    snprintf(buf, sizeof(buf),
             "STATUS: ok\n"
             "SERVICE: %s v%s\n"
             "DESCRIPTION: %s\n"
             "STARTED_AT: %s\n"
             "REQUESTS_HANDLED: %ld\n\n"
             "%s\n%s",
             MRLIOU_NAME, MRLIOU_VERSION, MRLIOU_DESCRIPTION,
             ts, g_state.requests_handled,
             mbuf, gbuf);
    ok_response(resp, buf);
}

/* POST /reason */
static void handle_reason(const HttpRequest *req, HttpResponse *resp)
{
    if (req->body_len <= 0) {
        err_response(resp, 400, "body required: plain text input");
        return;
    }

    ReasoningResult rr;
    if (reasoning_analyse(req->body, &rr) != 0) {
        err_response(resp, 500, "reasoning engine error");
        return;
    }

    char buf[MRLIOU_BUF_SIZE];
    snprintf(buf, sizeof(buf),
             "STATUS: ok\n"
             "MODULE: reasoning\n"
             "INTENT: %s\n"
             "KEYWORDS: %s\n"
             "INFERENCE: %s\n"
             "CONFIDENCE: %.2f\n"
             "EVIDENCE: %s\n",
             rr.intent, rr.keywords, rr.inference,
             (double)rr.confidence, rr.evidence);
    ok_response(resp, buf);
}

/* POST /think */
static void handle_think(const HttpRequest *req, HttpResponse *resp)
{
    /* Think = reason + generate (full pipeline) */
    if (req->body_len <= 0) {
        err_response(resp, 400, "body required: plain text input");
        return;
    }

    ReasoningResult rr;
    if (reasoning_analyse(req->body, &rr) != 0) {
        err_response(resp, 500, "reasoning engine error");
        return;
    }

    GenerationResult gr;
    if (generation_compose(req->body, &rr, &gr) != 0) {
        err_response(resp, 500, "generation engine error");
        return;
    }

    char buf[MRLIOU_BUF_SIZE];
    snprintf(buf, sizeof(buf),
             "STATUS: ok\n"
             "MODULE: think\n"
             "INTENT: %s\n"
             "KEYWORDS: %s\n"
             "CONFIDENCE: %.2f\n"
             "STRATEGY: %s\n"
             "QUALITY: %.2f\n\n"
             "--- OUTPUT ---\n%s",
             rr.intent, rr.keywords,
             (double)rr.confidence, gr.strategy,
             (double)gr.quality, gr.output);
    ok_response(resp, buf);
}

/* POST /learn */
static void handle_learn(const HttpRequest *req, HttpResponse *resp)
{
    if (req->body_len <= 0) {
        err_response(resp, 400, "body required: text to learn (key=value or free text)");
        return;
    }

    LearningResult lr;
    if (learning_absorb(req->body, &lr) != 0) {
        err_response(resp, 500, "learning engine error");
        return;
    }

    /* update growth after every learning cycle */
    float rl = 0.3f + (memory_count() * 0.001f);
    if (rl > 1.0f) rl = 1.0f;
    float gq = 0.2f + (growth_version() * 0.05f);
    if (gq > 1.0f) gq = 1.0f;
    growth_record(memory_count(), rl, gq, lr.summary);
    g_state.reasoning_level    = rl;
    g_state.generation_quality = gq;

    char buf[MRLIOU_BUF_SIZE];
    snprintf(buf, sizeof(buf),
             "STATUS: ok\n"
             "MODULE: learning\n"
             "ENTRIES_ADDED: %d\n"
             "ENTRIES_UPDATED: %d\n"
             "SUMMARY: %s\n"
             "GROWTH_VERSION: %d\n"
             "REASONING_LEVEL: %.4f\n",
             lr.entries_added, lr.entries_updated, lr.summary,
             growth_version(), (double)rl);
    ok_response(resp, buf);
}

/* GET /grow */
static void handle_grow(const HttpRequest *req, HttpResponse *resp)
{
    (void)req;
    char buf[MRLIOU_BUF_SIZE];
    growth_report(buf, sizeof(buf));
    ok_response(resp, buf);
}

/* POST /generate */
static void handle_generate(const HttpRequest *req, HttpResponse *resp)
{
    if (req->body_len <= 0) {
        err_response(resp, 400, "body required: plain text prompt");
        return;
    }

    ReasoningResult rr;
    reasoning_analyse(req->body, &rr);

    GenerationResult gr;
    if (generation_compose(req->body, &rr, &gr) != 0) {
        err_response(resp, 500, "generation engine error");
        return;
    }

    char buf[MRLIOU_BUF_SIZE];
    snprintf(buf, sizeof(buf),
             "STATUS: ok\n"
             "MODULE: generation\n"
             "STRATEGY: %s\n"
             "QUALITY: %.2f\n\n"
             "--- OUTPUT ---\n%s",
             gr.strategy, (double)gr.quality, gr.output);
    ok_response(resp, buf);
}

/* GET /memory/query?key=<key>  or  POST /memory/query  body: key */
static void handle_memory_query(const HttpRequest *req, HttpResponse *resp)
{
    const char *key = NULL;
    char key_buf[MRLIOU_MAX_KEY];

    /* key from POST body or GET query string */
    if (req->body_len > 0) {
        strncpy(key_buf, req->body, sizeof(key_buf) - 1);
        key_buf[sizeof(key_buf) - 1] = '\0';
        key = key_buf;
    } else {
        /* try ?key= in path */
        const char *qs = strchr(req->path, '?');
        if (qs) {
            const char *kp = strstr(qs, "key=");
            if (kp) {
                kp += 4;
                strncpy(key_buf, kp, sizeof(key_buf) - 1);
                key_buf[sizeof(key_buf) - 1] = '\0';
                key = key_buf;
            }
        }
    }

    if (!key || key[0] == '\0') {
        /* return full memory report */
        char buf[MRLIOU_BUF_SIZE];
        memory_report(buf, sizeof(buf));
        ok_response(resp, buf);
        return;
    }

    MemoryEntry me;
    if (memory_get(key, &me)) {
        char buf[MRLIOU_BUF_SIZE];
        snprintf(buf, sizeof(buf),
                 "STATUS: ok\n"
                 "MODULE: memory\n"
                 "KEY: %s\n"
                 "VALUE: %s\n"
                 "WEIGHT: %.4f\n"
                 "TIMESTAMP: %ld\n",
                 me.key, me.value, (double)me.weight, (long)me.timestamp);
        ok_response(resp, buf);
    } else {
        /* try substring search */
        MemoryEntry hits[8];
        int n = memory_search(key, hits, 8);
        if (n == 0) {
            err_response(resp, 404, "key not found");
            return;
        }
        char buf[MRLIOU_BUF_SIZE];
        int  pos = snprintf(buf, sizeof(buf),
                            "STATUS: ok\nMODULE: memory\nSEARCH: %s\nRESULTS: %d\n\n", key, n);
        for (int i = 0; i < n && pos < (int)sizeof(buf) - 1; i++) {
            pos += snprintf(buf + pos, sizeof(buf) - (size_t)pos,
                            "[%d] KEY=%s VALUE=%s WEIGHT=%.2f\n",
                            i + 1, hits[i].key, hits[i].value, (double)hits[i].weight);
        }
        ok_response(resp, buf);
    }
}

/* POST /memory/store  body: key=value  or  key: value */
static void handle_memory_store(const HttpRequest *req, HttpResponse *resp)
{
    if (req->body_len <= 0) {
        err_response(resp, 400, "body required: key=value");
        return;
    }

    /* re-use learning absorb for storing */
    LearningResult lr;
    learning_absorb(req->body, &lr);

    char buf[512];
    snprintf(buf, sizeof(buf),
             "STATUS: ok\n"
             "MODULE: memory\n"
             "ENTRIES_ADDED: %d\n"
             "ENTRIES_UPDATED: %d\n"
             "TOTAL: %d\n",
             lr.entries_added, lr.entries_updated, memory_count());
    ok_response(resp, buf);
}

/* 404 fallback */
static void handle_not_found(const HttpRequest *req, HttpResponse *resp)
{
    (void)req;
    err_response(resp, 404,
        "route not found.\n"
        "Available routes:\n"
        "  GET  /health\n"
        "  GET  /status\n"
        "  POST /reason\n"
        "  POST /think\n"
        "  POST /learn\n"
        "  GET  /grow\n"
        "  POST /generate\n"
        "  GET  /memory/query[?key=<k>]\n"
        "  POST /memory/query\n"
        "  POST /memory/store\n");
}

/* ---- route table ------------------------------------------------- */
typedef struct { const char *method; const char *path; RouteHandler fn; } RouteEntry;

static const RouteEntry ROUTES[] = {
    { "GET",  "/health",        handle_health        },
    { "GET",  "/status",        handle_status        },
    { "POST", "/reason",        handle_reason        },
    { "POST", "/think",         handle_think         },
    { "POST", "/learn",         handle_learn         },
    { "GET",  "/grow",          handle_grow          },
    { "POST", "/generate",      handle_generate      },
    { "GET",  "/memory/query",  handle_memory_query  },
    { "POST", "/memory/query",  handle_memory_query  },
    { "POST", "/memory/store",  handle_memory_store  },
    { NULL, NULL, NULL }
};

/* ---- public API -------------------------------------------------- */

int router_init(void)
{
    memset(&g_state, 0, sizeof(g_state));
    g_state.started_at = time(NULL);

    memory_init();
    reasoning_init();
    learning_init();
    growth_init();
    generation_init();
    return 0;
}

void router_dispatch(const HttpRequest *req, HttpResponse *resp)
{
    g_state.requests_handled++;

    /* strip query string for route matching */
    char path[256];
    strncpy(path, req->path, sizeof(path) - 1);
    path[sizeof(path) - 1] = '\0';
    char *qs = strchr(path, '?');
    if (qs) *qs = '\0';

    for (int i = 0; ROUTES[i].method; i++) {
        if (strcmp(ROUTES[i].method, req->method) == 0 &&
            strcmp(ROUTES[i].path,   path)         == 0) {
            ROUTES[i].fn(req, resp);
            return;
        }
    }
    handle_not_found(req, resp);
}

void router_shutdown(void)
{
    memory_shutdown();
    reasoning_shutdown();
    learning_shutdown();
    growth_shutdown();
    generation_shutdown();
}
