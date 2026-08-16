pssc Documentation
==================

`pssc` compiles PSS source into SystemVerilog, C, C++ and Python. It bundles the
`zuspec-fe-pss` front end, which translates PSS into Zuspec IR; parsing and AST
construction live in the separate `pssparser` package.

Overview
--------

This package covers:

- loading PSS through `pssparser` and translating parser AST nodes to Zuspec IR
- building runnable Python classes from that IR
- generating scenario code and operation-model programming APIs for the
  supported targets
- the extension surfaces a third party uses to add a target or a style of its
  own, without forking pssc

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api
   pss_to_sv
   progseq
   progseq_design

Markdown guides
---------------

These pages are Markdown and are read from the source tree; they are not part of
the toctree above because this build has no Markdown parser configured.

- ``docs/custom-generator-styles.md`` — adding a style, a backend extension or a
  target of your own
- ``docs/extension-stability.md`` — what the published surfaces promise, and the
  deprecation window
- ``docs/op-model-manifest.md`` — the ``--emit-manifest`` schema
- ``docs/lowering-call-legality.md`` — which PSS calls each target may lower
- ``docs/op-model-c-embedded.md`` — the C operation-model API with no heap
- ``docs/cli.md`` — CLI reference
