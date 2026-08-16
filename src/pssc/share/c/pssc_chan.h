/* pssc_chan.h -- the C runtime for `sync_pkg::channel_c<T, 1>`. Hand-written once.
 *
 * A PSS channel is a bounded buffer with blocking and non-blocking ends. This
 * header implements ONLY the depth-1, non-blocking end:
 *
 *     bool try_put(T)       post unless already full
 *     bool try_get(T *)     take unless empty
 *
 * and that restriction is the whole design, not a first cut.
 *
 * WHY NO BLOCKING get()/put(). They are the two operations that need a
 * scheduler, and this target has none -- see target_cfg.py and the
 * HAVE_EVENT_WAIT contract. A caller here cannot suspend until another party
 * posts, because there is no other party to run while it is suspended. The
 * generator REJECTS a model that calls them (lower_progseq._reject_blocking_chan)
 * rather than lowering them to something that looks like a wait and is not; a
 * `get()` that silently returned garbage on an empty channel would be a driver
 * that reports a completion nobody signalled.
 *
 * WHY THIS COSTS THE POLLING PROFILE NOTHING. `channel_c` is not only a wait
 * primitive. The WB DMA model's `inflight` guard uses try_get/try_put and never
 * blocks: PSS 3.1 has no mutable component attribute (§9.1.6), so a depth-1
 * channel is the only way to spell "a latch" at all. That is why the member is
 * ungated in the PSS while `wake.get()` is gated -- see
 * src/pss/wb_dma_ch_c.pss. A firmware target gets the guard; it does not get
 * the suspend.
 *
 * WHY DEPTH 1 ONLY. Depth 1 is a coalescing binary semaphore, which is a
 * `uint8_t` and a value -- no cursor, no wrap, no capacity field. A deeper
 * channel is a ring buffer, and a ring buffer whose size is a generated
 * constant is a different type per instance. Nothing in scope declares one, so
 * the generator rejects `DEPTH > 1` by name rather than shipping a ring buffer
 * that no test exercises.
 *
 * WHY THE PAYLOAD IS `uint64_t`. PSS channel element types reachable here are
 * integral (`bit`, `int`, an enum); the widest is 64 bits, and one payload type
 * means one channel type, so a component holding two channels of different
 * element types is still two plain members. The generator rejects a
 * struct-valued element type. Callers never see the payload width: the
 * generated body assigns through the model's own declared local.
 *
 * NOT THREAD-SAFE, deliberately. `try_put`/`try_get` are read-modify-write on a
 * plain object. Every caller in a generated model is the single foreground
 * thread; an interrupt handler posting to `wake` is the one case that is NOT,
 * and it is exactly the case that does not exist on this profile (notify_irq
 * is gated on HAVE_EVENT_WAIT). A platform that adds one must supply its own
 * critical section -- override PSSC_CHAN_ENTER/PSSC_CHAN_EXIT below.
 */
#ifndef PSSC_CHAN_H
#define PSSC_CHAN_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Mutual exclusion around the read-modify-write pair. No-ops by default --
 * see the thread-safety note above. Define both before including a generated
 * header to make the channels interrupt-safe. */
#ifndef PSSC_CHAN_ENTER
#  define PSSC_CHAN_ENTER() ((void)0)
#endif
#ifndef PSSC_CHAN_EXIT
#  define PSSC_CHAN_EXIT()  ((void)0)
#endif

typedef struct pssc_chan1_s {
    uint64_t v;        /* the held value; meaningful only while `full` */
    uint8_t  full;     /* 0 = empty, 1 = holds one element */
} pssc_chan1_t;

static inline void pssc_chan1_init(pssc_chan1_t *c) {
    c->v = 0;
    c->full = 0;
}

/* Post unless already full. Returns false when the channel is full -- which is
 * the COALESCING behaviour the model relies on, not a failure: a second
 * interrupt arriving before the first is consumed leaves one token, not two. */
static inline bool pssc_chan1_try_put(pssc_chan1_t *c, uint64_t v) {
    bool ok;
    PSSC_CHAN_ENTER();
    ok = (c->full == 0);
    if (ok) {
        c->v = v;
        c->full = 1;
    }
    PSSC_CHAN_EXIT();
    return ok;
}

/* Take unless empty. `*v` is left UNTOUCHED when the channel is empty, so a
 * caller that ignores the return value reads its own prior value rather than
 * an invented one. PSS says nothing about the output on failure; leaving it
 * alone is the only choice that cannot manufacture a completion. */
static inline bool pssc_chan1_try_get(pssc_chan1_t *c, uint64_t *v) {
    bool ok;
    PSSC_CHAN_ENTER();
    ok = (c->full != 0);
    if (ok) {
        *v = c->v;
        c->full = 0;
    }
    PSSC_CHAN_EXIT();
    return ok;
}

#ifdef __cplusplus
}
#endif

#endif /* PSSC_CHAN_H */
