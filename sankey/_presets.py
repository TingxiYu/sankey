from __future__ import annotations

from sankey._typing import PresetRegistry, Scheme

PRESETS: PresetRegistry = {
    "nature": {
        "main_palette":        ["#7B1515", "#B54848", "#D4956A", "#8BBDD4", "#4A6FAF", "#C4A35A"],
        "gradient_method":     "sequential",
        "gradient_lighten":    0.6,
        "input_colors":        ["#D4956A", "#8BBDD4", "#4A6FAF"],
        "residual_color":      "#F0F0F0",
        "residual_link_alpha": 0.38,
        "residual_link_color": "#bfbfbf",
        "outcome_color":       "#5A1010",
        "outcome_link_alpha":  0.35,
        "default_link_alpha":  0.18,
        "font_family":         "Arial",
        "font_size":           18,
        "node_thickness":      25,
        "node_pad":            80,
    },
    "cell": {
        "main_palette":        ["#1B6CA8", "#3DA5D9", "#73BFB8", "#9ED9CC", "#F4A261", "#E76F51"],
        "gradient_method":     "sequential",
        "gradient_lighten":    0.55,
        "input_colors":        ["#1B6CA8", "#73BFB8", "#E76F51"],
        "residual_color":      "#EAEAEA",
        "residual_link_alpha": 0.38,
        "residual_link_color": "#bfbfbf",
        "outcome_color":       "#0D4F8B",
        "outcome_link_alpha":  0.35,
        "default_link_alpha":  0.18,
        "font_family":         "Helvetica",
        "font_size":           18,
        "node_thickness":      25,
        "node_pad":            80,
    },
    "science": {
        "main_palette":        ["#D32F2F", "#1976D2", "#757575", "#FFA000", "#388E3C", "#7B1FA2"],
        "gradient_method":     "sequential",
        "gradient_lighten":    0.50,
        "input_colors":        ["#D32F2F", "#1976D2", "#FFA000"],
        "residual_color":      "#EEEEEE",
        "residual_link_alpha": 0.38,
        "residual_link_color": "#bfbfbf",
        "outcome_color":       "#212121",
        "outcome_link_alpha":  0.35,
        "default_link_alpha":  0.18,
        "font_family":         "Helvetica",
        "font_size":           18,
        "node_thickness":      25,
        "node_pad":            80,
    },
}


def load_preset(name: str, **overrides) -> Scheme:
    if name not in PRESETS:
        valid = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Valid: {valid}")
    base = dict(PRESETS[name])
    base.update(overrides)
    return base


def list_presets() -> list[str]:
    return sorted(PRESETS.keys())


def register_preset(name: str, config: Scheme) -> None:
    PRESETS[name] = config
