API
===

Top-Level Package
=================

The public package entrypoint is `zuspec.fe.pss`.

Primary exports
===============

- `Parser`
- `ParseException`
- `load_pss`
- `load_pss_files`
- `PssTranslationError`
- `AstToIrTranslator`
- `AstToIrContext`
- `IrToRuntimeBuilder`
- `ClassRegistry`

Responsibilities
================

`zuspec-fe-pss` is responsible for:

- obtaining parser ASTs through `pssparser`
- translating parser AST nodes into Zuspec IR
- building executable Python runtime classes from the translated IR

Parser-specific APIs such as grammar coverage, AST structure internals, and the
parser CLI are documented in the sibling `packages/pssparser/docs` tree.

Translation Modules
===================

`zuspec.fe.pss.ast_to_ir`
-------------------------

Contains the AST-to-IR translation pipeline.

Key public types:

- `AstToIrTranslator`
- `AstToIrContext`

`zuspec.fe.pss.ir_to_runtime`
-----------------------------

Contains the IR-to-runtime conversion layer.

Key public types:

- `IrToRuntimeBuilder`
- `ClassRegistry`

Typical Usage
=============

.. code-block:: python

   from zuspec.fe.pss import Parser
   from zuspec.fe.pss.ast_to_ir import AstToIrTranslator
   from zuspec.fe.pss.ir_to_runtime import IrToRuntimeBuilder

   parser = Parser()
   parser.parses([("inline.pss", "struct S { int a; }")])
   root = parser.link()

   ctx = AstToIrTranslator().translate(root)
   runtime = IrToRuntimeBuilder(ctx).build()

Extension API
=============

The surfaces a third-party package writes against to add a target, a style or a
backend extension. The task-shaped guide is
:doc:`custom-generator-styles`; what each surface *promises* is
:doc:`extension-stability`. Everything not listed here is private.

``pssc.targets``
----------------

Target registration and discovery. Entry-point group: ``pssc.targets``.

- ``Target`` — the base contract. Subclasses set ``name``/``description``,
  optionally publish ``target_cfg``, contribute options via ``add_args`` and
  emit via ``run``. ``Target.PSSC_TARGET_API`` versions the contract; a plugin
  carrying a different major is refused at discovery rather than allowed to
  half-work.
- ``register(target, aliases=(), ...)``, ``get(name)``, ``list_targets()``,
  ``discover(force=False)``
- ``plugin_errors()``, ``plugin_error_report()`` — why a plugin did not load. A
  broken plugin costs you that plugin, never the compiler.
- ``NO_PLUGINS_ENV`` (``PSSC_NO_PLUGINS``) — disable all discovery.

``pssc.targets.op_model``
-------------------------

The operation-model family: everything before emission, done once.

- ``OpModel`` — the elaborated model handed to a backend: ``root``, ``tree``,
  ``components`` (children before parents), ``components_root_first``,
  ``reg_groups``, ``value_structs``, ``imports``, ``ctor_names``, ``out_dir``,
  and the accessors ``operations()``, ``ctor()``, ``channels()``,
  ``sub_components()``, ``offset_of()``, ``base_stride_of()``.
- ``OpModelTarget`` — the base class a target subclasses. ``emit()`` is the one
  abstract method; ``derives_from`` inherits an ancestor's call legality, CLI
  options and ``target_cfg``; ``sections()`` opts into differential testing;
  ``core_package``/``core_lang``/``core_file_names()`` ship a runtime;
  ``abi_settings()`` feeds the manifest.

``pssc.targets.style``
----------------------

Style policies (tier A). Entry-point group: ``pssc.styles``, keyed
``"<target>:<name>"``.

- ``StylePolicy`` — the discovery protocol (``name``, ``target``,
  ``description``) plus ``indent()``, ``comment_style()``, ``banner()``
- ``pssc.targets.c.style.CStylePolicy`` — the C policy: ``symbol()``,
  ``type_name()``, ``reg_symbol()``, ``header_name()``, ``include_guard()``,
  ``reg_accessor_form()``, the ``render_reg_*``/``render_mem_*`` hooks,
  ``seam_headers()``, ``include_order()``, ``banner()``
- ``register()``, ``get()``, ``list_styles()``, ``registered_styles()``

``pssc.targets.call_legality``
------------------------------

What a target may lower, and how each call is dispatched.

- ``Entry``, ``Disposition``, ``Ctx``, ``BOTH``/``SOLVE_ONLY``/``TARGET_ONLY``
- ``COMMON`` — the Tier-1 set every target must render
- ``register_extension(target, entries, inherit=None, replace=False)``
- ``classify()``, ``entries_for()``, ``renderable()``, ``registered_targets()``

``pssc.targets.body_walker``
----------------------------

One walk of an operation body; each language renders what it finds.

- ``BodyWalker`` — statement/expression dispatch by node class name
  (``StmtAnnAssign`` → ``stmt_ann_assign``), nesting, comment attachment
- ``CallDispatch`` — routes a call by its ``Disposition``, so the table that
  decides legality and the table that renders are the same table
- ``scan_write_only()``, ``scan_output_locals()`` — the two language-neutral
  analyses

``pssc.targets.reg_layout``
---------------------------

The folded register layout, shared by every backend and by the manifest.

- ``RegAccessor`` — ``path``, ``const_off``, ``strides``, ``access``,
  ``prim_bits``, ``value_bits``, ``value_struct``
- ``collect_accessors(comp_dtype)``, ``is_reserved()``, ``prim_bits()``,
  ``value_bits()``, ``value_struct()``

An address is the one thing in a generated programming API that a golden
snapshot cannot check, so do not recompute one.

``pssc.targets.sections`` and ``pssc.targets.comments``
-------------------------------------------------------

- ``Section``, ``index_of``, ``insert_after``, ``insert_before``, ``replace``,
  ``remove``, ``names`` — assembling and rearranging a generated file
- ``LINE``, ``BLOCK``, ``HASH``, ``comment_lines``, ``append_trailing``

``pssc.targets.overridable``
----------------------------

- ``overridable``, ``overridable_attr`` — mark a member as published surface
- ``surface(cls)``, ``manifest_for(cls)``, ``report(cls)``, ``check_pairs(cls)``

``pssc.targets.manifest``
-------------------------

- ``SCHEMA``, ``VERSION``, ``build(model, target=..., ...)``, ``write(path, doc)``

``pssc.testing``
----------------

The kit for plugin authors, so nobody has to depend on pssc's private fixtures.

- ``compile_op_model(target, ...) -> CompileOutcome``, ``op_model_sources()``,
  ``op_model_root``, ``model_dir()``
- ``assert_common_tier()``, ``assert_deterministic()``
- ``generated_sections()``, ``diff_from_baseline()``,
  ``assert_differs_from_baseline()``
- ``golden_dir_compare()``, ``assert_dirs_match()``
- ``pssc.testing.conformance.run(target)``

``pssc.dvflow.common``
----------------------

- ``run_build(ctxt, input, target=..., ...)`` — the body of a dv-flow build task
- ``register_filetype(ext, filetype, is_incdir=False)``
