// pssc_reg_pkg -- core runtime for pssc-generated programming-sequence models.
//
// IP-independent, hand-written ONCE, shipped with pssc and reused verbatim by
// every generated package (see `pssc compile -t sv-progseq` and
// `pssc sv-core-path`). Holds:
//   * addr_handle_t   -- PSS addr_handle_t mapped to a 64-bit SV address
//   * pss_mem_if   -- the memory-access interface (THE seam to the DUT)
//   * reg_access_e    -- register access mode
//   * reg_c           -- generic register handle (address folded at build,
//                        width-based transaction sizing)
//
// Design: design/pss-programming-seq-gen-design.md (§5).
// Validated reference: examples/export/programming_seqs/wb_dma_sv_proto.sv.

package pssc_reg_pkg;

  // PSS addr_handle_t -> 64-bit SV address.
  typedef bit [63:0] addr_handle_t;

  // ----- The memory-access interface. -----
  // Pure-virtual, stateless API -> interface class (suffix `_if`). The user (or
  // an adapter generated next to the model) supplies the implementation. Tasks,
  // not functions: a front-door access can consume time. Reads return through
  // an output argument.
  interface class pss_mem_if;
    pure virtual task write8 (addr_handle_t addr, bit [7:0]  data);
    pure virtual task read8  (addr_handle_t addr, output bit [7:0]  data);
    pure virtual task write16(addr_handle_t addr, bit [15:0] data);
    pure virtual task read16 (addr_handle_t addr, output bit [15:0] data);
    pure virtual task write32(addr_handle_t addr, bit [31:0] data);
    pure virtual task read32 (addr_handle_t addr, output bit [31:0] data);
    pure virtual task write64(addr_handle_t addr, bit [63:0] data);
    pure virtual task read64 (addr_handle_t addr, output bit [63:0] data);
  endclass

  // ----- Register access mode. -----
  typedef enum {READWRITE, READONLY, WRITEONLY} reg_access_e;

  // ----- Generic register handle, parameterized by value type. -----
  // Holds its absolute address, folded at build time. data_t tracks $bits(T);
  // the bus primitive is selected from ACC_W (register width rounded up to the
  // nearest legal transaction size: 8/16/32/64). All widths fold at elaboration.
  class reg_c #(type T = bit [31:0], reg_access_e ACC = READWRITE);
    localparam int          WIDTH = $bits(T);
    localparam int          POW2  = 1 << $clog2(WIDTH);          // nearest pow2 >= WIDTH
    localparam int          ACC_W = POW2 < 8 ? 8 : (POW2 > 64 ? 64 : POW2);
    typedef bit [WIDTH-1:0] data_t;                             // raw value-vector, width of T

    protected pss_mem_if m_bus;
    protected addr_handle_t m_addr;

    function new(pss_mem_if bus, addr_handle_t addr);
      m_bus  = bus;
      m_addr = addr;
    endfunction

    function addr_handle_t addr(); return m_addr; endfunction

    // Struct-typed accessors -- legible field-level access at call sites.
    task write(T v);
      data_t raw = v;   // bitstream pack
      write_val(raw);
    endtask
    task read(output T v);
      data_t raw;
      read_val(raw);
      v = T'(raw);
    endtask

    // Raw accessors -- value width tracks T; transaction sized to ACC_W.
    task write_val(data_t v);
      if      (ACC_W == 8)  m_bus.write8 (m_addr,  8'(v));
      else if (ACC_W == 16) m_bus.write16(m_addr, 16'(v));
      else if (ACC_W == 32) m_bus.write32(m_addr, 32'(v));
      else                  m_bus.write64(m_addr, 64'(v));
    endtask
    task read_val(output data_t v);
      bit [7:0]  d8;
      bit [15:0] d16;
      bit [31:0] d32;
      bit [63:0] d64;
      if      (ACC_W == 8)  begin m_bus.read8 (m_addr, d8);  v = data_t'(d8);  end
      else if (ACC_W == 16) begin m_bus.read16(m_addr, d16); v = data_t'(d16); end
      else if (ACC_W == 32) begin m_bus.read32(m_addr, d32); v = data_t'(d32); end
      else                  begin m_bus.read64(m_addr, d64); v = data_t'(d64); end
    endtask
  endclass

endpackage
