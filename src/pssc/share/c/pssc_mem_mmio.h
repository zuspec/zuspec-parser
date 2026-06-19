/* pssc_mem_mmio.h -- link style "mmio" (bare-metal memory-mapped access).
 *
 * When addr_handle_t is a real CPU address, the seam is just a `volatile`
 * load/store -- no user code, no function pointer, no call. As `static inline`
 * each primitive compiles to a single load/store instruction. There is no
 * import API to implement, so the generated <prefix>_create takes only the base.
 *
 * Caveat: the address space must be directly CPU-addressable, and there is no
 * hook for logging, backdoor, or a simulated bus -- use vtable/direct for that.
 */
#ifndef PSSC_MEM_MMIO_H
#define PSSC_MEM_MMIO_H

#include "pssc_mem.h"

static inline void     pssc_w8 (const void *s, pssc_addr_t a, uint8_t  d) { (void)s; *(volatile uint8_t  *)(uintptr_t)a = d; }
static inline uint8_t  pssc_r8 (const void *s, pssc_addr_t a)             { (void)s; return *(volatile uint8_t  *)(uintptr_t)a; }
static inline void     pssc_w16(const void *s, pssc_addr_t a, uint16_t d) { (void)s; *(volatile uint16_t *)(uintptr_t)a = d; }
static inline uint16_t pssc_r16(const void *s, pssc_addr_t a)             { (void)s; return *(volatile uint16_t *)(uintptr_t)a; }
static inline void     pssc_w32(const void *s, pssc_addr_t a, uint32_t d) { (void)s; *(volatile uint32_t *)(uintptr_t)a = d; }
static inline uint32_t pssc_r32(const void *s, pssc_addr_t a)             { (void)s; return *(volatile uint32_t *)(uintptr_t)a; }
static inline void     pssc_w64(const void *s, pssc_addr_t a, uint64_t d) { (void)s; *(volatile uint64_t *)(uintptr_t)a = d; }
static inline uint64_t pssc_r64(const void *s, pssc_addr_t a)             { (void)s; return *(volatile uint64_t *)(uintptr_t)a; }

#endif /* PSSC_MEM_MMIO_H */
