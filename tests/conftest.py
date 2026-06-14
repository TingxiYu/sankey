import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_wide_df():
    """Minimal wide-format data: 2 inputs to 2 H1 to 1 outcome."""
    return pd.DataFrame({
        "input":  ["A", "A", "B", "B", "B"],
        "h1":     ["X", "Y", "X", "Y", "X"],
        "outcome":["O", "O", "O", "O", "O"],
    })


@pytest.fixture
def sample_capacities():
    return {
        "Inputs": [60.0, 40.0],
        "H1":     [50.0, 50.0],
        "Outcome":[100.0],
    }


@pytest.fixture
def sample_nodes():
    return pd.DataFrame({
        "name":        ["A", "B", "X", "Y", "O"],
        "layer":       ["Inputs", "Inputs", "H1", "H1", "Outcome"],
        "is_residual": [False, False, False, False, False],
    })


@pytest.fixture
def sample_edges():
    return pd.DataFrame({
        "source": [0, 0, 1, 1],
        "target": [2, 3, 2, 3],
        "value":  [30.0, 30.0, 20.0, 20.0],
    })
