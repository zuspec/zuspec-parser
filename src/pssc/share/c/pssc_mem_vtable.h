/* pssc_mem_vtable.h -- link style "vtable" (multi-instance / host).
 *
 * The seam is a struct of function pointers plus an opaque user context. The
 * generated component holds a `const pssc_mem_if *` and passes it as the first
 * argument to every primitive, so multiple instances bound to different buses
 * coexist. This is the C analogue of SystemVerilog's pss_mem_if + redirect.
 */
#ifndef PSSC_MEM_VTABLE_H
#define PSSC_MEM_VTABLE_H

/* See pssc_mem.h's selector: this marks the seam as already chosen. */
#define PSSC_MEM_SEAM_CHOSEN 1
#include "pssc_mem.h"

typedef struct pssc_mem_if {
    void     (*write8 )(void *ctx, pssc_addr_t a, uint8_t  d);
    uint8_t  (*read8  )(void *ctx, pssc_addr_t a);
    void     (*write16)(void *ctx, pssc_addr_t a, uint16_t d);
    uint16_t (*read16 )(void *ctx, pssc_addr_t a);
    void     (*write32)(void *ctx, pssc_addr_t a, uint32_t d);
    uint32_t (*read32 )(void *ctx, pssc_addr_t a);
    void     (*write64)(void *ctx, pssc_addr_t a, uint64_t d);
    uint64_t (*read64 )(void *ctx, pssc_addr_t a);
    void     *ctx;                          /* opaque user state */
} pssc_mem_if;

static inline void     pssc_w8 (const pssc_mem_if *b, pssc_addr_t a, uint8_t  d) { b->write8 (b->ctx, a, d); }
static inline uint8_t  pssc_r8 (const pssc_mem_if *b, pssc_addr_t a)             { return b->read8 (b->ctx, a); }
static inline void     pssc_w16(const pssc_mem_if *b, pssc_addr_t a, uint16_t d) { b->write16(b->ctx, a, d); }
static inline uint16_t pssc_r16(const pssc_mem_if *b, pssc_addr_t a)             { return b->read16(b->ctx, a); }
static inline void     pssc_w32(const pssc_mem_if *b, pssc_addr_t a, uint32_t d) { b->write32(b->ctx, a, d); }
static inline uint32_t pssc_r32(const pssc_mem_if *b, pssc_addr_t a)             { return b->read32(b->ctx, a); }
static inline void     pssc_w64(const pssc_mem_if *b, pssc_addr_t a, uint64_t d) { b->write64(b->ctx, a, d); }
static inline uint64_t pssc_r64(const pssc_mem_if *b, pssc_addr_t a)             { return b->read64(b->ctx, a); }

#endif /* PSSC_MEM_VTABLE_H */
