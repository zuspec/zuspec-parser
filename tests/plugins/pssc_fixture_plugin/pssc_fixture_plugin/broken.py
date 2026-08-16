"""An entry point that fails on import.

The realistic shape of a broken plugin: not a syntax error in the plugin
itself, but a dependency that is not there. pssc must record it, name it, and
carry on with every other target.
"""
raise ImportError("no module named 'the_vendor_sdk' (pssc-fixture-plugin)")
