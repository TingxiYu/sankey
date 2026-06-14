import plotly.graph_objects as go
from sankey import sankey


def test_full_pipeline_from_capacities():
    caps = {
        "Inputs":  [60.0, 40.0],
        "H1":      [30.0, 30.0, 40.0],
        "Outcome": [100.0],
    }
    fig = sankey(caps, preset="nature", seed=0)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "sankey"
    assert len(fig.data[0].node.x) == 6


def test_full_pipeline_from_wide():
    import pandas as pd
    df = pd.DataFrame({
        "in": ["A", "A", "B", "B", "B"],
        "mid": ["X", "Y", "X", "Y", "X"],
        "out": ["Z", "Z", "Z", "Z", "Z"],
    })
    fig = sankey(df, layer_cols=["in", "mid", "out"], preset="cell")
    assert isinstance(fig, go.Figure)
    assert fig.data[0].type == "sankey"


def test_full_pipeline_from_long():
    import pandas as pd
    nodes = pd.DataFrame({
        "name": ["A", "B", "C"],
        "layer": ["L1", "L1", "L2"],
        "is_residual": [False, False, False],
    })
    edges = pd.DataFrame({
        "source": [0, 1],
        "target": [2, 2],
        "value":  [5.0, 5.0],
    })
    fig = sankey((edges, nodes), preset="science")
    assert isinstance(fig, go.Figure)


def test_preset_override():
    caps = {"A": [10.0], "B": [10.0]}
    fig = sankey(caps, preset="nature", residual_color="#123456", height=999)
    assert fig.layout.height == 999
