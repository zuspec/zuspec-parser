// pssc_chan.hpp -- the C++ runtime for `sync_pkg::channel_c<T, 1>`. Hand-written once.
//
// The C++ counterpart of share/c/pssc_chan.h, and it implements the same half of
// the type for the same reason: the depth-1, NON-BLOCKING end.
//
//     bool try_put(T)        post unless already full
//     bool try_get(T &out)   take unless empty
//
// WHY NO BLOCKING get()/put(). They are the two operations that need a
// scheduler, and this backend generates none -- see targets/target_cfg.py and
// the HAVE_EVENT_WAIT contract. A caller here cannot suspend until another
// party posts, because there is no other party to run while it is suspended.
// The generator refuses a model that calls them rather than lowering them to
// something that looks like a wait and is not.
//
// WHY THIS MATTERS EVEN WITHOUT WAITING. `channel_c` is not only a wait
// primitive. PSS 3.1 has no mutable component attribute (§9.1.6), so a depth-1
// channel is the only way to spell "a latch" at all -- which is what the WB DMA
// model's `inflight` guard is, and it never blocks. A polling profile gets the
// guard; it does not get the suspend.
//
// WHY DEPTH 1 ONLY. Depth 1 is a coalescing binary semaphore: one value and one
// flag, no cursor, no wrap, no capacity. A deeper channel is a ring buffer, and
// the generator rejects `DEPTH > 1` by name rather than shipping one no test
// exercises.
//
// TYPED, unlike the C runtime. C had one channel struct and a `uint64_t`
// payload, so a generated body had to widen the model's own local to match; a
// template carries the model's declared element type through instead, and a
// mismatch between a channel and the local it is drained into becomes a
// compile error rather than a widening.
//
// NOT THREAD-SAFE, deliberately -- same position as the C runtime.
// `try_put`/`try_get` are read-modify-write on a plain object, and every caller
// in a generated model is the single foreground thread. A platform that adds an
// interrupt handler posting to a channel must supply its own critical section:
// define PSSC_CHAN_ENTER/PSSC_CHAN_EXIT before including a generated header.
#ifndef PSSC_CHAN_HPP
#define PSSC_CHAN_HPP

#ifndef PSSC_CHAN_ENTER
#  define PSSC_CHAN_ENTER() ((void)0)
#endif
#ifndef PSSC_CHAN_EXIT
#  define PSSC_CHAN_EXIT()  ((void)0)
#endif

namespace pssc {

template <class T>
class chan1 {
    T    v_{};          // the held value; meaningful only while full_
    bool full_ = false;
public:
    // Post unless already full. `false` is the COALESCING behaviour the model
    // relies on and not a failure: a second notification arriving before the
    // first is consumed leaves one token, not two.
    bool try_put(T v) {
        PSSC_CHAN_ENTER();
        const bool ok = !full_;
        if (ok) {
            v_ = v;
            full_ = true;
        }
        PSSC_CHAN_EXIT();
        return ok;
    }

    // Take unless empty. `out` is left UNTOUCHED when the channel is empty, so
    // a caller that ignores the result reads its own prior value rather than an
    // invented one. PSS says nothing about the output on failure; leaving it
    // alone is the only choice that cannot manufacture a completion.
    bool try_get(T &out) {
        PSSC_CHAN_ENTER();
        const bool ok = full_;
        if (ok) {
            out = v_;
            full_ = false;
        }
        PSSC_CHAN_EXIT();
        return ok;
    }

    bool empty() const { return !full_; }
};

}  // namespace pssc

#endif  // PSSC_CHAN_HPP
