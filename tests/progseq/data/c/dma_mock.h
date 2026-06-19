/* dma_mock.h -- a DMA-aware mock "hardware" model shared by the C testbenches.
 *
 * Models just enough of the WB DMA core for the self-check: a register space, a
 * small byte-addressable system memory, and a channel that completes (sets DONE)
 * when CH_EN is written -- moving TOT_SZ words from A0 to A1. A poison source
 * address forces the error path (sets ERR). This is the C port of the SV
 * tb_pkg::dma_mock_bus_c in wb_dma_sv_proto.sv.
 */
#ifndef DMA_MOCK_H
#define DMA_MOCK_H

#include <stdint.h>

#define DMA_REGWORDS    256        /* register space: base .. base+0x400 */
#define DMA_SYSCAP      1024       /* sparse system-memory byte capacity */
#define DMA_POISON_SRC  0xdead0000u

typedef struct {
    uint64_t base;
    uint32_t regmem[DMA_REGWORDS];
    struct { uint32_t addr; uint8_t val; uint8_t used; } sys[DMA_SYSCAP];
} dma_mock_t;

void     dma_mock_init(dma_mock_t *m, uint64_t base);
uint8_t  dma_mock_sys_get(dma_mock_t *m, uint32_t addr);
void     dma_mock_sys_set(dma_mock_t *m, uint32_t addr, uint8_t v);
uint32_t dma_mock_reg_get(dma_mock_t *m, uint64_t addr);   /* absolute-addr word read */

/* reg_access primitives operating on a mock instance. */
void     dma_mock_write8 (dma_mock_t *m, uint64_t a, uint8_t  d);
uint8_t  dma_mock_read8  (dma_mock_t *m, uint64_t a);
void     dma_mock_write16(dma_mock_t *m, uint64_t a, uint16_t d);
uint16_t dma_mock_read16 (dma_mock_t *m, uint64_t a);
void     dma_mock_write32(dma_mock_t *m, uint64_t a, uint32_t d);
uint32_t dma_mock_read32 (dma_mock_t *m, uint64_t a);
void     dma_mock_write64(dma_mock_t *m, uint64_t a, uint64_t d);
uint64_t dma_mock_read64 (dma_mock_t *m, uint64_t a);

#endif /* DMA_MOCK_H */
