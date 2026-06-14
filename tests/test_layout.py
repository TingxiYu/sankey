import pytest
from sankey._layout import auto_x, compute_y, compute_layout


class TestAutoX:
    def test_3_layers(self):
        x = auto_x(3)
        assert x == pytest.approx([0.0, 0.5, 1.0])

    def test_1_layer(self):
        x = auto_x(1)
        assert x == [0.5]

    def test_2_layers(self):
        x = auto_x(2)
        assert x == pytest.approx([0.0, 1.0])


class TestComputeY:
    def test_fixed_gap_3_nodes(self):
        caps = [10.0, 20.0, 30.0]
        y = compute_y(caps, method="fixed_gap", gap=0.05, total_height=1.0)
        assert len(y) == 3
        assert y[0] < y[1] < y[2]  # smallest at top, largest at bottom
        assert all(0 <= yi <= 1 for yi in y)

    def test_fixed_gap_1_node(self):
        y = compute_y([50.0], method="fixed_gap", gap=0.02, total_height=1.0)
        assert len(y) == 1
        assert y[0] == pytest.approx(0.5)

    def test_uniform(self):
        y = compute_y([100.0, 1.0], method="uniform", total_height=1.0)
        assert len(y) == 2
        assert y[0] == pytest.approx(0.25)
        assert y[1] == pytest.approx(0.75)

    def test_proportional(self):
        caps = [50.0, 50.0]
        y = compute_y(caps, method="proportional", total_height=1.0)
        assert len(y) == 2
        assert y[0] == pytest.approx(0.25)
        assert y[1] == pytest.approx(0.75)

    def test_invalid_method_raises(self):
        with pytest.raises(ValueError, match="Unknown method"):
            compute_y([1.0], method="invalid")


class TestComputeLayout:
    def test_returns_xy(self):
        layers = ["L1", "L2", "L3"]
        caps_by_layer = {"L1": [10.0, 20.0], "L2": [30.0], "L3": [10.0, 20.0]}
        x, y = compute_layout(layers, caps_by_layer, x_method="auto", y_method="fixed_gap")
        assert len(x) == 5
        assert len(y) == 5
        assert x[:2] == [0.0, 0.0]
        assert x[2] == 0.5
        assert x[3:] == [1.0, 1.0]

    def test_manual_x(self):
        layers = ["L1", "L2"]
        caps_by_layer = {"L1": [10.0], "L2": [10.0]}
        x, y = compute_layout(
            layers, caps_by_layer,
            x_method={"L1": 0.1, "L2": 0.9},
            y_method="fixed_gap",
        )
        assert x == [0.1, 0.9]
