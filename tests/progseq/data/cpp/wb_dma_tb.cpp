// wb_dma_tb.cpp -- self-checking testbench for the C++ WB DMA driver.
//
// A DMA-aware mock bus (subclassing pssc::mem_if) models a channel that
// completes on CH_EN and moves TOT_SZ words A0->A1; a poison source forces ERR.
// The C++ port of tb_pkg::dma_mock_bus_c; the same five checks -> PROTOTYPE PASS.
#include <cstdint>
#include <cstdio>
#include <map>

#include "pssc_reg.hpp"
#include "wb_dma.hpp"

class dma_mock_bus : public pssc::mem_if {
    static constexpr std::uint32_t POISON_SRC = 0xdead0000u;
    pssc::addr_t base_;
public:
    std::map<pssc::addr_t, std::uint32_t> regmem;   // register space
    std::map<std::uint32_t, std::uint8_t> sysmem;   // system memory

    explicit dma_mock_bus(pssc::addr_t base) : base_(base) {}

    std::uint32_t rdword(pssc::addr_t a) const {
        auto it = regmem.find(a);
        return it == regmem.end() ? 0u : it->second;
    }

private:
    bool decode_csr(pssc::addr_t a, int &ch) const {
        if (a < base_ + 0x20u) return false;
        pssc::addr_t rel = a - (base_ + 0x20u);
        if (rel >= 31u * 0x20u) return false;
        if (rel % 0x20u != 0) return false;
        ch = static_cast<int>(rel / 0x20u);
        return true;
    }
    void run_transfer(int ch, pssc::addr_t csr_addr, std::uint32_t csr_data) {
        pssc::addr_t chbase = base_ + 0x20u + static_cast<pssc::addr_t>(ch) * 0x20u;
        std::uint32_t a0 = rdword(chbase + 0x08u);
        std::uint32_t a1 = rdword(chbase + 0x10u);
        std::uint32_t sz = rdword(chbase + 0x04u);
        int nbytes = static_cast<int>(sz & 0xfffu) * 4;
        if (a0 == POISON_SRC) {
            regmem[csr_addr] = (csr_data & ~0x00000401u) | 0x00001000u;  // ERR
            return;
        }
        for (int i = 0; i < nbytes; i++) {
            auto it = sysmem.find(a0 + i);
            sysmem[a1 + i] = (it == sysmem.end()) ? 0 : it->second;
        }
        regmem[csr_addr] = (csr_data & ~0x00000401u) | 0x00000800u;      // DONE
    }
    void maybe_run(pssc::addr_t a, std::uint32_t data) {
        int ch;
        if (decode_csr(a, ch) && (data & 0x1u)) run_transfer(ch, a, data);
    }

public:
    void          write8 (pssc::addr_t a, std::uint8_t  d) override { pssc::addr_t w = a & ~pssc::addr_t(3); unsigned sh = unsigned(a & 3) * 8; regmem[w] = (rdword(w) & ~(0xffu << sh)) | (std::uint32_t(d) << sh); }
    std::uint8_t  read8  (pssc::addr_t a) override { return std::uint8_t(rdword(a & ~pssc::addr_t(3)) >> (unsigned(a & 3) * 8)); }
    void          write16(pssc::addr_t a, std::uint16_t d) override { pssc::addr_t w = a & ~pssc::addr_t(3); unsigned sh = unsigned(a & 2) * 8; regmem[w] = (rdword(w) & ~(0xffffu << sh)) | (std::uint32_t(d) << sh); }
    std::uint16_t read16 (pssc::addr_t a) override { return std::uint16_t(rdword(a & ~pssc::addr_t(3)) >> (unsigned(a & 2) * 8)); }
    void          write32(pssc::addr_t a, std::uint32_t d) override { regmem[a] = d; maybe_run(a, d); }
    std::uint32_t read32 (pssc::addr_t a) override { return rdword(a); }
    void          write64(pssc::addr_t a, std::uint64_t d) override { regmem[a] = std::uint32_t(d); regmem[a + 4] = std::uint32_t(d >> 32); }
    std::uint64_t read64 (pssc::addr_t a) override { return std::uint64_t(rdword(a)) | (std::uint64_t(rdword(a + 4)) << 32); }
};

