/* pssc_mem_direct.h -- COMPATIBILITY SHIM. Use pssc_mem_fn.h.
 *
 * This file's contents moved to `pssc_mem_fn.h` in C4.3. The old name described
 * a deployment ("direct / single DUT"); the new one describes the mechanism
 * (calls extern functions linked by name), which is what actually distinguishes
 * it from the other seams.
 *
 * Kept because generated headers in the wild `#include "pssc_mem_direct.h"` by
 * name. `--link-style direct` still works and still emits this include.
 *
 * Nothing new should include this file.
 */
#ifndef PSSC_MEM_DIRECT_H
#define PSSC_MEM_DIRECT_H

#include "pssc_mem_fn.h"

#endif /* PSSC_MEM_DIRECT_H */
