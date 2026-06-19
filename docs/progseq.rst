Programming-Sequence Generation (SystemVerilog / C / C++)
=========================================================

The ``sv-progseq`` target turns a PSS **component tree** — a register model plus
the driver/operation routines layered on it — into a reusable **SystemVerilog
programming API**. A SV/UVM consumer can then write::

   status = dma.mem_to_mem_copy(.channel(5), .src_addr(s), .dst_addr(d), .num_bytes(4096));

and have it run the exact register-programming sequence the PSS describes,
expressed against an abstract bus the consumer supplies (front-door BFM,
backdoor poke, or a C model — unchanged).

The worked example throughout is the WISHBONE DMA model in
``examples/export/programming_seqs/`` (``dma_regs.pss`` + ``dma_engine.pss``).

Quick start
-----------

Generate the package and put the bundled core package on your compile order:

.. code-block:: console

   $ pssc compile -t sv-progseq --root dma_engine_c \
         examples/export/programming_seqs/dma_regs.pss \
         examples/export/programming_seqs/dma_engine.pss \
         -o out/

   $ pssc sv-core-path --file     # path to pssc_reg_pkg.sv (the core runtime)

This writes ``out/<package>.sv`` (default ``<root>_pkg``) and copies the core
runtime ``out/pssc_reg_pkg.sv`` alongside it. Compile them in dependency order::

   pssc_reg_pkg.sv   <package>.sv   <your testbench>.sv

Options (``pssc compile -t sv-progseq ...``):

================================  ============================================
Option                            Description
================================  ============================================
``--root COMP``                   root component type (required); bare or
                                  qualified name (``pkg::comp``)
``--package NAME``                generated package name (default ``<root>_pkg``)
``--no-core-copy``                do not copy ``pssc_reg_pkg.sv`` into the output
================================  ============================================

The generated API
-----------------

For a root component ``C`` the package contains:

``<value>_s`` (packed structs)
   register bit-field layouts, one per register value type.
``<group>_c`` (classes)
   the register model, one per ``reg_group_c`` component.
``C_if`` (interface class)
   the **export API** — one ``task`` per operation.
``C_import_if`` (interface class)
   the import API — ``extends pss_mem_if`` (plus any global imports).
``C`` (class)
   the **component class** — export implementation + import redirect + static
   ``create()``, all in one.

Interface classes use the ``_if`` suffix. ``C_if`` is *your interface to the
component*: it exposes the operations and nothing else.

Supplying the bus
-----------------

The generated model never touches a pin. It reaches the DUT through the core
memory-access interface ``pss_mem_if`` (in ``pssc_reg_pkg``):

.. code-block:: systemverilog

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

Notes:

- The primitives are **tasks** (a front-door access can consume time); reads
  return through an ``output`` argument.
- ``addr_handle_t`` is ``bit [63:0]`` (PSS ``addr_handle_t``).
- The register handle picks the primitive whose width is the value width rounded
  up to the nearest legal size (8/16/32/64).

You can supply the bus two ways:

1. **Implement ``pss_mem_if``** (or ``C_import_if``) directly.
2. **Match the signatures only** (duck typing). Your class need not formally
   ``implement`` the interface — pass it as the ``IMP_T`` parameter and the
   component class forwards each primitive to it. This lets you reuse an existing
   BFM/adapter unchanged.

Constructing and calling
------------------------

The component class ``C`` carries a static ``create()``. Its parameters are the
import object followed by the root component's ``ctor`` parameters; it returns
the export handle ``C_if``:

.. code-block:: systemverilog

   import pssc_reg_pkg::*;
   import dma_engine_c_pkg::*;     // or your --package name

   my_bus_c        bus = new(/* DUT handle, clock, ... */);   // signature-compatible
   dma_engine_c_if dma;
   int             status;

   dma = dma_engine_c#(my_bus_c)::create(bus, 64'h4000_0000);

   dma.configure_channel(5, 7, 0, 0, 0);
   dma.mem_to_mem_copy(status, 5, 32'h1000_0000, 32'h2000_0000, 4096);
   if (status != 0) $error("DMA copy failed");

Conventions visible above:

- A blocking operation that returns a PSS ``int`` carries its result on a leading
  ``output int status`` argument (a blocking routine must be a ``task``).
- PSS arguments that collide with SV keywords are renamed (e.g. ``priority`` →
  ``priority_``).
- ``IMP_T`` defaults to ``C_import_if``; override it (as above) to wire a
  duck-typed object.

How the redirect works
~~~~~~~~~~~~~~~~~~~~~~~~

``C`` ``implements C_if, C_import_if`` and holds both the user object and the
register model. It constructs the register model with ``this`` as the bus —
because ``C`` *is-a* ``pss_mem_if`` (via ``C_import_if``), every register access
routes ``m_regs`` → ``this.write32/read32`` → the user object. There is no
separate adapter or factory class.

Worked example
--------------

Each backend ships a self-checking testbench that drives the generated WB DMA API
through a mock bus and prints ``WB_DMA PROTOTYPE PASS``, plus a validated
hand-written reference the generator converges on (references live under
``examples/export/programming_seqs/``):

- **SV** — TB ``tests/progseq/data/wb_dma_tb.sv``, reference ``wb_dma_sv_proto.sv``;
  gated under Verilator.
