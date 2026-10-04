<p align="center">
  <img src="https://raw.githubusercontent.com/doydl-technologies/dollarwave/main/dollarwave/assets/py_dollarwave_logo.png" alt="dollarwave logo" width="700">
</p>

# dollarwave

`dollarwave` converts monetary amounts between years using historical U.S.
Consumer Price Index (CPI) values. It includes a small Python API, historical
comparison helpers, optional charts, and a Tk desktop interface.

## Project status

The project is maintained in stability mode. Existing behavior and compatibility
remain the priority; focused fixes, packaging updates, and data-source maintenance
are welcome. The package is no longer marked as deprecated.

## Installation

```bash
python -m pip install dollarwave
```

Python 3.8 through 3.14 are supported. The package is pure Python and supports
Windows, macOS, and Linux. The desktop interface requires a Python installation
with Tk support.

## Quick start

```python
from dollarwave import inflation_calculator

adjusted_amount = inflation_calculator(
    amount=1,
    original_year=1970,
    target_year=2024,
)
```

The calculation returns a rounded `float` and prints a readable result:

```text
$1 from 1970 is equivalent to $8.08 in 2024 dollars.
```

The exact result can change when the upstream CPI table is revised.

### Historical comparison

```python
values = inflation_calculator.comparison(
    amount=10,
    n_years=5,
    plot=False,
)
```

Set `plot=True` to display the result with Matplotlib.

### Current-year monthly change

```python
values = inflation_calculator.current_year_change(amount=10, plot=False)
```

### Desktop interface

```python
from dollarwave import GUI

GUI.run()
```

## Data and network behavior

The first calculation in a process downloads the public CPI table used by the
library. Importing `dollarwave` does not make a network request. The parsed data
is cached in memory for later calculations in that process. A clear
`CPIDataError` is raised if the source cannot be reached or its table no longer
has the expected structure.

`dollarwave` is intended for general-purpose calculations, not accounting,
investment, tax, or legal advice.

## Development

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pytest -q
python -m build
python -m twine check dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution details and
[SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## License

`dollarwave` is available under the [MIT License](LICENSE).
