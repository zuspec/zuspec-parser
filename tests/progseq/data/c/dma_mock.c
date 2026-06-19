/* dma_mock.c -- implementation of the shared DMA mock hardware model. */
#include "dma_mock.h"

void dma_mock_init(dma_mock_t *m, uint64_t base) {
    m->base = base;
    for (int i = 0; i < DMA_REGWORDS; i++) m->regmem[i] = 0;
    for (int i = 0; i < DMA_SYSCAP; i++) { m->sys[i].used = 0; m->sys[i].addr = 0; m->sys[i].val = 0; }
}

uint8_t dma_mock_sys_get(dma_mock_t *m, uint32_t addr) {
    for (int i = 0; i < DMA_SYSCAP; i++)
        if (m->sys[i].used && m->sys[i].addr == addr) return m->sys[i].val;
    return 0;
}

void dma_mock_sys_set(dma_mock_t *m, uint32_t addr, uint8_t v) {
    int free_slot = -1;
    for (int i = 0; i < DMA_SYSCAP; i++) {
        if (m->sys[i].used && m->sys[i].addr == addr) { m->sys[i].val = v; return; }
        if (!m->sys[i].used && free_slot < 0) free_slot = i;
    }
    if (free_slot >= 0) { m->sys[free_slot].used = 1; m->sys[free_slot].addr = addr; m->sys[free_slot].val = v; }
}

static uint32_t *regslot(dma_mock_t *m, uint64_t addr) {
    uint64_t off = addr - m->base;
    uint64_t idx = off / 4;
    if (off >= (uint64_t)DMA_REGWORDS * 4) return 0;   /* out of modeled range */
    return &m->regmem[idx];
}

uint32_t dma_mock_reg_get(dma_mock_t *m, uint64_t addr) {
    uint32_t *p = regslot(m, addr);
    return p ? *p : 0;
}

/* CSR sits at offset 0 of each 0x20-byte channel block; channels start at
 * base+0x20. Returns 1 and the channel index for a channel-CSR address. */
static int decode_csr(dma_mock_t *m, uint64_t a, int *ch) {
    uint64_t rel;
    if (a < (m->base + 0x20u)) return 0;
    rel = a - (m->base + 0x20u);
    if (rel >= (31u * 0x20u)) return 0;
    if ((rel % 0x20u) != 0) return 0;
    *ch = (int)(rel / 0x20u);
    return 1;
}

static void run_transfer(dma_mock_t *m, int ch, uint64_t csr_addr, uint32_t csr_data) {
    uint64_t chbase = m->base + 0x20u + (uint64_t)ch * 0x20u;
    uint32_t a0 = dma_mock_reg_get(m, chbase + 0x08u);
    uint32_t a1 = dma_mock_reg_get(m, chbase + 0x10u);
    uint32_t sz = dma_mock_reg_get(m, chbase + 0x04u);
    int nbytes = (int)(sz & 0xfffu) * 4;     /* TOT_SZ words -> bytes */
    uint32_t *p = regslot(m, csr_addr);
    if (!p) return;
    if (a0 == DMA_POISON_SRC) {
        *p = (csr_data & ~0x00000401u) | 0x00001000u;   /* clear CH_EN/BUSY, set ERR */
        return;
    }
    for (int i = 0; i < nbytes; i++)
        dma_mock_sys_set(m, a1 + i, dma_mock_sys_get(m, a0 + i));
    *p = (csr_data & ~0x00000401u) | 0x00000800u;        /* clear CH_EN/BUSY, set DONE */
}

static void maybe_run(dma_mock_t *m, uint64_t addr, uint32_t data) {
    int ch;
    if (decode_csr(m, addr, &ch) && (data & 0x1u) /* CH_EN */)
        run_transfer(m, ch, addr, data);
}

void dma_mock_write32(dma_mock_t *m, uint64_t a, uint32_t d) {
    uint32_t *p = regslot(m, a);
    if (p) *p = d;
    maybe_run(m, a, d);
}
uint32_t dma_mock_read32(dma_mock_t *m, uint64_t a) { return dma_mock_reg_get(m, a); }

void dma_mock_write8(dma_mock_t *m, uint64_t a, uint8_t d) {
    uint64_t wa = a & ~(uint64_t)0x3; uint32_t *p = regslot(m, wa);
    if (p) { unsigned sh = (unsigned)(a & 0x3) * 8; *p = (*p & ~(0xffu << sh)) | ((uint32_t)d << sh); }
}
uint8_t dma_mock_read8(dma_mock_t *m, uint64_t a) {
    uint32_t w = dma_mock_reg_get(m, a & ~(uint64_t)0x3); return (uint8_t)(w >> ((unsigned)(a & 0x3) * 8));
}
void dma_mock_write16(dma_mock_t *m, uint64_t a, uint16_t d) {
    uint64_t wa = a & ~(uint64_t)0x3; uint32_t *p = regslot(m, wa);
    if (p) { unsigned sh = (unsigned)(a & 0x2) * 8; *p = (*p & ~(0xffffu << sh)) | ((uint32_t)d << sh); }
}
uint16_t dma_mock_read16(dma_mock_t *m, uint64_t a) {
    uint32_t w = dma_mock_reg_get(m, a & ~(uint64_t)0x3); return (uint16_t)(w >> ((unsigned)(a & 0x2) * 8));
}
void dma_mock_write64(dma_mock_t *m, uint64_t a, uint64_t d) {
    uint32_t *lo = regslot(m, a), *hi = regslot(m, a + 4);
    if (lo) *lo = (uint32_t)d;
    if (hi) *hi = (uint32_t)(d >> 32);
}
uint64_t dma_mock_read64(dma_mock_t *m, uint64_t a) {
    return (uint64_t)dma_mock_reg_get(m, a) | ((uint64_t)dma_mock_reg_get(m, a + 4) << 32);
}