- **C** — TB ``tests/progseq/data/c/wb_dma_tb*.c``, reference ``c_proto/``; gated
  under gcc + clang. The reference compiles all three link styles from one source,
  demonstrating the byte-identical bodies.
- **C++** — TB ``tests/progseq/data/cpp/wb_dma_tb.cpp``, reference ``cpp_proto/``;
  gated under g++ + clang++.

C backend (``c-progseq``)
-------------------------

The ``c-progseq`` target emits the same programming API in C: register value
**unions** (anonymous-union bitfields, so ``csr.FIELD`` works), zero-overhead
**baked inline accessors**, and free functions over an opaque ``<prefix>_t``.
Bodies keep native value-returning reads, native ``return``, and native
``do...while`` — closer to the PSS source than the SV output.

.. code-block:: console

   $ pssc compile -t c-progseq --root dma_engine_c --prefix wb_dma \
         --link-style vtable \
         examples/export/programming_seqs/dma_regs.pss \
         examples/export/programming_seqs/dma_engine.pss -o out/

   $ pssc c-core-path --file pssc_mem_vtable.h   # locate a core seam header

The **memory-access seam** is chosen by ``--link-style`` — the *only* thing it
changes; every register accessor and operation body is byte-identical across the
three:

================  ==========================================================
``--link-style``  Seam / when to use
================  ==========================================================
``vtable``        a ``pssc_mem_if`` struct of function pointers + ``ctx``
                  (default; multi-instance, host-friendly — the C analogue of
                  SV's ``pss_mem_if``)
``direct``        user-supplied ``extern`` functions linked by name
                  (bare-metal, single DUT — zero per-instance storage)
``mmio``          inlined ``*(volatile T*)addr`` load/store (firmware against
                  real registers; no import to implement; header-only)
================  ==========================================================

Other options: ``--prefix NAME`` (symbol/file prefix; default root name sans
``_c``), ``--reg-style {bitfields,accessors}`` (``accessors`` emits a portable,
layout-independent ``<type>_<FIELD>_get/_set`` fallback), ``--header-only`` (a
single self-contained ``.h``; forced for ``mmio``). Output is ``<prefix>.h``
(+ ``<prefix>.c`` unless header-only) plus the copied core seam header(s).

Construct and call (vtable)::

   pssc_mem_if bus = { ..., .ctx = &my_state };
   wb_dma_t *dma = wb_dma_create(&bus, 0x40000000u);
   int st = wb_dma_mem_to_mem_copy(dma, 5, src, dst, 4096);
   wb_dma_destroy(dma);

For embedded/static allocation, ``wb_dma_init(self, ...)`` fills a caller-owned
struct (no ``malloc``).

C++ backend (``cpp-progseq``)
-----------------------------

The ``cpp-progseq`` target is the closest to SystemVerilog: pure-virtual export
interfaces, a real ``pssc::reg<T,ACC>`` **template** (1:1 with SV's
``reg_c #(T,ACC)``), and register-group classes. The user subclasses
``pssc::mem_if`` directly — **no redirect trick**.

.. code-block:: console

   $ pssc compile -t cpp-progseq --root dma_engine_c --namespace wb_dma \
         examples/export/programming_seqs/dma_regs.pss \
         examples/export/programming_seqs/dma_engine.pss -o out/

   $ pssc cpp-core-path --file    # path to pssc_reg.hpp (the core runtime)

This writes a single header ``out/<namespace>.hpp`` and copies ``pssc_reg.hpp``
alongside. Use it::

   struct my_bus : pssc::mem_if { /* override read32/write32/... */ };
   my_bus bus;
   auto dma = wb_dma::wb_dma::create(bus, 0x40000000u);  // unique_ptr<wb_dma_if>
   dma->mem_to_mem_copy(5, src, dst, 4096);

Options: ``--namespace NAME`` (namespace + class prefix; default root sans
``_c``), ``--dispatch {virtual,template}`` (``virtual`` default; the
zero-overhead ``template`` model is planned). A stock ``pssc::mmio_mem`` seam
ships for bare-metal MMIO (the C++ analogue of C ``--link-style mmio``).

Choosing a backend
-------------------

================  ================================================================
Backend           Typical use
================  ================================================================
``sv-progseq``    SystemVerilog/UVM testbenches; front-door BFM or backdoor poke
``c-progseq``     firmware/drivers (``mmio``/``direct``) or host C models (``vtable``)
``cpp-progseq``   host C++ models and reference drivers; template-rich, type-safe
================  ================================================================

Limitations (this phase)
------------------------

- **C/C++ value layouts assume little-endian** bitfield allocation (gcc/clang,
  x86/ARM, LP64/LLP64), documented in each generated header's banner. Use C
  ``--reg-style accessors`` for a layout-independent fallback.
- **C++ ``--dispatch template``** (zero-overhead, duck-typed bus) is planned; the
  default ``virtual`` dispatch is shipped.
- **Registers are internal.** A component's register groups back its operations;
  they are not surfaced as a separate navigable API.
- **Front-door timing.** The SV backend emits only the ``task`` form (no zero-time
  backdoor flavor).

See also
--------

- *Programming-Sequence Generation — Architecture* (``progseq_design``) — the
  generation architecture and module map.
- ``pssc sv-core-path`` / ``c-core-path`` / ``cpp-core-path`` — locate the
  bundled core runtime/seam header(s) for your build.
