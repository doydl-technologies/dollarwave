# Contributing

Focused bug fixes, compatibility updates, documentation improvements, and
data-source maintenance are welcome. Please avoid broad API redesigns because
`dollarwave` is maintained primarily for existing users.

## Development setup

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pytest -q
```

Before opening a pull request, run the tests and verify both distributions:

```bash
python -m build
python -m twine check dist/*
```

Tests must not depend on live network access. Use a small HTML fixture or an
in-memory DataFrame when changing CPI parsing or calculation behavior.
