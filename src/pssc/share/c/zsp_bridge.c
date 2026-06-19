/*
 * zsp_bridge.c -- pssc C scenario <-> SystemVerilog DPI bridge runtime.
 * See zsp_bridge.h. Model-independent; the spawn switch is generated separately
 * (pssc_bridge_dispatch).
 */
#include <stdlib.h>
#include "zsp_bridge.h"

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
    while (zsp_timebase_run(&b->tb)) {
        /* run the ready queue to quiescence */
    }
}

int zsp_bridge_done(zsp_bridge_t *b) {
    return zsp_timebase_has_pending(&b->tb) ? 0 : 1;
}
