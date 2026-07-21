/* ------------------------------------------------------------------ */
/* Mr.liou AI — main entry point                                      */
/* Initialises all modules, starts the local HTTP server, and handles */
/* graceful shutdown on SIGINT / SIGTERM.                             */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include "config.h"
#include "mrliou_defs.h"
#include "server.h"
#include "router.h"

/* ---- signal handling --------------------------------------------- */

static int g_listen_fd = -1;

static void on_signal(int sig)
{
    (void)sig;
    const char msg[] = "\n[mrliou] shutting down...\n";
    if (write(STDOUT_FILENO, msg, sizeof(msg) - 1) == -1) { /* nothing to do in signal handler */ }
    server_stop();
    /* closing the listen socket unblocks accept() */
    if (g_listen_fd >= 0) {
        close(g_listen_fd);
        g_listen_fd = -1;
    }
}

/* ---- entry point ------------------------------------------------- */

int main(int argc, char *argv[])
{
    int port = MRLIOU_PORT;

    /* optional: first argument overrides port */
    if (argc >= 2) {
        port = atoi(argv[1]);
        if (port <= 0 || port > 65535) {
            fprintf(stderr, "Invalid port: %s\n", argv[1]);
            return 1;
        }
    }

    /* banner */
    printf("╔══════════════════════════════════════════╗\n");
    printf("║  %s v%s              ║\n", MRLIOU_NAME, MRLIOU_VERSION);
    printf("║  %s  ║\n", MRLIOU_DESCRIPTION);
    printf("╚══════════════════════════════════════════╝\n\n");

    /* initialise modules */
    printf("[mrliou] initialising modules...\n");
    if (router_init() != 0) {
        fprintf(stderr, "[mrliou] failed to initialise modules\n");
        return 1;
    }
    printf("[mrliou] modules ready.\n");

    /* open listen socket */
    g_listen_fd = server_init(port);
    if (g_listen_fd < 0) {
        fprintf(stderr, "[mrliou] failed to bind port %d\n", port);
        router_shutdown();
        return 1;
    }

    /* signal handlers */
    signal(SIGINT,  on_signal);
    signal(SIGTERM, on_signal);

    printf("[mrliou] listening on http://127.0.0.1:%d\n\n", port);
    printf("  GET  http://127.0.0.1:%d/health\n",   port);
    printf("  GET  http://127.0.0.1:%d/status\n",   port);
    printf("  POST http://127.0.0.1:%d/reason\n",   port);
    printf("  POST http://127.0.0.1:%d/think\n",    port);
    printf("  POST http://127.0.0.1:%d/learn\n",    port);
    printf("  GET  http://127.0.0.1:%d/grow\n",     port);
    printf("  POST http://127.0.0.1:%d/generate\n", port);
    printf("  GET  http://127.0.0.1:%d/memory/query\n", port);
    printf("  POST http://127.0.0.1:%d/memory/store\n", port);
    printf("\nPress Ctrl+C to stop.\n\n");

    /* main loop */
    server_run(g_listen_fd, router_dispatch);

    /* shutdown */
    server_shutdown(g_listen_fd);
    router_shutdown();
    printf("[mrliou] stopped.\n");
    return 0;
}
