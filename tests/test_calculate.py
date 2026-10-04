import time

import pandas as pd
import pytest

from dollarwave.calculate import (
    CPIDataError,
    CPIDataTool,
    CPIHTMLTableParser,
    Fail,
    InflationCalculator,
    LazyInflationCalculator,
    create_cpi_tool,
)


MONTH_COLUMNS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "June",
    "July",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def make_frame():
    current_year = time.localtime().tm_year
    rows = []
    for year, average in (
        (current_year - 2, 100.0),
        (current_year - 1, 110.0),
        (current_year, 120.0),
    ):
        row = {"Year": str(year), "Avg": average}
        row.update({month: average for month in MONTH_COLUMNS})
        rows.append(row)
    return pd.DataFrame(rows)


def make_html():
    frame = make_frame()
    headings = "".join(f"<th>{column}</th>" for column in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = "".join(f"<td>{value}</td>" for value in row)
        rows.append(f"<tr>{cells}</tr>")
    return f"<html><table><tr>{headings}</tr>{''.join(rows)}</table></html>"


def test_html_parser_extracts_expected_table():
    parser = CPIHTMLTableParser()
    result = parser.parse_data(make_html())

    assert list(result["Year"]) == [
        str(time.localtime().tm_year - 2),
        str(time.localtime().tm_year - 1),
        str(time.localtime().tm_year),
    ]
    assert parser.data_fetched is True


def test_html_parser_rejects_missing_cpi_table():
    with pytest.raises(CPIDataError, match="header"):
        CPIHTMLTableParser().parse_data("<html><p>No table here.</p></html>")


def test_adjusted_value_uses_annual_averages(capsys):
    calculator = InflationCalculator(CPIDataTool(make_frame()))
    current_year = time.localtime().tm_year

    result = calculator(10, current_year - 2, current_year)

    assert result == pytest.approx(12.0)
    assert "is equivalent to $12.00" in capsys.readouterr().out


def test_lazy_calculator_loads_once():
    calls = []

    def loader():
        calls.append(True)
        return InflationCalculator(CPIDataTool(make_frame()))

    calculator = LazyInflationCalculator(loader)
    current_year = time.localtime().tm_year

    assert calculator._calculator is None
    assert calculator(10, current_year - 2, current_year) == pytest.approx(12.0)
    assert calculator.adjusted_value(
        10, current_year - 2, current_year - 1
    ) == pytest.approx(11.0)
    assert len(calls) == 1


def test_current_year_change_uses_available_months():
    tool = CPIDataTool(make_frame())
    calculator = InflationCalculator(tool)

    result = calculator.current_year_change(10)

    assert result["January"] == pytest.approx(10.0)
    assert len(result) == 12


def test_legacy_failure_object_remains_supported(capsys):
    failure = create_cpi_tool(None)
    calculator = InflationCalculator(failure)

    assert isinstance(failure, Fail)
    assert calculator(10, 2000, 2020) is None
    assert "unavailable" in capsys.readouterr().out
