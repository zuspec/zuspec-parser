/* pssc_mem_mmio.h -- COMPATIBILITY SHIM. Use pssc_mem_ptr.h.
 *
 * This file's contents moved to `pssc_mem_ptr.h` in C4.3. The old name said
 * what the seam was FOR ("memory-mapped I/O"); the new one says what it DOES
 * (forms a pointer from the address and dereferences it), which is the property
 * that decides whether it is usable -- see the width assertion in pssc_mem.h.
 *
 * Kept because generated headers in the wild `#include "pssc_mem_mmio.h"` by
 * name, and a rename that breaks them buys nothing. `--link-style mmio` still
 * works and still emits this include.
 *
 * Nothing new should include this file.
 */
#ifndef PSSC_MEM_MMIO_H
#define PSSC_MEM_MMIO_H

#include "pssc_mem_ptr.h"

#endif /* PSSC_MEM_MMIO_H */
