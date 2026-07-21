#ifndef MRLIOU_ROUTER_H
#define MRLIOU_ROUTER_H

#include "mrliou_defs.h"

/* ------------------------------------------------------------------ */
/* Router module — maps HTTP method + path to handler functions       */
/* ------------------------------------------------------------------ */

/* Register all built-in routes and initialise all engine modules.
   Must be called once before router_dispatch.  Returns 0 on success. */
int router_init(void);

/* Dispatch an incoming request to the appropriate handler.
   Fills *resp with the result. */
void router_dispatch(const HttpRequest *req, HttpResponse *resp);

/* Tear down all engine modules. */
void router_shutdown(void);

#endif /* MRLIOU_ROUTER_H */
