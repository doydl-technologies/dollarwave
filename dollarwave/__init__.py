"""Inflation adjustment calculations using historical U.S. CPI data."""

from ._version import __version__
from .calculate import CPIDataError
from .core import GUI, inflation_calculator

__all__ = ["CPIDataError", "GUI", "__version__", "inflation_calculator"]
