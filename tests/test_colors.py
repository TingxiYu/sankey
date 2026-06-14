import pytest
import pandas as pd
from sankey._colors import (
    hex_to_rgba, lerp_color,
    palette_nature, palette_cell, palette_science, palette_lancet,
    palette_colorbrewer, palette_viridis, palette_batlow,
    palette_custom,
    gradient_sequential, gradient_diverging, layer_gradient,
    _apply_color_rules, _apply_color_rules_to_df, _eval_match,
)


class TestHexToRgba:
    def test_full_opacity(self):
        assert hex_to_rgba("#FF0000", 1.0) == "rgba(255,0,0,1.0)"

    def test_half_opacity(self):
        assert hex_to_rgba("#0000FF", 0.5) == "rgba(0,0,255,0.5)"

    def test_without_hash(self):
        assert hex_to_rgba("FF0000", 0.3) == "rgba(255,0,0,0.3)"


class TestLerpColor:
    def test_midpoint(self):
        assert lerp_color("#000000", "#FFFFFF", 0.5) == "#7F7F7F"

    def test_start(self):
        assert lerp_color("#000000", "#FFFFFF", 0.0) == "#000000"

    def test_end(self):
        assert lerp_color("#000000", "#FFFFFF", 1.0) == "#FFFFFF"


class TestPalettes:
    def test_nature_returns_hex_list(self):
        p = palette_nature()
        assert len(p) >= 4
        assert all(c.startswith("#") and len(c) == 7 for c in p)

    def test_cell_returns_hex_list(self):
        p = palette_cell()
        assert len(p) >= 4
        assert all(c.startswith("#") and len(c) == 7 for c in p)

    def test_science_returns_hex_list(self):
        p = palette_science()
        assert len(p) >= 4
        assert all(c.startswith("#") and len(c) == 7 for c in p)

    def test_lancet_returns_hex_list(self):
        p = palette_lancet()
        assert len(p) >= 4
        assert all(c.startswith("#") and len(c) == 7 for c in p)

    def test_colorbrewer_valid(self):
        p = palette_colorbrewer("Set1", n=3)
        assert len(p) == 3
        assert all(c.startswith("#") for c in p)

    def test_colorbrewer_unknown(self):
        with pytest.raises(ValueError, match="Unknown ColorBrewer"):
            palette_colorbrewer("NoSuchPalette")

    def test_colorbrewer_too_many(self):
        with pytest.raises(ValueError, match="has only"):
            palette_colorbrewer("Set1", n=999)

    def test_viridis(self):
        p = palette_viridis(5)
        assert len(p) == 5
        assert all(c.startswith("#") for c in p)

    def test_batlow(self):
        p = palette_batlow(5)
        assert len(p) == 5
        assert all(c.startswith("#") for c in p)

    def test_custom_valid(self):
        assert palette_custom(["#FF0000", "#00FF00"]) == ["#FF0000", "#00FF00"]

    def test_custom_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid hex color"):
            palette_custom(["notahex"])

    def test_custom_empty_raises(self):
        with pytest.raises(ValueError, match="at least one color"):
            palette_custom([])


class TestGradients:
    def test_sequential_3_colors(self):
        result = gradient_sequential("#000000", "#FFFFFF", 3)
        assert len(result) == 3
        assert result[0] == "#000000"
        assert result[-1] == "#FFFFFF"

    def test_sequential_1_color(self):
        result = gradient_sequential("#000000", "#FFFFFF", 1)
        assert result == ["#000000"]

    def test_diverging_5_colors(self):
        result = gradient_diverging("#0000FF", "#FFFFFF", "#FF0000", 5)
        assert len(result) == 5
        assert result[0] == "#0000FF"
        assert result[-1] == "#FF0000"

    def test_layer_gradient(self):
        result = layer_gradient("#7B1515", 4, lighten=0.3)
        assert len(result) == 4
        assert all(c.startswith("#") for c in result)


class TestEvalMatch:
    def test_string_residual(self):
        node = {"is_residual": True}
        assert _eval_match("is_residual", node) is True

    def test_string_not_residual(self):
        node = {"is_residual": False}
        assert _eval_match("is_residual", node) is False

    def test_string_layer_equals(self):
        node = {"layer": "Inputs"}
        assert _eval_match("layer == 'Inputs'", node) is True

    def test_string_layer_not_equals(self):
        node = {"layer": "H1"}
        assert _eval_match("layer == 'Inputs'", node) is False

    def test_callable(self):
        node = {"name": "Target"}
        assert _eval_match(lambda n: n["name"] == "Target", node) is True

    def test_callable_false(self):
        node = {"name": "Other"}
        assert _eval_match(lambda n: n["name"] == "Target", node) is False

    def test_is_input(self):
        node = {"is_input": True}
        assert _eval_match("is_input", node) is True

    def test_is_outcome(self):
        node = {"is_outcome": True}
        assert _eval_match("is_outcome", node) is True


class TestApplyColorRules:
    def test_residual_match(self):
        rules = [{"match": "is_residual", "color": "#F0F0F0"}]
        node = {"name": "Res", "layer": "H1", "is_residual": True}
        result = _apply_color_rules(node, rules)
        assert result["color"] == "#F0F0F0"

    def test_callable_match(self):
        rules = [{"match": lambda row: row["name"] == "Special", "color": "#FF0000"}]
        node = {"name": "Special", "layer": "H2", "is_residual": False}
        result = _apply_color_rules(node, rules)
        assert result["color"] == "#FF0000"

    def test_no_match_returns_empty(self):
        rules = [{"match": "is_residual", "color": "#F0F0F0"}]
        node = {"name": "X", "layer": "H1", "is_residual": False}
        result = _apply_color_rules(node, rules)
        assert result == {}

    def test_multiple_rules_first_wins(self):
        rules = [
            {"match": "layer == 'H1'", "color": "#AAA"},
            {"match": "is_residual", "color": "#BBB"},
        ]
        node = {"name": "Res", "layer": "H1", "is_residual": True}
        result = _apply_color_rules(node, rules)
        assert result["color"] == "#AAA"

    def test_applies_link_alpha(self):
        rules = [{"match": "is_residual", "color": "#F0F0F0", "link_alpha": 0.12}]
        node = {"name": "Res", "layer": "H1", "is_residual": True}
        result = _apply_color_rules(node, rules)
        assert result["link_alpha"] == 0.12


class TestApplyColorRulesToDf:
    def test_layer_match_with_palette(self):
        rules = [{"match": "layer == 'Inputs'", "palette": ["#AAA", "#BBB"]}]
        nodes_df = pd.DataFrame({"name": ["A", "B"], "layer": ["Inputs", "Inputs"], "is_residual": [False, False]})
        colors, alphas = _apply_color_rules_to_df(nodes_df, rules, default_color="#888888")
        assert colors == ["#888888", "#888888"]  # palette is a list, not handled by _apply_color_rules_to_df
        assert alphas == [0.22, 0.22]

    def test_default_color_used_when_no_match(self):
        nodes_df = pd.DataFrame({"name": ["X"], "layer": ["H1"], "is_residual": [False]})
        colors, alphas = _apply_color_rules_to_df(nodes_df, [], default_color="#ABC")
        assert colors == ["#ABC"]
        assert alphas == [0.22]
