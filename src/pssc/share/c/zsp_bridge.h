/*
 * zsp_bridge.h -- pssc C scenario <-> SystemVerilog DPI bridge runtime.
 *
 * Model-independent runtime that owns one zsp_timebase and drives a generated
 * scenario by integer action id. The host (a SV trampoline over DPI, or a C
 * harness) calls create -> spawn(action_id, seed) -> run -> done.
 *
 * `pssc_bridge_dispatch` is generated per model (the ACTION_* spawn switch);
 * it instantiates the selected action's root coroutine and posts it onto the
 * bridge timebase. This header stays free of any model specifics.
 *
 * Companion design: design/pssc-c-bridge-runtime-design.md (Phase C1).
 */
#ifndef INCLUDED_ZSP_BRIDGE_H
#define INCLUDED_ZSP_BRIDGE_H

#include "zsp_alloc.h"
#include "zsp_init_ctxt.h"
#include "zsp_timebase.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct zsp_bridge_s {
    zsp_alloc_t      alloc;   /* malloc-backed allocator                       */
    zsp_timebase_t   tb;      /* ready-queue executor (untimed scenario)       */
    zsp_init_ctxt_t  ctxt;    /* {alloc, timebase} handed to <Action>_init     */
    long long        status;  /* last spawned action's status/result (reserved) */
} zsp_bridge_t;

/* Generated per model: spawn the root coroutine selected by `action_id`,
 * after seeding any runtime solve. Defined in the generated dispatcher TU. */
void pssc_bridge_dispatch(zsp_bridge_t *b, int action_id, long long seed);

/* Lifecycle */
zsp_bridge_t *zsp_bridge_create(void);
void          zsp_bridge_destroy(zsp_bridge_t *b);

/* SV -> C: drive the scenario */
void zsp_bridge_spawn(zsp_bridge_t *b, int action_id, long long seed);
void zsp_bridge_run(zsp_bridge_t *b);   /* run the ready queue to quiescence  */
int  zsp_bridge_done(zsp_bridge_t *b);  /* 1 when no pending work remains       */

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_ZSP_BRIDGE_H */
