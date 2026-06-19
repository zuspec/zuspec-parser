/*
 * zsp_bridge.c -- pssc C scenario <-> SystemVerilog DPI bridge runtime.
 * See zsp_bridge.h. Model-independent; the spawn switch is generated separately
 * (pssc_bridge_dispatch).
 */
#include <stdlib.h>
#include "zsp_bridge.h"

/* Verilator/DPI scope handoff. The C scenario re-enters SV (calling an exported
 * import) while it runs; Verilator requires the SV scope to be set first (IEEE
 * 1800 35.5.3). zsp_bridge_capture_scope (a `context` DPI import) grabs the
 * caller's scope; zsp_bridge_run restores it before running coroutines. The
 * symbols are weak so a non-DPI host (a plain C harness) still links -- there
 * they are absent, g_sv_scope stays NULL, and the set is skipped. */
extern void *svGetScope(void) __attribute__((weak));
extern int   svSetScope(void *scope) __attribute__((weak));
static void *g_sv_scope;

void zsp_bridge_capture_scope(void) {
    if (svGetScope) {
        g_sv_scope = svGetScope();
    }
}

/* The single active bridge -- a generated import sub-task posts to it without
 * threading a handle through the coroutine ABI (one scenario instance). */
static zsp_bridge_t *g_bridge;

zsp_bridge_t *zsp_bridge_create(void) {
    zsp_bridge_t *b = (zsp_bridge_t *)malloc(sizeof(zsp_bridge_t));
    if (!b) {
        return NULL;
    }
    zsp_alloc_malloc_init(&b->alloc);
    zsp_timebase_init(&b->tb, &b->alloc, ZSP_TIME_PS);
    b->ctxt.alloc = &b->alloc;
    b->ctxt.timebase = &b->tb;
    b->status = 0;
    b->pending_head = b->pending_tail = b->active_head = NULL;
    b->next_req_id = 0;
    g_bridge = b;
    return b;
}

void zsp_bridge_destroy(zsp_bridge_t *b) {
    if (b) {
        free(b);
    }
}

void zsp_bridge_spawn(zsp_bridge_t *b, int action_id, long long seed) {
    pssc_bridge_dispatch(b, action_id, seed);
}

void zsp_bridge_run(zsp_bridge_t *b) {
    if (g_sv_scope && svSetScope) {
        svSetScope(g_sv_scope);   /* re-arm the SV scope for any C->SV import */
    }
    while (zsp_timebase_run(&b->tb)) {
        /* run the ready queue to quiescence */
    }
}

int zsp_bridge_done(zsp_bridge_t *b) {
    if (zsp_timebase_has_pending(&b->tb)) {
        return 0;
    }
    /* Outstanding import requests (posted or in-flight) mean not done. */
    return (b->pending_head == NULL && b->active_head == NULL) ? 1 : 0;
}

/* --- blocking-import mailbox ------------------------------------------------ */

void zsp_bridge_post_request(struct zsp_thread_s *thread, zsp_bridge_req_t *req) {
    zsp_bridge_t *b = g_bridge;
    req->thread = thread;
    req->req_id = ++b->next_req_id;
    req->next = NULL;
    thread->flags |= ZSP_THREAD_FLAGS_BLOCKED;   /* suspend until completed */
    if (b->pending_tail) {
        b->pending_tail->next = req;
    } else {
        b->pending_head = req;
    }
    b->pending_tail = req;
}

int zsp_bridge_next_request(zsp_bridge_t *b, int *req_id, int *fn_id, void **args) {
    zsp_bridge_req_t *req = b->pending_head;
    if (!req) {
        return 0;
    }
    b->pending_head = req->next;
    if (!b->pending_head) {
        b->pending_tail = NULL;
    }
    /* move to the active list until completed */
    req->next = b->active_head;
    b->active_head = req;
    if (req_id) *req_id = req->req_id;
    if (fn_id)  *fn_id = req->fn_id;
    if (args)   *args = (void *)req;
    return 1;
}

void zsp_bridge_complete(zsp_bridge_t *b, int req_id, long long ret) {
    zsp_bridge_req_t **pp = &b->active_head;
    while (*pp && (*pp)->req_id != req_id) {
        pp = &(*pp)->next;
    }
    zsp_bridge_req_t *req = *pp;
    if (!req) {
        return;
    }
    *pp = req->next;                     /* unlink from active */
    zsp_thread_t *thread = req->thread;
    thread->rval = (uintptr_t)ret;       /* import return value */
    thread->flags &= ~ZSP_THREAD_FLAGS_BLOCKED;
    zsp_timebase_schedule(&b->tb, thread);   /* re-wake the coroutine */
}

long long zsp_bridge_arg_i(void *args, int idx) {
    zsp_bridge_req_t *req = (zsp_bridge_req_t *)args;
    if (!req || idx < 0 || idx >= req->argc) {
        return 0;
    }
    return req->argv[idx];
}
