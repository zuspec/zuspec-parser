"""DV Flow Manager (DFM) integration for ``pssc``.

Exposes ``pssc`` as a DFM task package (loaded via the ``dv_flow.mgr`` entry
point ``pssc.dvflow.__ext__``):

  * **Reference tasks** (:mod:`pssc.dvflow.reference`) emit ``std.FileSet``
    datasets for the shared SV/C/C++ core source that ``pssc`` bundles.
  * **Build tasks** (:mod:`pssc.dvflow.build`) consume PSS source filesets and
    run one ``pssc`` output style each, emitting correctly-typed filesets.

``dv-flow-mgr`` is a regular ``pssc`` dependency, so the package is always
registered. The Python task bodies still import :mod:`dv_flow.mgr` lazily (and
:mod:`pssc.dvflow.__ext__` stays import-free) to keep package discovery cheap
and importing core ``pssc`` light.
"""
