/* wb_dma_tb.c -- self-checking testbench for the C WB DMA driver.
 *
 * Drives the (hand-written or generated) wb_dma.h API against the shared mock
 * hardware (dma_mock.c) and prints WB_DMA PROTOTYPE PASS on success. This is the
 * C analogue of the SV tb in wb_dma_sv_proto.sv; the same five checks, incl.
 * real data movement and the error path.
 *
 * Compiles for the vtable seam (default) or the direct seam (PSSC_LINK_DIRECT).
 * mmio has no simulated-bus hook, so it is exercised by wb_dma_tb_mmio.c.
 */
#include <stdio.h>

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
#include "dma_mock.h"

static uint64_t chbase(uint64_t base, int ch) { return base + 0x20u + (uint64_t)ch * 0x20u; }

#if defined(PSSC_LINK_DIRECT)
/* The direct seam links these by name; forward to one global mock. */
static dma_mock_t g_mock;
void     pssc_mem_write8 (pssc_addr_t a, uint8_t  d) { dma_mock_write8 (&g_mock, a, d); }
uint8_t  pssc_mem_read8  (pssc_addr_t a)             { return dma_mock_read8 (&g_mock, a); }
void     pssc_mem_write16(pssc_addr_t a, uint16_t d) { dma_mock_write16(&g_mock, a, d); }
uint16_t pssc_mem_read16 (pssc_addr_t a)             { return dma_mock_read16(&g_mock, a); }
void     pssc_mem_write32(pssc_addr_t a, uint32_t d) { dma_mock_write32(&g_mock, a, d); }
uint32_t pssc_mem_read32 (pssc_addr_t a)             { return dma_mock_read32(&g_mock, a); }
void     pssc_mem_write64(pssc_addr_t a, uint64_t d) { dma_mock_write64(&g_mock, a, d); }
uint64_t pssc_mem_read64 (pssc_addr_t a)             { return dma_mock_read64(&g_mock, a); }
#else
/* The vtable seam takes a void* ctx; forward to the mock it points at. */
static void     w8 (void *c, pssc_addr_t a, uint8_t  d) { dma_mock_write8 ((dma_mock_t *)c, a, d); }
static uint8_t  r8 (void *c, pssc_addr_t a)             { return dma_mock_read8 ((dma_mock_t *)c, a); }
static void     w16(void *c, pssc_addr_t a, uint16_t d) { dma_mock_write16((dma_mock_t *)c, a, d); }
static uint16_t r16(void *c, pssc_addr_t a)             { return dma_mock_read16((dma_mock_t *)c, a); }
static void     w32(void *c, pssc_addr_t a, uint32_t d) { dma_mock_write32((dma_mock_t *)c, a, d); }
static uint32_t r32(void *c, pssc_addr_t a)             { return dma_mock_read32((dma_mock_t *)c, a); }
static void     w64(void *c, pssc_addr_t a, uint64_t d) { dma_mock_write64((dma_mock_t *)c, a, d); }
static uint64_t r64(void *c, pssc_addr_t a)             { return dma_mock_read64((dma_mock_t *)c, a); }
#endif

