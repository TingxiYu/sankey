"""Sankey — Publication-quality Sankey diagrams for scientific journals.

Usage:
    from sankeyplot import sankey, load_preset

    # From long-format data
    fig = sankey((edges, nodes), preset="nature")

    # From wide-format data
    fig = sankey(df_wide, layer_cols=["input","h1","outcome"], preset="nature")

    # From capacities
    fig = sankey(capacities_dict, preset="nature")
"""

from __future__ import annotations

from sankeyplot._presets import load_preset, list_presets, register_preset
from sankeyplot._colors import (
    palette_nature,
    palette_cell,
    palette_science,
    palette_lancet,
    palette_colorbrewer,
    palette_viridis,
    palette_batlow,
    palette_custom,
)
from sankeyplot._data import from_wide, from_capacity
from sankeyplot._layout import compute_layout as _compute_layout
from sankeyplot._render import render as _render


def sankey(
    data=None,
    preset: str | dict | None = None,
    *,
    # Color overrides
    main_palette=None,
    input_colors=None,
    residual_color=None,
    outcome_color=None,
    # Layout
    x_method="auto",
    y_method="fixed_gap",
    gap=0.02,
    # Data format
    layer_cols=None,
    layer_pairs=None,
    seed=42,
    # Render
    node_thickness=None,
    node_pad=None,
    font_family=None,
    font_size=None,
    height=700,
    width=2000,
    title=None,
    **layout_kwargs,
):
    if data is None:
        raise ValueError("data is required.")

    # Resolve scheme
    if preset is None:
        scheme = load_preset("nature")
    elif isinstance(preset, str):
        scheme = load_preset(preset)
    else:
        scheme = dict(preset)

    for key, val in [
        ("main_palette", main_palette),
        ("input_colors", input_colors),
        ("residual_color", residual_color),
        ("outcome_color", outcome_color),
    ]:
        if val is not None:
            scheme[key] = val

    # Resolve data
    if isinstance(data, tuple) and len(data) == 2:
        edges, nodes = data
    elif isinstance(data, dict):
        caps = data
        if layer_pairs is None:
            layers = list(caps.keys())
            layer_pairs = list(zip(layers[:-1], layers[1:]))
        nodes, edges = from_capacity(caps, layer_pairs, seed=seed)
    elif hasattr(data, "columns"):
        if layer_cols is None:
            raise ValueError("layer_cols is required for wide-format DataFrames.")
        nodes, edges = from_wide(data, layer_cols)
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")

    # Compute layout
    layers = nodes["layer"].unique().tolist()
    caps_by_layer = {}
    for layer in layers:
        idxs = nodes.index[nodes["layer"] == layer].tolist()
        caps = []
        for idx in idxs:
            outflow = float(edges[edges["source"] == idx]["value"].sum())
            inflow = float(edges[edges["target"] == idx]["value"].sum())
            caps.append(max(outflow, inflow, 1e-6))
        caps_by_layer[layer] = caps

    x, y = _compute_layout(
        layers, caps_by_layer,
        x_method=x_method, y_method=y_method, gap=gap,
    )

    # Render
    return _render(
        nodes, edges, x, y, scheme,
        node_thickness=node_thickness or scheme.get("node_thickness", 12),
        node_pad=node_pad or scheme.get("node_pad", 5),
        font_family=font_family or scheme.get("font_family", "Arial"),
        font_size=font_size or scheme.get("font_size", 18),
        height=height, width=width, title=title,
        **layout_kwargs,
    )
