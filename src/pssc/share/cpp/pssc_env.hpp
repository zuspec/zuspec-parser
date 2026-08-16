// pssc_env.hpp -- the non-memory part of the platform seam. Hand-written once.
//
// `pssc_reg.hpp` covers how the generated code reaches the DEVICE. This covers
// the little it needs from the ENVIRONMENT: today, a way to say something.
// Separate from the memory seam for the same reason as in C -- memory access is
// required by every generated model, and this is optional, so mixing them would
// make the required seam look bigger than it is.
//
// WHAT THE PLATFORM MUST SUPPLY
// -----------------------------
//
//     void pssc::message(const char *fmt, ...);
//
// printf-style. The generated code calls it for `message(...)` in a PSS exec
// body, and (unless `--match-default none`) for an unmatched `match`.
//
// THE PSS `message(verbosity, fmt, ...)` VERBOSITY ARGUMENT IS DROPPED, exactly
// as the SystemVerilog and C projections drop it. PSS verbosity levels are a
// simulation-runtime concept with no counterpart here, and inventing a mapping
// would hand the platform a number it has no basis for interpreting.
//
// IF YOU WANT NONE OF THIS: generate with `--message-style none`, which drops
// the calls and their format strings, so nothing needs implementing.
#ifndef PSSC_ENV_HPP
#define PSSC_ENV_HPP

namespace pssc {

// Implemented by the platform. DECLARED here so that a generated body calling
// it fails to link with this name when it is missing, rather than resolving to
// whatever else is in scope.
void message(const char *fmt, ...);

}  // namespace pssc

// Marks a point the model says cannot be reached (`--match-default
// unreachable`). Deliberately NOT a no-op by default: an unmatched `match` is
// an error in PSS (3.1 §22.7.9), so silence here would convert a stated
// impossibility into a silent fall-through. Override before including the
// generated header if the platform has a fault handler worth calling.
#ifndef PSSC_UNREACHABLE
#  if defined(__GNUC__) || defined(__clang__)
#    define PSSC_UNREACHABLE() __builtin_unreachable()
#  else
#    define PSSC_UNREACHABLE() ((void)0)
#  endif
#endif

#endif  // PSSC_ENV_HPP
