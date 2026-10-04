"""Consumer Price Index retrieval and inflation calculations."""

from copy import deepcopy
from html.parser import HTMLParser
import time

import pandas as pd
import requests


CPI_DATA_URL = (
    "https://www.usinflationcalculator.com/inflation/"
    "consumer-price-index-and-annual-percent-changes-from-1913-to-2008/"
)
DEFAULT_TIMEOUT = 20
REQUIRED_COLUMNS = (
    "Year",
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
    "Avg",
)


class CPIDataError(RuntimeError):
    """Raised when CPI data cannot be downloaded or validated."""


class CPIHTMLTableParser(HTMLParser):
    """Extract the annual U.S. CPI table from an HTML document."""

    def __init__(self, url=CPI_DATA_URL, timeout=DEFAULT_TIMEOUT, session=None):
        super().__init__()
        self.url = url
        self.timeout = timeout
        self.session = session or requests.Session()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.table_data = []
        self.current_row = []
        self.current_cell = ""
        self.data_frame = None
        self.request_successful = False
        self.data_fetched = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag in {"td", "th"} and self.in_row:
            self.in_cell = True
            self.current_cell = ""

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.in_row and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
            self.current_cell = ""
        elif tag == "tr" and self.in_table:
            self.in_row = False
            if self.current_row:
                self.table_data.append(self.current_row)
        elif tag == "table":
            self.in_table = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data

    def fetch_data(self):
        """Download, parse, and return the CPI table."""
        if self.data_fetched:
            return self.data_frame

        try:
            response = self.session.get(
                self.url,
                timeout=self.timeout,
                headers={"User-Agent": "dollarwave/2.0.7"},
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            self.request_successful = False
            raise CPIDataError("Unable to download CPI data.") from exc

        self.request_successful = True
        return self.parse_data(response.text)

    def parse_data(self, html):
        """Parse and validate CPI data from an HTML string."""
        self.table_data = []
        self.data_frame = None
        self.data_fetched = False
        self.reset()
        self.feed(html)
        self.create_data_frame()
        self.validate_data_frame()
        return self.data_frame

    def create_data_frame(self):
        """Convert the table containing CPI headings into a DataFrame."""
        header_index = None
        for index, row in enumerate(self.table_data):
            if all(column in row for column in REQUIRED_COLUMNS):
                header_index = index
                break

        if header_index is None:
            raise CPIDataError("The CPI table header was not found in the response.")

        columns = self.table_data[header_index]
        rows = []
        for row in self.table_data[header_index + 1 :]:
            if len(row) >= len(columns) and row[0].strip().isdigit():
                rows.append(row[: len(columns)])

        if not rows:
            raise CPIDataError("The CPI table did not contain any annual data rows.")

        self.data_frame = pd.DataFrame(rows, columns=columns)
        self.data_frame = self.data_frame.drop(
            columns=["Dec-Dec", "Avg-Avg"], errors="ignore"
        )

    def validate_data_frame(self):
        """Validate the expected columns and the freshness of the CPI data."""
        if self.data_frame is None or not all(
            column in self.data_frame.columns for column in REQUIRED_COLUMNS
        ):
            raise CPIDataError("The CPI table is missing one or more required columns.")

        years = pd.to_numeric(self.data_frame["Year"], errors="coerce").dropna()
        if years.empty:
            raise CPIDataError("The CPI table does not contain valid years.")

        latest_year = int(years.max())
        if latest_year < time.localtime().tm_year - 1:
            raise CPIDataError(
                f"The downloaded CPI table is stale; its latest year is {latest_year}."
            )

        self.data_fetched = True

    def get_data_frame(self):
        """Return the most recently parsed CPI DataFrame."""
        return self.data_frame


class CPIDataTool:
    """Prepare and query annual and monthly CPI values."""

    def __init__(self, dataframe):
        if dataframe is None or dataframe.empty:
            raise CPIDataError("A non-empty CPI DataFrame is required.")

        self.df = deepcopy(dataframe)
        self.current_month = time.strftime("%B")
        self.current_year = time.localtime().tm_year
        self.month_map = {
            "January": "Jan",
            "February": "Feb",
            "March": "Mar",
            "April": "Apr",
            "May": "May",
            "June": "June",
            "July": "July",
            "August": "Aug",
            "September": "Sep",
            "October": "Oct",
            "November": "Nov",
            "December": "Dec",
        }
        self.convert_columns_to_float()
        self.calculate_avg_for_nan()
        self.set_year_as_index()
        self.min = self.df.index.min()
        self.max = self.df.index.max()

    def validate_year(self, year, comparison_year):
        """Validate that two distinct years are available in the dataset."""
        if int(year) == int(comparison_year):
            raise ValueError("The given year and comparison year cannot be the same.")
        if int(year) < int(self.min) or int(year) > int(self.max):
            raise ValueError(
                f"The given year {year} is out of the allowable range "
                f"({self.min} to {self.max})."
            )
        if int(comparison_year) < int(self.min) or int(comparison_year) > int(self.max):
            raise ValueError(
                f"The comparison year {comparison_year} is out of the allowable "
                f"range ({self.min} to {self.max})."
            )

    def convert_columns_to_float(self):
        """Convert CPI columns to floats and invalid cells to NaN."""
        numeric_columns = [column for column in self.df.columns if column != "Year"]
        self.df[numeric_columns] = self.df[numeric_columns].apply(
            pd.to_numeric, errors="coerce"
        )

    def calculate_avg_for_nan(self):
        """Fill missing annual averages from the available monthly values."""
        for index, row in self.df.iterrows():
            if pd.isna(row["Avg"]):
                values = row[list(REQUIRED_COLUMNS[1:13])].dropna().astype(float)
                if not values.empty:
                    self.df.at[index, "Avg"] = values.mean()

    def set_year_as_index(self):
        """Use the year string as the DataFrame index."""
        self.df["Year"] = self.df["Year"].astype(str)
        self.df.set_index("Year", inplace=True)

    def get_value(self, year, column):
        """Return the CPI value for one year and column."""
        column = self.month_map.get(column, column)
        return self.df.at[str(year), column]

    def get_month_values(
        self,
        year,
        comparison_year=None,
        print_message=True,
        month=None,
        override_validation=False,
    ):
        """Return one monthly CPI value for each of two years."""
        comparison_year = str(comparison_year or self.current_year)
        if not override_validation:
            self.validate_year(str(year), comparison_year)

        month = month.capitalize() if month else self.current_month
        month_abbreviation = self.month_map.get(month, month)
        first_value = self.get_value(year, month_abbreviation)
        second_value = self.get_value(comparison_year, month_abbreviation)

        if pd.isna(second_value):
            if print_message:
                print(
                    "Switching to annual averages because "
                    f"{month} CPI is not available for {comparison_year}."
                )
            return self.get_avg_values(
                year, comparison_year, month_abbreviation, override_validation
            )

        return pd.DataFrame(
            {str(year): [first_value], comparison_year: [second_value]},
            index=[month],
        )

    def get_avg_values(
        self,
        year,
        comparison_year=None,
        month=None,
        override_validation=False,
    ):
        """Return annual average CPI values for two years."""
        comparison_year = str(comparison_year or self.current_year)
        if not override_validation:
            self.validate_year(str(year), comparison_year)

        label = month.capitalize() if month else "Avg"
        return pd.DataFrame(
            {
                str(year): [self.get_value(year, "Avg")],
                comparison_year: [self.get_value(comparison_year, "Avg")],
            },
            index=[label],
        )


class Fail:
    """Represent an unavailable CPI dataset for backward compatibility."""

    def __init__(self, message=None):
        self.message = message

    def print_message(self):
        """Print the stored failure message."""
        print(self.message)


class InflationCalculator:
    """Calculate inflation-adjusted values from prepared CPI data."""

    def __init__(self, cpi_data_tool):
        if isinstance(cpi_data_tool, Fail):
            self.cpi_data_tool = None
            self.is_available = False
            return
        if not isinstance(cpi_data_tool, CPIDataTool):
            raise TypeError("cpi_data_tool must be an instance of CPIDataTool")
        self.cpi_data_tool = cpi_data_tool
        self.is_available = True

    def __call__(self, amount, original_year, target_year):
        return self.adjusted_value(amount, original_year, target_year)

    def adjusted_value(self, amount, original_year, target_year):
        """Return an amount adjusted between two annual CPI values."""
        if not self.is_available:
            print("Inflation calculation is unavailable.")
            return None

        cpi_values = self.cpi_data_tool.get_avg_values(original_year, target_year)
        cpi_original = cpi_values.iloc[0][str(original_year)]
        cpi_target = cpi_values.iloc[0][str(target_year)]
        adjusted = round(amount * (cpi_target / cpi_original), 2)
        print(
            f"${amount} from {original_year} is equivalent to "
            f"${adjusted:.2f} in {target_year} dollars."
        )
        return adjusted

    def comparison(self, amount, n_years, plot=False):
        """Compare an amount over a range ending in the current year."""
        if not self.is_available:
            print("Historical value calculation is unavailable.")
            return None

        current_year = int(self.cpi_data_tool.current_year)
        start_year = current_year - n_years
        if start_year < int(self.cpi_data_tool.min) or current_year > int(
            self.cpi_data_tool.max
        ):
            raise ValueError(
                "Data for the requested range is unavailable. The available "
                f"range is {self.cpi_data_tool.min} to {self.cpi_data_tool.max}."
            )

        cpi_current = self.cpi_data_tool.get_avg_values(
            current_year, override_validation=True
        ).iloc[0, 0]
        historical_values = {}
        for year in range(start_year, current_year):
            cpi_year = self.cpi_data_tool.get_avg_values(
                year, override_validation=True
            ).iloc[0, 0]
            historical_values[year] = round(amount * (cpi_year / cpi_current), 2)

        for year, value in historical_values.items():
            print(
                f"${amount} from {year} is equivalent to "
                f"${value:.2f} in {current_year} dollars."
            )

        if plot:
            self._plot_comparison(amount, start_year, current_year, historical_values)
        return historical_values

    def current_year_change(self, amount, plot=False):
        """Compare an amount across available months in the current year."""
        if not self.is_available:
            print("Current-year CPI calculation is unavailable.")
            return None

        current_year = str(self.cpi_data_tool.current_year)
        month_values = self.cpi_data_tool.df.loc[current_year]
        results = {}
        for month, cpi in month_values.items():
            if month == "Avg" or pd.isna(cpi):
                continue
            month_name = next(
                (
                    name
                    for name, abbreviation in self.cpi_data_tool.month_map.items()
                    if abbreviation == month
                ),
                month,
            )
            results[month_name] = round(amount * (cpi / month_values["Avg"]), 2)

        if plot:
            self._plot_current_year(amount, current_year, results)
        return results

    @staticmethod
    def _plot_comparison(amount, start_year, current_year, values):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 5))
        plt.plot(list(values), list(values.values()), marker="o")
        plt.title(
            f"Inflation Adjusted Value of ${amount} Over Time "
            f"({start_year}-{current_year})"
        )
        plt.xlabel("Year")
        plt.ylabel(f"Equivalent Value in {current_year} Dollars")
        plt.grid(True)
        plt.xticks(list(values), rotation=45)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def _plot_current_year(amount, current_year, values):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 5))
        plt.plot(list(values), list(values.values()), marker="o")
        plt.title(f"Value of ${amount} by Monthly CPI in {current_year}")
        plt.xlabel("Month")
        plt.ylabel("Adjusted Value ($)")
        plt.grid(True)
        plt.show()

    def __dir__(self):
        return ["adjusted_value", "comparison", "current_year_change"]


