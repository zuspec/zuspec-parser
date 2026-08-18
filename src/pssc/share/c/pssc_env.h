/* pssc_env.h -- the non-memory part of the platform seam. Hand-written once.
 *
 * `pssc_mem.h` covers how the generated code reaches the DEVICE. This covers
 * the little it needs from the ENVIRONMENT: today, a way to say something.
 *
 * WHY THIS IS SEPARATE FROM pssc_mem.h. Memory access is required by every
 * generated model and is the thing the link style varies. What is here is
 * optional, is not performance-critical, and is what a firmware integrator is
 * most likely to want to redirect at a real logging facility. Mixing the two
 * would make the required seam look bigger than it is.
 *
 * WHAT THE PLATFORM MUST SUPPLY
 * -----------------------------
 *
 *   void pssc_message(const char *fmt, ...);
 *
 * printf-style. The generated code calls it for `message(...)` in a PSS exec
 * body, and (unless `--match-default none`) for an unmatched `match`.
 *
 * The PSS `message(verbosity, fmt, ...)` VERBOSITY ARGUMENT IS DROPPED, exactly
 * as the SystemVerilog projection drops it. PSS verbosity levels are a
 * simulation-runtime concept with no counterpart here, and inventing a mapping
 * would give the platform a number it has no basis for interpreting. Filter by
 * content, or generate with `--message-style none` and pay nothing.
 *
 * IF YOU WANT NONE OF THIS: generate with `--message-style none`. That drops
 * the calls AND their format strings, so nothing needs to be implemented and
 * no `.rodata` is spent -- which on a part with kilobytes of it is the point.
 *
 * A weak empty definition can be emitted with `--emit-stubs`, so a link
 * succeeds before the platform side exists. Note that no memory primitive is
 * ever stubbed: a silently-succeeding bus access would be a driver that
 * reports the device is fine because it never talked to it.
 */
#ifndef PSSC_ENV_H
#define PSSC_ENV_H

#ifdef __cplusplus
extern "C" {
#endif

/* Implemented by the platform. Declared here so a generated body that calls it
 * is a compile error when it is missing, rather than an implicit declaration
 * that links to whatever `pssc_message` happens to be in scope. */
void pssc_message(const char *fmt, ...);

/* Marks a point the model says cannot be reached (`--match-default
 * unreachable`). Deliberately NOT a no-op by default: an unmatched `match` is
 * an error in PSS (3.1 §22.7.9), so silence here would convert a stated
 * impossibility into a silent fall-through. Override before including the
 * generated header if the platform has a fault handler worth calling. */
#ifndef PSSC_UNREACHABLE
#  if defined(__GNUC__) || defined(__clang__)
#    define PSSC_UNREACHABLE() __builtin_unreachable()
#  else
#    define PSSC_UNREACHABLE() ((void)0)
#  endif
#endif

/* On a definition that may legitimately have no caller in its translation
 * unit. The generated register accessors are the case: the set is derived from
 * the register map, so it covers registers no operation in this model happens
 * to touch, and when they live in the .c (the default layout) that is a
 * translation-unit-local `static inline` nobody calls -- which clang reports
 * under -Wunused-function. The accessors are the API's vocabulary for the
 * device, not a list of what today's operations use, so pruning them to the
 * called set would make a model edit silently remove a symbol. */
#ifndef PSSC_MAYBE_UNUSED
#  if defined(__GNUC__) || defined(__clang__)
#    define PSSC_MAYBE_UNUSED __attribute__((unused))
#  else
#    define PSSC_MAYBE_UNUSED
#  endif
#endif

#ifdef __cplusplus
}
#endif

#endif /* PSSC_ENV_H */
