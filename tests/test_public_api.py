import sys

import dollarwave


def test_public_version():
    assert dollarwave.__version__ == "2.0.7"


def test_import_does_not_construct_gui_or_fetch_cpi_data():
    assert "dollarwave.calculateGUI" not in sys.modules
    assert dollarwave.inflation_calculator._calculator is None
    assert callable(dollarwave.inflation_calculator)
    assert callable(dollarwave.GUI.run)