class LazyInflationCalculator:
    """Load remote CPI data only when a calculation is requested."""

    def __init__(self, loader=None):
        self._loader = loader or self._default_loader
        self._calculator = None

    @staticmethod
    def _default_loader():
        parser = CPIHTMLTableParser()
        return InflationCalculator(CPIDataTool(parser.fetch_data()))

    def _get_calculator(self):
        if self._calculator is None:
            self._calculator = self._loader()
        return self._calculator

    @property
    def is_available(self):
        try:
            self._get_calculator()
        except CPIDataError:
            return False
        return True

    @property
    def cpi_data_tool(self):
        return self._get_calculator().cpi_data_tool

    def __call__(self, amount, original_year, target_year):
        return self._get_calculator()(amount, original_year, target_year)

    def adjusted_value(self, amount, original_year, target_year):
        return self._get_calculator().adjusted_value(amount, original_year, target_year)

    def comparison(self, amount, n_years, plot=False):
        return self._get_calculator().comparison(amount, n_years, plot)

    def current_year_change(self, amount, plot=False):
        return self._get_calculator().current_year_change(amount, plot)

    def __dir__(self):
        return ["adjusted_value", "comparison", "current_year_change"]


def create_cpi_tool(dataframe):
    """Create a CPI data tool from a DataFrame."""
    if dataframe is None:
        return Fail("DataFrame cannot be None. Provide valid CPI data.")
    return CPIDataTool(dataframe)


inflation_calculator = LazyInflationCalculator()

__all__ = [
    "CPIDataError",
    "CPIDataTool",
    "CPIHTMLTableParser",
    "Fail",
    "InflationCalculator",
    "LazyInflationCalculator",
    "inflation_calculator",
]
