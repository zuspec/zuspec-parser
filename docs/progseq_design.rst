Programming-Sequence Generation — Architecture
==============================================

This page summarizes how the ``op-model-sv`` target lowers a PSS component tree to
SystemVerilog. The authoritative design notes are
``design/pss-programming-seq-gen-design.md`` (scheme) and
``design/pss-programming-seq-gen-impl-plan.md`` (implementation/test/doc plan);
the validated reference output is
``examples/export/programming_seqs/wb_dma_sv_proto.sv``.

Pipeline
--------

``pssc compile -t op-model-sv --root <comp>`` resolves the root component from the
translated IR and walks its subtree:

1. **Classify** each reachable component by its ``super`` type
   (`pssc.targets.progseq_model`): ``reg_group_c`` → register group;
   ``packed_s`` → register value struct; otherwise a regular component.
2. **Register model** (`pssc.targets.sv.lower_reg_model`): emit one packed
   struct per value type (fields reversed — PSS is LSB-first, SV packed is
   MSB-first) and one class per ``reg_group_c``, with offsets folded into each
   child handle. Scalar offsets come from the IR's pre-computed ``offset_map``;
   array base/stride is recovered by evaluating the affine
   ``get_offset_of_instance_array`` arms.
3. **Programming API** (`pssc.targets.sv.lower_progseq`): for each regular
   component, an export interface ``<comp>_if`` (one ``task`` per operation) and
   the single component class ``<comp>`` (operations + import redirect + static
   ``create()``). Operation bodies are translated statement-for-statement.
4. **Emit** (`pssc.targets.progseq_gen`): assemble the package, import the
   core, write ``<package>.sv``, and copy ``pssc_reg_pkg.sv``.

Generated shape
---------------

.. code-block:: text

   pssc_reg_pkg            (core, shipped)   addr_handle_t, pss_mem_if, reg_c
   <root>_pkg              (generated)
     value structs         <reg>_s ... (packed, fields reversed)
     register groups       <group>_c ...
     export API            <comp>_if          (pure virtual task per operation)
     import API            <comp>_import_if   (extends pss_mem_if)
     component class       <comp> #(IMP_T)    (impl + import redirect + create)

Body-translation rules
----------------------

PSS operation bodies map to SV with a few rewrites:

==================================  ===========================================
PSS                                 SV
==================================  ===========================================
``int`` return                      leading ``output int status`` arg
arg after an ``output``             explicit ``input`` (SV inherits direction)
``regs.<p>.read()`` (value form)    ``m_regs.<p>.read(tmp)`` (task/output form)
``repeat { B } while (c)``          ``forever begin B; if (!(c)) break; end``
``return v``                        ``status = v; return;``
SV-keyword identifier               renamed (``priority`` → ``priority_``)
==================================  ===========================================

The component class as the bus
------------------------------

The folded component class ``<comp>`` ``implements <comp>_if, <comp>_import_if``.
It builds the register model with ``this`` as the bus: since ``<comp>`` is-a
``pss_mem_if`` (via the import interface), register accesses route
``m_regs`` → ``this`` → the held user object ``m_imp``. This removes the need for
a separate adapter or factory class.

Frozen decisions
----------------

- Memory-access primitives are **tasks** (front-door timing); reads use ``output``.
- PSS ``addr_handle_t`` → ``bit [63:0]``.
- Transaction width = value width rounded up to 8/16/32/64 (``ACC_W``).
- ``create()`` takes the import handle + the root ``ctor`` parameters.
- Interface classes are suffixed ``_if``; the component is one class ``<comp>``.

C and C++ backends
------------------

The ``op-model-c`` and ``op-model-cpp`` targets reuse the language-neutral model
(``progseq_model``: walk + classify + the hoisted affine-offset and type-list
helpers) verbatim; only the per-language *emission* differs. The authoritative
notes are ``design/pss-c-op-model-cpp-gen-design.md`` and
``design/pss-c-op-model-cpp-gen-impl-plan.md``; the validated references are
``examples/export/programming_seqs/c_proto/`` and ``cpp_proto/``.

The one thing that varies between backends is the **seam** — how a register
access reaches the user's bus:

==============  ============================================================
Backend         Seam
==============  ============================================================
SV              ``pss_mem_if`` interface class + self-as-bus redirect
C ``vtable``    ``pssc_mem_if`` struct of function pointers + ``ctx``
C ``direct``    ``extern`` free functions linked by name
C ``mmio``      inlined ``*(volatile T*)addr`` load/store
C++             ``pssc::mem_if`` abstract base (user subclasses it)
==============  ============================================================

Because the seam is the only variable, **every C operation body is
byte-identical across the three link styles** — only the one-line ``pssc_bus()``
shim and the ``_create`` signature/``bus`` field differ. C and C++ bodies are
*simpler* than SV: native value-returning reads, native ``return`` values, and
native ``do...while`` (PSS ``repeat{}while``) — the three SV rewrites do not fire.

PSS construct → C / C++ artifact:

==============================  ==========================  =====================
PSS                             C                           C++
==============================  ==========================  =====================
``addr_handle_t``               ``pssc_addr_t``             ``pssc::addr_t``
``reg_c<T,ACC>``                baked inline accessor       ``pssc::reg<T,ACC>``
``struct : packed_s<>``         ``union{raw; struct{…}}``   same union header
``component : reg_group_c``     baked accessors             ``<group>_c`` class
regular ``component``           ``C_t`` + free fns          ``C_if`` + ``C``
``import`` fn                   extern / vtable ptr         pure virtual
``repeat{}while``, value read   native ``do...while``       native
==============================  ==========================  =====================

Modules
-------

- ``pssc.targets.progseq_tgt`` — the ``ProgSeqTarget`` (``op-model-sv``) target and
  ``--root`` resolution.
- ``pssc.targets.progseq_model`` — language-neutral tree walk + classification
  (``func_kind``, ``comp_kind``, ``walk_tree``) and the shared affine-offset and
  type-collection helpers (``_array_base_stride``, ``collect_reg_groups``,
  ``collect_value_structs``).
- ``pssc.targets.progseq_gen`` — SV package assembly and file emission.
- ``pssc.targets.sv.lower_reg_model`` / ``sv.lower_progseq`` — SV emitters.
- ``pssc.targets.c_progseq_tgt`` / ``cpp_progseq_tgt`` — the C and C++ targets.
- ``pssc.targets.c.c_progseq_gen`` / ``cpp.cpp_progseq_gen`` — header/source
  assembly + core-seam copy.
- ``pssc.targets.c.lower_reg_model`` / ``c.lower_progseq`` — C value unions,
  baked accessors, handle/shim, export functions, and the body emitter.
- ``pssc.targets.cpp.lower_reg_model`` / ``cpp.lower_progseq`` — C++ value unions,
  ``reg<T>`` group classes, the pure-virtual APIs, and the component class.
