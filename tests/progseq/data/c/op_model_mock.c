/* op_model_mock.c -- see op_model_mock.h for what is modelled and why. */
#include <stdio.h>
#include <string.h>

#include "op_model_mock.h"

static void om_trace(om_mock_t *m, uint8_t is_write, uint8_t width,
                     uint64_t a, uint64_t d)
{
    if (m->n_trace >= OM_TRACE_CAP) { m->overflow++; return; }
    m->trace[m->n_trace].is_write = is_write;
    m->trace[m->n_trace].width    = width;
    m->trace[m->n_trace].addr     = a;
    m->trace[m->n_trace].data     = d;
    m->n_trace++;
}

void om_init(om_mock_t *m, uint64_t base)
{
    memset(m, 0, sizeof(*m));
    m->base = base;
}

uint64_t om_ch_reg(om_mock_t *m, int ch, unsigned off)
{
    return m->base + OM_CH_BASE + (uint64_t)OM_CH_STRIDE * (unsigned)ch + off;
}

/* Which channel's CSR is `a`, or -1. */
static int om_csr_of(om_mock_t *m, uint64_t a)
{
    int i;
    for (i = 0; i < OM_CH_COUNT; i++)
        if (a == om_ch_reg(m, i, 0)) return i;
    return -1;
}

static uint32_t *om_word(om_mock_t *m, uint64_t a)
{
    uint64_t off = (a - m->base) >> 2;
    if (a < m->base || off >= OM_REGWORDS) return NULL;
    return &m->regmem[off];
}

void om_write32(void *ctx, uint64_t a, uint32_t d)
{
    om_mock_t *m = (om_mock_t *)ctx;
    uint32_t *w = om_word(m, a);
    int ch = om_csr_of(m, a);

    om_trace(m, 1, 32, a, d);
    if (!w) return;

    if (ch >= 0) {
        /* STOP wins over CH_EN: it is the abort, and the device reports it as
         * an error. Checked FIRST so a read-modify-write that happens to carry
         * ch_en=1 along with stop=1 still aborts. */
        if (d & OM_CSR_STOP) {
            m->running[ch] = 0;
            m->polls[ch]   = 0;
            *w = (d & ~(OM_CSR_STOP | OM_CSR_BUSY | OM_CSR_CH_EN))
                 | OM_CSR_ERR | OM_CSR_INT_ERR;
            return;
        }
        if (d & OM_CSR_CH_EN) {
            m->running[ch] = 1;
            m->polls[ch]   = 0;
            *w = (d | OM_CSR_BUSY) & ~(OM_CSR_DONE | OM_CSR_ERR);
            return;
        }
    }
    *w = d;
}

uint32_t om_read32(void *ctx, uint64_t a)
{
    om_mock_t *m = (om_mock_t *)ctx;
    uint32_t *w = om_word(m, a);
    int ch = om_csr_of(m, a);
    uint32_t v;

    if (!w) { om_trace(m, 0, 32, a, 0); return 0; }

    if (ch >= 0 && m->running[ch]) {
        if (++m->polls[ch] >= OM_PENDING_POLLS) {
            m->running[ch] = 0;
            *w = (*w & ~OM_CSR_BUSY) | OM_CSR_DONE | OM_CSR_INT_DONE;
        }
    }
    v = *w;
    om_trace(m, 0, 32, a, v);

    /* Read-to-clear on CHn_CSR: done, err and the interrupt sources. The model
     * documents this at length -- it is why a stop and the transfer it aborts
     * race for the ERR, and why only one of them can see it. */
    if (ch >= 0)
        *w &= ~(OM_CSR_DONE | OM_CSR_ERR | OM_CSR_INT_DONE | OM_CSR_INT_ERR);
    return v;
}

/* The narrow and wide accesses are plain storage: the operation model programs
 * this device entirely through 32-bit registers, so anything else arriving here
 * is itself a finding. They are traced, not rejected, so the testbench can say
 * so with a register address rather than a crash. */
void om_write8(void *ctx, uint64_t a, uint8_t d)
{
    om_mock_t *m = (om_mock_t *)ctx;
    uint32_t *w = om_word(m, a & ~3ull);
    om_trace(m, 1, 8, a, d);
    if (w) { unsigned sh = (unsigned)(a & 3) * 8;
             *w = (*w & ~(0xffu << sh)) | ((uint32_t)d << sh); }
}

uint8_t om_read8(void *ctx, uint64_t a)
{
    om_mock_t *m = (om_mock_t *)ctx;
    uint32_t *w = om_word(m, a & ~3ull);
    uint8_t v = w ? (uint8_t)(*w >> ((unsigned)(a & 3) * 8)) : 0;
    om_trace(m, 0, 8, a, v);
    return v;
}

void om_write16(void *ctx, uint64_t a, uint16_t d)
{
    om_mock_t *m = (om_mock_t *)ctx;
    uint32_t *w = om_word(m, a & ~3ull);
    om_trace(m, 1, 16, a, d);
    if (w) { unsigned sh = (unsigned)(a & 2) * 8;
             *w = (*w & ~(0xffffu << sh)) | ((uint32_t)d << sh); }
}

uint16_t om_read16(void *ctx, uint64_t a)
{
    om_mock_t *m = (om_mock_t *)ctx;
    uint32_t *w = om_word(m, a & ~3ull);
    uint16_t v = w ? (uint16_t)(*w >> ((unsigned)(a & 2) * 8)) : 0;
    om_trace(m, 0, 16, a, v);
    return v;
}

void om_write64(void *ctx, uint64_t a, uint64_t d)
{
    om_write32(ctx, a, (uint32_t)d);
    om_write32(ctx, a + 4, (uint32_t)(d >> 32));
}

uint64_t om_read64(void *ctx, uint64_t a)
{
    uint64_t lo = om_read32(ctx, a);
    return lo | ((uint64_t)om_read32(ctx, a + 4) << 32);
}

/* --- trace queries --- */

unsigned om_n_writes(om_mock_t *m, uint64_t addr)
{
    unsigned i, n = 0;
    for (i = 0; i < m->n_trace; i++)
        if (m->trace[i].is_write && m->trace[i].addr == addr) n++;
    return n;
}

unsigned om_n_reads(om_mock_t *m, uint64_t addr)
{
    unsigned i, n = 0;
    for (i = 0; i < m->n_trace; i++)
        if (!m->trace[i].is_write && m->trace[i].addr == addr) n++;
    return n;
}

uint64_t om_last_write(om_mock_t *m, uint64_t addr)
{
    unsigned i;
    uint64_t v = 0;
    for (i = 0; i < m->n_trace; i++)
        if (m->trace[i].is_write && m->trace[i].addr == addr) v = m->trace[i].data;
    return v;
}

int om_find(om_mock_t *m, uint64_t addr, uint8_t is_write, unsigned from)
{
    unsigned i;
    for (i = from; i < m->n_trace; i++)
        if (m->trace[i].addr == addr && m->trace[i].is_write == is_write)
            return (int)i;
    return -1;
}

void om_dump(om_mock_t *m)
{
    unsigned i;
    printf("--- %u accesses (overflow=%u) ---\n", m->n_trace, m->overflow);
    for (i = 0; i < m->n_trace; i++)
        printf("  [%3u] %s%-2u 0x%08llx = 0x%08llx\n", i,
               m->trace[i].is_write ? "W" : "R", m->trace[i].width,
               (unsigned long long)m->trace[i].addr,
               (unsigned long long)m->trace[i].data);
}