static pssc::addr_t chbase(pssc::addr_t base, int ch) { return base + 0x20u + pssc::addr_t(ch) * 0x20u; }

int main() {
    pssc::addr_t base = 0x40000000u;
    dma_mock_bus bus(base);
    auto dma = wb_dma::wb_dma::create(bus, base);
    int errors = 0, status;

    // 1) configure_channel
    dma->configure_channel(5, 7, true, true, false);
    {
        wb_dma::dma_ch_csr_t csr; csr.raw = bus.rdword(chbase(base, 5));
        if (csr.PRIORITY != 7 || csr.MODE != 1 || csr.SRC_SEL != 1 || csr.DST_SEL != 0) {
            std::printf("  FAIL configure_channel fields: csr=0x%08x\n", csr.raw); errors++;
        }
        if (csr.CH_EN != 0) { std::printf("  FAIL configure_channel started the channel\n"); errors++; }
    }

    // 2) mem_to_mem_copy + data movement
    for (int i = 0; i < 16; i++) bus.sysmem[0x10000000u + i] = std::uint8_t(i + 1);
    status = dma->mem_to_mem_copy(3, 0x10000000u, 0x20000000u, 16);
    if (status != 0) { std::printf("  FAIL copy status=%d\n", status); errors++; }
    for (int i = 0; i < 16; i++)
        if (bus.sysmem[0x20000000u + i] != std::uint8_t(i + 1)) {
            std::printf("  FAIL copy data[%d]=0x%02x\n", i, bus.sysmem[0x20000000u + i]); errors++;
        }
    {
        pssc::addr_t cb = chbase(base, 3);
        wb_dma::dma_ch_sz_t sz; sz.raw = bus.rdword(cb + 0x04u);
        if (bus.rdword(cb + 0x08u) != 0x10000000u) { std::printf("  FAIL A0\n"); errors++; }
        if (bus.rdword(cb + 0x10u) != 0x20000000u) { std::printf("  FAIL A1\n"); errors++; }
        if (sz.TOT_SZ != 4) { std::printf("  FAIL TOT_SZ=%u\n", sz.TOT_SZ); errors++; }
    }

    // 3) masked
    status = dma->mem_to_mem_copy_masked(7, 0x30000000u, 0x00000fffu, 0x40000000u, 0x000000ffu, 8);
    if (status != 0) { std::printf("  FAIL masked status=%d\n", status); errors++; }
    {
        pssc::addr_t cb = chbase(base, 7);
        if (bus.rdword(cb + 0x0cu) != 0x00000fffu) { std::printf("  FAIL AM0\n"); errors++; }
        if (bus.rdword(cb + 0x14u) != 0x000000ffu) { std::printf("  FAIL AM1\n"); errors++; }
    }

    // 4) desc
    status = dma->mem_to_mem_copy_desc(9, 0x50000000u);
    if (status != 0) { std::printf("  FAIL desc status=%d\n", status); errors++; }
    {
        pssc::addr_t cb = chbase(base, 9);
        wb_dma::dma_ch_csr_t csr; csr.raw = bus.rdword(cb);
        if (bus.rdword(cb + 0x18u) != 0x50000000u) { std::printf("  FAIL DESC\n"); errors++; }
        if (csr.USE_ED != 1) { std::printf("  FAIL USE_ED not set\n"); errors++; }
    }

    // 5) error path
    status = dma->mem_to_mem_copy(2, 0xdead0000u, 0x60000000u, 4);
    if (status != 1) { std::printf("  FAIL error path: expected status=1 got %d\n", status); errors++; }

    if (errors == 0) std::printf("WB_DMA PROTOTYPE PASS\n");
    else             std::printf("WB_DMA PROTOTYPE FAIL (%d errors)\n", errors);
    return errors ? 1 : 0;
}
