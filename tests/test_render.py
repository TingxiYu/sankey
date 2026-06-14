import plotly.graph_objects as go
import pytest
from sankey._render import render
from sankey._presets import load_preset


class TestRender:
    def test_returns_figure(self, sample_nodes, sample_edges):
        x = [0.0, 0.0, 0.5, 0.5, 1.0]
        y = [0.2, 0.6, 0.3, 0.7, 0.5]
        scheme = load_preset("nature")
        fig = render(sample_nodes, sample_edges, x, y, scheme)
        assert isinstance(fig, go.Figure)

    def test_contains_sankey_trace(self, sample_nodes, sample_edges):
        x = [0.0, 0.0, 0.5, 0.5, 1.0]
        y = [0.2, 0.6, 0.3, 0.7, 0.5]
        scheme = load_preset("nature")
        fig = render(sample_nodes, sample_edges, x, y, scheme)
        assert len(fig.data) == 1
        assert fig.data[0].type == "sankey"

    def test_respects_thickness(self, sample_nodes, sample_edges):
        x = [0.0, 0.0, 0.5, 0.5, 1.0]
        y = [0.2, 0.6, 0.3, 0.7, 0.5]
        scheme = load_preset("nature")
        fig = render(sample_nodes, sample_edges, x, y, scheme, node_thickness=20)
        assert fig.data[0].node.thickness == 20

    def test_respects_height_width(self, sample_nodes, sample_edges):
        x = [0.0, 0.0, 0.5, 0.5, 1.0]
        y = [0.2, 0.6, 0.3, 0.7, 0.5]
        scheme = load_preset("nature")
        fig = render(sample_nodes, sample_edges, x, y, scheme, height=500, width=1000)
        assert fig.layout.height == 500
        assert fig.layout.width == 1000

    def test_residual_nodes_get_residual_color(self, sample_nodes, sample_edges):
        nodes = sample_nodes.copy()
        nodes.loc[nodes["name"] == "X", "is_residual"] = True
        x = [0.0, 0.0, 0.5, 0.5, 1.0]
        y = [0.2, 0.6, 0.3, 0.7, 0.5]
        scheme = load_preset("nature")
        fig = render(nodes, sample_edges, x, y, scheme)
        colors = fig.data[0].node.color
        x_idx = nodes[nodes["name"] == "X"].index[0]
        assert colors[x_idx] == scheme["residual_color"]

    def test_generates_annotations(self, sample_nodes, sample_edges):
        x = [0.0, 0.0, 0.5, 0.5, 1.0]
        y = [0.2, 0.6, 0.3, 0.7, 0.5]
        scheme = load_preset("nature")
        fig = render(sample_nodes, sample_edges, x, y, scheme)
        assert len(fig.layout.annotations) >= 3
