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
//   * channel_c       -- PSS `sync_pkg::channel_c<Te, DEPTH>` (§21.9.1)
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

    // Masked write -- PSS 3.1 §21.14.1:
    //
    //   REG_VAL(new) = (REG_VAL(current) & ~mask) | (val & mask)
    //
    // THIS READS THE REGISTER, and that is the LRM's definition rather than an
    // implementation choice. On a device whose reads have side effects -- a
    // channel CSR that clears its status and interrupt-source bits when read --
    // a masked write has those side effects too. A caller reaching for this
    // instead of read/modify/write is choosing a shorter spelling, not fewer
    // bus transactions.
    //
    // One task covers all four spellings the LRM offers. write_field,
    // write_fields and write_masked are resolved and folded to a (mask, value)
    // constant pair by the compiler, so no field name and no per-register
    // generation reaches here; this stays type-generic.
    //
    // It is also the single place a platform read-modify-write instruction or a
    // byte-enable write would go. §21.14.1 permits that optimisation but does
    // not require it, and nothing above this line would have to change.
    task write_val_masked(data_t mask, data_t val);
      data_t cur;
      read_val(cur);
      write_val((cur & ~mask) | (val & mask));
    endtask
  endclass

  // ----- PSS sync_pkg::channel_c<Te, DEPTH> (LRM 3.1 §21.9.1). -----
  // A bounded FIFO with blocking and non-blocking access at both ends. Backed
  // by `mailbox`, which is the SV construct that already has these exact
  // semantics: bounded, thread-safe, blocking `get`/`put`, non-blocking
  // `try_get`/`try_put`.
  //
  // DEPTH IS PART OF THE MODEL, not a buffer-tuning knob. `channel_c<T,1>` is a
  // coalescing binary semaphore -- `try_put` failing while an item is pending
  // is the behaviour a wake-up channel relies on -- so the parameter is passed
  // straight to `new()` and never rounded up.
  //
  // NOTE the guard below. `mailbox #(T) m = new(0)` is UNBOUNDED in SV, so a
  // DEPTH that reached here as 0 would produce a channel that never coalesces
  // and never blocks a writer: a behavioural change with no error anywhere. PSS
  // requires a positive depth and the front end rejects 0, so this is the
  // backstop for a channel that arrives by some other path.
  class channel_c #(type Te = bit, int DEPTH = 1);
    localparam int BOUND = (DEPTH < 1) ? 1 : DEPTH;

    protected mailbox #(Te) m_mbx;

    function new();
      m_mbx = new(BOUND);
    endfunction

    // Blocking. Tasks, because they consume time -- and because a target exec
    // blocked here must not stall other execs, which is the whole reason PSS
    // has channels rather than a polling loop (§20.8).
    task get(output Te t);
      m_mbx.get(t);
    endtask

    task put(Te t);
      m_mbx.put(t);
    endtask

    // Non-blocking. Functions, so they are callable from contexts that cannot
    // consume time -- which is what makes `try_put` legal from an interrupt
    // observer or any other simulator thread outside the model's own process.
    //
    // `mailbox::try_get`/`try_put` return an int: > 0 on success, 0 when the
    // operation cannot proceed, and < 0 for a type mismatch (only reachable
    // with an untyped mailbox -- this one is parameterized). PSS specifies a
    // bool, so anything not positive is false.
    function bit try_get(output Te t);
      return (m_mbx.try_get(t) > 0);
    endfunction

    function bit try_put(Te t);
      return (m_mbx.try_put(t) > 0);
    endfunction

    // Not PSS API. For a testbench that needs to see whether a wake is already
    // pending without consuming it -- diagnostics, not stimulus.
    function int num();
      return m_mbx.num();
    endfunction
  endclass

endpackage
