/* ------------------------------------------------------------------ */
/* Mr.liou AI — server module                                         */
/* POSIX TCP socket HTTP/1.1 single-threaded server.                  */
/* ------------------------------------------------------------------ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include "server.h"
#include "config.h"

static volatile int g_running = 1;

/* ---- socket helpers ---------------------------------------------- */

int server_init(int port)
{
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(fd);
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family      = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port        = htons((uint16_t)port);

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, MRLIOU_BACKLOG) < 0) {
        perror("listen");
        close(fd);
        return -1;
    }

    return fd;
}

void server_stop(void)
{
    g_running = 0;
}

void server_shutdown(int listen_fd)
{
    if (listen_fd >= 0) close(listen_fd);
}

/* ---- HTTP request parser ----------------------------------------- */

int server_parse_request(const char *raw, int raw_len, HttpRequest *req)
{
    if (!raw || raw_len <= 0 || !req) return -1;
    memset(req, 0, sizeof(*req));

    const char *p   = raw;
    const char *end = raw + raw_len;

    /* --- request line: METHOD SP path SP HTTP/x.x CRLF --- */
    const char *sp1 = memchr(p, ' ', (size_t)(end - p));
    if (!sp1) return -1;

    int mlen = (int)(sp1 - p);
    if (mlen <= 0 || mlen >= (int)sizeof(req->method)) return -1;
    memcpy(req->method, p, (size_t)mlen);
    req->method[mlen] = '\0';

    p = sp1 + 1;
    const char *sp2 = memchr(p, ' ', (size_t)(end - p));
    if (!sp2) return -1;

    int plen = (int)(sp2 - p);
    if (plen <= 0 || plen >= (int)sizeof(req->path)) return -1;
    memcpy(req->path, p, (size_t)plen);
    req->path[plen] = '\0';

    /* advance past the rest of request line */
    const char *crlf = strstr(sp2, "\r\n");
    if (!crlf) return -1;
    p = crlf + 2;

    /* --- parse headers until blank line --- */
    int content_length = 0;
    while (p < end) {
        const char *hdr_end = strstr(p, "\r\n");
        if (!hdr_end) break;
        if (hdr_end == p) { p += 2; break; } /* blank line = end of headers */

        /* look for Content-Length */
        if (strncasecmp(p, "Content-Length:", 15) == 0) {
            const char *vp = p + 15;
            while (*vp == ' ') vp++;
            content_length = atoi(vp);
        }
        p = hdr_end + 2;
    }

    /* --- body --- */
    int remaining = (int)(end - p);
    if (content_length > 0 && remaining > 0) {
        int blen = content_length < remaining ? content_length : remaining;
        if (blen >= MRLIOU_BUF_SIZE) blen = MRLIOU_BUF_SIZE - 1;
        memcpy(req->body, p, (size_t)blen);
        req->body[blen] = '\0';
        req->body_len   = blen;
    }

    return 0;
}

/* ---- HTTP response writer ---------------------------------------- */

int server_send_response(int client_fd, const HttpResponse *resp)
{
    if (client_fd < 0 || !resp) return -1;

    const char *ct = resp->content_type[0] ? resp->content_type : "text/plain";
    char header[512];
    int  hlen = snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: %s; charset=utf-8\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n",
        resp->status_code,
        resp->status_code == 200 ? "OK" :
        resp->status_code == 400 ? "Bad Request" :
        resp->status_code == 404 ? "Not Found"   : "Internal Server Error",
        ct,
        resp->body_len > 0 ? resp->body_len : (int)strlen(resp->body));

    int sent = (int)write(client_fd, header, (size_t)hlen);
    if (sent < 0) return -1;

    int blen = resp->body_len > 0 ? resp->body_len : (int)strlen(resp->body);
    if (blen > 0) {
        int bsent = (int)write(client_fd, resp->body, (size_t)blen);
        if (bsent < 0) return -1;
        sent += bsent;
    }
    return sent;
}

/* ---- accept loop ------------------------------------------------- */

void server_run(int listen_fd, DispatchFn dispatch)
{
    char buf[MRLIOU_BUF_SIZE];

    while (g_running) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        int client_fd = accept(listen_fd,
                               (struct sockaddr *)&client_addr,
                               &client_len);
        if (client_fd < 0) {
            if (g_running) perror("accept");
            continue;
        }

        /* read request */
        int n = (int)read(client_fd, buf, sizeof(buf) - 1);
        if (n <= 0) { close(client_fd); continue; }
        buf[n] = '\0';

        HttpRequest  req;
        HttpResponse resp;
        memset(&resp, 0, sizeof(resp));

        if (server_parse_request(buf, n, &req) != 0) {
            resp.status_code = 400;
            strncpy(resp.body, "STATUS: error\nMESSAGE: bad request\n",
                    sizeof(resp.body) - 1);
        } else {
            dispatch(&req, &resp);
        }

        server_send_response(client_fd, &resp);
        close(client_fd);
    }
}
