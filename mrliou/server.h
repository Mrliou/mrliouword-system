#ifndef MRLIOU_SERVER_H
#define MRLIOU_SERVER_H

#include "mrliou_defs.h"

/* ------------------------------------------------------------------ */
/* Server module — POSIX TCP socket HTTP/1.1 listener                 */
/* Single-threaded; processes one request at a time.                  */
/* ------------------------------------------------------------------ */

/* Initialise the server socket.  Returns socket fd on success, -1. */
int server_init(int port);

/* Run the accept-and-serve loop.  Blocks until server_stop() is
   called from a signal handler.  Takes the router dispatch function
   as its second argument. */
typedef void (*DispatchFn)(const HttpRequest *, HttpResponse *);
void server_run(int listen_fd, DispatchFn dispatch);

/* Signal the server loop to exit (safe to call from SIGINT handler). */
void server_stop(void);

/* Close the listen socket and free resources. */
void server_shutdown(int listen_fd);

/* Write a response struct to the connected client socket fd.
   Returns bytes sent or -1 on error. */
int server_send_response(int client_fd, const HttpResponse *resp);

/* Parse raw HTTP request bytes into an HttpRequest struct.
   Returns 0 on success, -1 on parse failure. */
int server_parse_request(const char *raw, int raw_len, HttpRequest *req);

#endif /* MRLIOU_SERVER_H */
