import pandas as pd
import pytest
from sankey._data import from_wide, from_capacity, validate_conservation, validate_no_cycles


class TestFromWide:
    def test_basic_conversion(self, sample_wide_df):
        nodes, edges = from_wide(
            sample_wide_df,
            layer_cols=["input", "h1", "outcome"],
        )
        assert len(nodes) == 5  # A, B, X, Y, O
        assert set(nodes["name"]) == {"A", "B", "X", "Y", "O"}
        assert nodes.loc[nodes["name"] == "A", "layer"].iloc[0] == "input"
        assert nodes.loc[nodes["name"] == "O", "layer"].iloc[0] == "outcome"

    def test_node_count_correct(self, sample_wide_df):
        nodes, edges = from_wide(
            sample_wide_df,
            layer_cols=["input", "h1", "outcome"],
        )
        a_idx = nodes[nodes["name"] == "A"].index[0]
        b_idx = nodes[nodes["name"] == "B"].index[0]
        a_out = edges[edges["source"] == a_idx]["value"].sum()
        b_out = edges[edges["source"] == b_idx]["value"].sum()
        assert a_out == 2.0
        assert b_out == 3.0

    def test_residual_detection(self):
        df = pd.DataFrame({
            "in": ["X", "Y"],
            "out": ["Z", "Residual"],
        })
        nodes, edges = from_wide(df, layer_cols=["in", "out"])
        res_node = nodes[nodes["name"] == "Residual"]
        assert res_node["is_residual"].iloc[0] == True

    def test_preserves_layer_order(self, sample_wide_df):
        nodes, edges = from_wide(
            sample_wide_df,
            layer_cols=["input", "h1", "outcome"],
        )
        layers = nodes["layer"].unique().tolist()
        assert layers == ["input", "h1", "outcome"]


class TestFromCapacity:
    def test_generates_correct_node_count(self):
        caps = {
            "Inputs": [60.0, 40.0],
            "H1": [50.0, 50.0],
            "Outcome": [100.0],
        }
        pairs = [("Inputs", "H1"), ("H1", "Outcome")]
        nodes, edges = from_capacity(caps, pairs, seed=0)
        assert len(nodes) == 5  # 2 + 2 + 1

    def test_flow_conservation(self):
        caps = {
            "A": [100.0],
            "B": [30.0, 70.0],
            "C": [100.0],
        }
        pairs = [("A", "B"), ("B", "C")]
        nodes, edges = from_capacity(caps, pairs, seed=0)
        # Check total flow through middle layer matches
        b_idxs = nodes[nodes["layer"] == "B"].index.tolist()
        inflow = edges[edges["target"].isin(b_idxs)]["value"].sum()
        outflow = edges[edges["source"].isin(b_idxs)]["value"].sum()
        assert abs(inflow - 100.0) < 0.01
        assert abs(outflow - 100.0) < 0.01


class TestValidateConservation:
    def test_conserved_flow_passes(self, sample_nodes, sample_edges):
        errors = validate_conservation(sample_edges, sample_nodes)
        assert errors["max_row_err"] < 1e-10
        assert errors["max_col_err"] < 1e-10


class TestValidateNoCycles:
    def test_dag_passes(self, sample_edges):
        validate_no_cycles(sample_edges)  # should not raise

    def test_self_loop_raises(self):
        edges = pd.DataFrame({"source": [0], "target": [0], "value": [1.0]})
        with pytest.raises(ValueError, match="self-loop"):
            validate_no_cycles(edges)
