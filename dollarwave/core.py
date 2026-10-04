"""Public dollarwave objects."""

from .calculate import inflation_calculator


class _GUI:
    """Create the Tk application only when the GUI is launched."""

    @staticmethod
    def run():
        from .calculateGUI import InflationCalculatorApp

        InflationCalculatorApp(inflation_calculator).run()

    def __dir__(self):
        return ["run"]


GUI = _GUI()

__all__ = ["GUI", "inflation_calculator"]
