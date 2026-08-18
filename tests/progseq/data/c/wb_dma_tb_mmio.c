/* wb_dma_tb_mmio.c -- self-check for the mmio link style.
 *
 * mmio accesses real CPU addresses via volatile load/store; there is no hook to
 * model a live DMA engine (auto-DONE / data movement). So this TB backs the
 * register space with a plain RAM block, pre-seeds the channel status bits the
 * polling loops wait on (DONE for the copies, ERR for the error path), and
 * verifies that each operation programs the registers correctly. Data movement
 * is out of scope for mmio (use vtable/direct for a simulated bus).
 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "wb_dma.h"

/* The register value layouts are the driver's IMPLEMENTATION and are not in
 * wb_dma.h -- deliberately: a caller drives this device through the operations,
 * not by assembling register words. A checker still has to decode the words the
 * driver left behind, so it states the bit positions ITSELF.
 *
 * That is the stronger arrangement anyway. Decoding with the generator's own
 * layout could never detect a generator that put a field in the wrong place:
 * the check and the thing checked would move together. These constants come
 * from the register spec (dma_regs.pss), which is what the driver is supposed
 * to agree with. */
#define FLD(w, lsb, width)  (((w) >> (lsb)) & ((1u << (width)) - 1u))
#define CSR_CH_EN(w)    FLD(w,  0, 1)
#define CSR_DST_SEL(w)  FLD(w,  1, 1)
#define CSR_SRC_SEL(w)  FLD(w,  2, 1)
#define CSR_MODE(w)     FLD(w,  5, 1)
#define CSR_USE_ED(w)   FLD(w,  7, 1)
#define CSR_PRIORITY(w) FLD(w, 13, 3)
#define SZ_TOT_SZ(w)    FLD(w,  0, 12)

#define RAMWORDS 256
static uint32_t g_ram[RAMWORDS];

static uint64_t chbase_off(int ch) { return 0x20u + (uint64_t)ch * 0x20u; }
static uint32_t ram_at(uint64_t off) { return g_ram[off / 4]; }
static void     seed_csr(int ch, uint32_t bits) { g_ram[chbase_off(ch) / 4] = bits; }

int main(void) {
    memset(g_ram, 0, sizeof(g_ram));
    uint64_t base = (uint64_t)(uintptr_t)g_ram;
    int errors = 0, status;

    wb_dma_t *dma = wb_dma_create(base);

    /* 1) configure_channel (no polling). */
    wb_dma_configure_channel(dma, 5, 7, 1, 1, 0);
    {
        uint32_t csr = ram_at(chbase_off(5));
        if (CSR_PRIORITY(csr) != 7 || CSR_MODE(csr) != 1 ||
            CSR_SRC_SEL(csr) != 1 || CSR_DST_SEL(csr) != 0) {
            printf("  FAIL configure_channel fields: csr=0x%08x\n", csr); errors++;
        }
        if (CSR_CH_EN(csr) != 0) { printf("  FAIL configure_channel started the channel\n"); errors++; }
    }

    /* 2) mem_to_mem_copy: pre-seed DONE so the poll exits; verify programming. */
    seed_csr(3, 0x00000800u);
    status = wb_dma_mem_to_mem_copy(dma, 3, 0x10000000u, 0x20000000u, 16);
    if (status != 0) { printf("  FAIL copy status=%d\n", status); errors++; }
    {
        uint64_t cb = chbase_off(3);
        uint32_t sz = ram_at(cb + 0x04u);
        if (ram_at(cb + 0x08u) != 0x10000000u) { printf("  FAIL A0\n"); errors++; }
        if (ram_at(cb + 0x10u) != 0x20000000u) { printf("  FAIL A1\n"); errors++; }
        if (SZ_TOT_SZ(sz) != 4) { printf("  FAIL TOT_SZ=%u\n", SZ_TOT_SZ(sz)); errors++; }
    }

    /* 3) masked: verify AM0/AM1. */
    seed_csr(7, 0x00000800u);
    status = wb_dma_mem_to_mem_copy_masked(dma, 7, 0x30000000u, 0x00000fffu,
                                           0x40000000u, 0x000000ffu, 8);
    if (status != 0) { printf("  FAIL masked status=%d\n", status); errors++; }
    {
        uint64_t cb = chbase_off(7);
        if (ram_at(cb + 0x0cu) != 0x00000fffu) { printf("  FAIL AM0\n"); errors++; }
        if (ram_at(cb + 0x14u) != 0x000000ffu) { printf("  FAIL AM1\n"); errors++; }
    }

    /* 4) desc: verify DESC and USE_ED. */
    seed_csr(9, 0x00000800u);
    status = wb_dma_mem_to_mem_copy_desc(dma, 9, 0x50000000u);
    if (status != 0) { printf("  FAIL desc status=%d\n", status); errors++; }
    {
        uint64_t cb = chbase_off(9);
        uint32_t csr = ram_at(cb);
        if (ram_at(cb + 0x18u) != 0x50000000u) { printf("  FAIL DESC\n"); errors++; }
        if (CSR_USE_ED(csr) != 1) { printf("  FAIL USE_ED not set\n"); errors++; }
    }

    /* 5) error path: pre-seed ERR so the poll returns non-zero. */
    seed_csr(2, 0x00001000u);
    status = wb_dma_mem_to_mem_copy(dma, 2, 0xdead0000u, 0x60000000u, 4);
    if (status != 1) { printf("  FAIL error path: expected status=1 got %d\n", status); errors++; }

    wb_dma_destroy(dma);
    if (errors == 0) printf("WB_DMA PROTOTYPE PASS\n");
    else             printf("WB_DMA PROTOTYPE FAIL (%d errors)\n", errors);
    return errors ? 1 : 0;
}
