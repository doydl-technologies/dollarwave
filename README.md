<p align="center">
  <img src="https://raw.githubusercontent.com/doydl-technologies/dollarwave/main/dollarwave/assets/py_dollarwave_logo.png" alt="dollarwave logo" width="700">
</p>

### Dollarwave Library: Inflation Adjustment Using CPI Data

# ⚠️ Dollarwave Library - DEPRECATED

**This library is no longer maintained. Please use [quantsumore](https://pypi.org/project/quantsumore) instead.**

The `quantsumore` library provides the same core functionality as `dollarwave`, with enhancements and active development. This guide will show you how to migrate your code to the new library.

---

## Migrating to `quantsumore`

### Inflation Adjustment Example in `quantsumore`

If you used the `inflation_calculator` in `dollarwave`, here’s how to achieve the same with `quantsumore`:

```bash
pip install quantsumore
```

```python
from quantsumore.api import cpi

# Create an instance of the inflation adjustment tool
cpi_instance = cpi.CPI_U.InflationAdjustment

# Calculate the adjusted value
original_amount = 1
original_year = 1970
target_year = 2024
adjusted_amount = cpi_instance.select(original_amount, original_year, target_year)
print(f"${original_amount} from {original_year} is equivalent to ${adjusted_amount:.2f} in {target_year} dollars.")
```
Output:
```
$1 from 1970 is equivalent to $8.04 in 2024 dollars.
```

### Using the GUI in `quantsumore`

If you used the graphical user interface (GUI) in `dollarwave`, here's how to use it in `quantsumore`:

```python
from quantsumore.gui import GUI

# Run the inflation calculator GUI
GUI.run()
```

---

## ⚠️ Original Dollarwave Documentation (Deprecated)

The following examples are for `dollarwave`, but it is recommended to use `quantsumore` as shown above.

### Dollarwave Library: Inflation Adjustment Using CPI Data

The `dollarwave` module is a comprehensive library designed for adjusting the value of money across different years using Consumer Price Index (CPI) data. It offers extensive capabilities to handle and process CPI data, ensuring accurate inflation adjustments.

### Why dollarwave? (Deprecated)

- **Accurate Inflation Adjustments**: Utilizes CPI data to calculate the equivalent value of money across different years.
- **Easy to Use**: Provides a straightforward API for calculating inflation-adjusted values.
- **Data Validation**: Ensures the accuracy and consistency of CPI data used in calculations.

## Usage Examples (Deprecated)

### Calculating Inflation-Adjusted Values (Deprecated)

Use the `inflation_calculator` to calculate the equivalent value of money across different years:

```python
from dollarwave import inflation_calculator

# Calculate the adjusted value
original_amount = 1
original_year = 1970
target_year = 2024
adjusted_amount = inflation_calculator(original_amount, original_year, target_year)
```
Output:
```
$1 from 1970 is equivalent to $8.04 in 2024 dollars.
```

### Using the GUI (Deprecated)

You can also use the graphical user interface (GUI) to perform inflation calculations:

```python
from dollarwave import GUI

# Run the GUI
GUI.run()
```

#### GUI Screenshots (Deprecated)

Here are some screenshots of the GUI in action:

- **Adjusted Value Tab**

![Adjusted Value Tab](https://github.com/doydl-technologies/dollarwave/blob/main/dollarwave/assets/adjusted_value_gui_img.png)

- **Current Year Change Tab**

![Current Year Change Tab](https://github.com/doydl-technologies/dollarwave/blob/main/dollarwave/assets/current_year_change_gui_img.png)

---

## Installation (Use quantsumore instead)

To install the **deprecated** `dollarwave` library, use pip:

```bash
pip install dollarwave
```

However, it is strongly recommended to use the new `quantsumore` library:

```bash
pip install quantsumore
```

## Contributing

Contributions are welcome for `quantsumore`, but `dollarwave` is no longer maintained. Please read the [contribution guidelines](CONTRIBUTING.md) for details on contributing to `quantsumore`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
