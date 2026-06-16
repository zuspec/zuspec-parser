
# Codex
You must prefix all commands with 'direnv exec . <command>' to get
a proper environment. (If direnv is not approved, the vendored venv at
`packages/python/` can be used directly with `PYTHONPATH=./src`.)

# Package

This is **pssc** (the PSS compiler), import root `pssc`, source under `src/pssc/`.
It was previously `zuspec-fe-pss` (import root `zuspec.fe.pss`); see
`docs/migration-from-zuspec-fe-pss.md` for the import map.

# Build and run

Focus on Python and unit tests for now.

```
direnv exec . pytest tests/unit          # fast unit suite (pytest.ini default)
direnv exec . pssc --version             # console entry point
```

Do not make assumptions about the number of cores. Use what is available.

## Changing the AST
Schema for the AST is in `ast`. It is processed by `packages/pyastbuilder`.
This schema defines the data model created by parsing PSS code.
Any time an AST file is changed, the environment must be built from
scratch by removing the build directory and re-running cmake+make.
(The pssc migration itself touches only Python — no AST/cmake rebuild needed.)