static int run_selfcheck(wb_dma_t *dma, dma_mock_t *m, uint64_t base) {
    int errors = 0, status;

    /* 1) configure_channel: sets PRIORITY/MODE/SRC/DST, leaves CH_EN clear. */
    wb_dma_configure_channel(dma, 5, 7, 1, 1, 0);
    {
        uint32_t csr = dma_mock_reg_get(m, chbase(base, 5));
        if (CSR_PRIORITY(csr) != 7 || CSR_MODE(csr) != 1 ||
            CSR_SRC_SEL(csr) != 1 || CSR_DST_SEL(csr) != 0) {
            printf("  FAIL configure_channel fields: csr=0x%08x\n", csr); errors++;
        }
        if (CSR_CH_EN(csr) != 0) { printf("  FAIL configure_channel started the channel\n"); errors++; }
    }

    /* 2) mem_to_mem_copy: program + complete + actually move data. */
    for (int i = 0; i < 16; i++) dma_mock_sys_set(m, 0x10000000u + i, (uint8_t)(i + 1));
    status = wb_dma_mem_to_mem_copy(dma, 3, 0x10000000u, 0x20000000u, 16);
    if (status != 0) { printf("  FAIL copy status=%d\n", status); errors++; }
    for (int i = 0; i < 16; i++)
        if (dma_mock_sys_get(m, 0x20000000u + i) != (uint8_t)(i + 1)) {
            printf("  FAIL copy data[%d]=0x%02x\n", i, dma_mock_sys_get(m, 0x20000000u + i)); errors++;
        }
    {
        uint64_t cb = chbase(base, 3);
        uint32_t sz = dma_mock_reg_get(m, cb + 0x04u);
        if (dma_mock_reg_get(m, cb + 0x08u) != 0x10000000u) { printf("  FAIL A0\n"); errors++; }
        if (dma_mock_reg_get(m, cb + 0x10u) != 0x20000000u) { printf("  FAIL A1\n"); errors++; }
        if (SZ_TOT_SZ(sz) != 4) { printf("  FAIL TOT_SZ=%u\n", SZ_TOT_SZ(sz)); errors++; }
    }

    /* 3) mem_to_mem_copy_masked: also programs AM0/AM1. */
    status = wb_dma_mem_to_mem_copy_masked(dma, 7, 0x30000000u, 0x00000fffu,
                                           0x40000000u, 0x000000ffu, 8);
    if (status != 0) { printf("  FAIL masked status=%d\n", status); errors++; }
    {
        uint64_t cb = chbase(base, 7);
        if (dma_mock_reg_get(m, cb + 0x0cu) != 0x00000fffu) { printf("  FAIL AM0\n"); errors++; }
        if (dma_mock_reg_get(m, cb + 0x14u) != 0x000000ffu) { printf("  FAIL AM1\n"); errors++; }
    }

    /* 4) mem_to_mem_copy_desc: programs DESC and sets USE_ED. */
    status = wb_dma_mem_to_mem_copy_desc(dma, 9, 0x50000000u);
    if (status != 0) { printf("  FAIL desc status=%d\n", status); errors++; }
    {
        uint64_t cb = chbase(base, 9);
        uint32_t csr = dma_mock_reg_get(m, cb);
        if (dma_mock_reg_get(m, cb + 0x18u) != 0x50000000u) { printf("  FAIL DESC\n"); errors++; }
        if (CSR_USE_ED(csr) != 1) { printf("  FAIL USE_ED not set\n"); errors++; }
    }

    /* 5) Error path: poison source address makes the channel set ERR. */
    status = wb_dma_mem_to_mem_copy(dma, 2, 0xdead0000u, 0x60000000u, 4);
    if (status != 1) { printf("  FAIL error path: expected status=1 got %d\n", status); errors++; }

    return errors;
}

int main(void) {
    uint64_t base = 0x40000000u;
    int errors;
#if defined(PSSC_LINK_DIRECT)
    dma_mock_init(&g_mock, base);
    wb_dma_t *dma = wb_dma_create(base);
    errors = run_selfcheck(dma, &g_mock, base);
#else
    static dma_mock_t mock;
    dma_mock_init(&mock, base);
    pssc_mem_if busif = { w8, r8, w16, r16, w32, r32, w64, r64, &mock };
    wb_dma_t *dma = wb_dma_create(&busif, base);
    errors = run_selfcheck(dma, &mock, base);
#endif
    wb_dma_destroy(dma);
    if (errors == 0) printf("WB_DMA PROTOTYPE PASS\n");
    else             printf("WB_DMA PROTOTYPE FAIL (%d errors)\n", errors);
    return errors ? 1 : 0;
}
