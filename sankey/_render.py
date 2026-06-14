from __future__ import annotations

import plotly.graph_objects as go

from sankey._colors import hex_to_rgba, _apply_color_rules
from sankey._typing import Scheme


def _build_node_colors(nodes, scheme: Scheme) -> list[str]:
    colors = []
    residual_color = scheme.get("residual_color", "#F0F0F0")
    outcome_color = scheme.get("outcome_color", "#5A1010")
    input_colors = scheme.get("input_colors", [])
    main_palette = scheme.get("main_palette", [])

    rules = []
    rules.append({"match": "is_residual", "color": residual_color,
                  "link_alpha": scheme.get("residual_link_alpha", 0.12)})
    rules.append({"match": "is_outcome", "color": outcome_color,
                  "link_alpha": scheme.get("outcome_link_alpha", 0.30)})
    if input_colors:
        rules.append({"match": "is_input", "palette": input_colors,
                      "link_alpha": scheme.get("default_link_alpha", 0.22)})

    for _, node in nodes.iterrows():
        result = _apply_color_rules(node, rules)
        color = result.get("color")
        palette = result.get("palette")

        if color is not None:
            colors.append(color)
        elif palette is not None and isinstance(palette, list):
            layer_nodes = nodes[nodes["layer"] == node["layer"]]
            idx = layer_nodes.index.tolist().index(node.name)
            colors.append(palette[idx % len(palette)])
        else:
            layer_nodes = nodes[nodes["layer"] == node["layer"]]
            idx = layer_nodes.index.tolist().index(node.name)
            if main_palette:
                colors.append(main_palette[idx % len(main_palette)])
            else:
                colors.append("#CCCCCC")
    return colors


def _build_link_colors(nodes, edges, node_colors: list[str], scheme: Scheme) -> list[str]:
    residual_link_alpha = scheme.get("residual_link_alpha", 0.12)
    default_link_alpha = scheme.get("default_link_alpha", 0.22)
    outcome_link_alpha = scheme.get("outcome_link_alpha", 0.30)

    link_colors = []
    for _, edge in edges.iterrows():
        si = int(edge["source"])
        ti = int(edge["target"])
        src_is_res = nodes.loc[si, "is_residual"] if si in nodes.index else False
        tgt_is_res = nodes.loc[ti, "is_residual"] if ti in nodes.index else False
        src_is_outcome = nodes.loc[si, "layer"] == "Outcome" if si in nodes.index else False

        if src_is_res or tgt_is_res:
            alpha = residual_link_alpha
            base_color = scheme.get("residual_link_color", "#B0B0B0")
        elif src_is_outcome:
            alpha = outcome_link_alpha
            base_color = node_colors[si] if si < len(node_colors) else "#888888"
        else:
            alpha = default_link_alpha
            base_color = node_colors[si] if si < len(node_colors) else "#888888"

        link_colors.append(hex_to_rgba(base_color, alpha))
    return link_colors


def _mark_special_nodes(nodes):
    nodes = nodes.copy()
    layers = nodes["layer"].unique().tolist()
    nodes["is_input"] = nodes["layer"] == layers[0]
    nodes["is_outcome"] = nodes["layer"] == layers[-1]
    return nodes


def render(
    nodes,
    edges,
    x: list[float],
    y: list[float],
    scheme: Scheme | None = None,
    *,
    node_thickness: int | None = None,
    node_pad: int | None = None,
    font_family: str | None = None,
    font_size: int | None = None,
    height: int = 700,
    width: int = 2000,
    title: str | None = None,
    **layout_kwargs,
) -> go.Figure:
    if scheme is None:
        from sankey._presets import load_preset
        scheme = load_preset("nature")

    if node_thickness is None:
        node_thickness = scheme.get("node_thickness", 12)
    if node_pad is None:
        node_pad = scheme.get("node_pad", 5)
    if font_family is None:
        font_family = scheme.get("font_family", "Arial")
    if font_size is None:
        font_size = scheme.get("font_size", 18)

    nodes = _mark_special_nodes(nodes)
    node_colors = _build_node_colors(nodes, scheme)
    link_colors = _build_link_colors(nodes, edges, node_colors, scheme)

    labels = [str(node["name"]) for _, node in nodes.iterrows()]

    sankey = go.Sankey(
        arrangement="fixed",
        node=dict(
            pad=node_pad,
            thickness=node_thickness,
            line=dict(color="white", width=0.3),
            label=labels,
            color=node_colors,
            x=x,
            y=y,
            hovertemplate="%{label}<br>Flow: %{value:.1f}<extra></extra>",
        ),
        link=dict(
            source=edges["source"].tolist(),
            target=edges["target"].tolist(),
            value=edges["value"].tolist(),
            color=link_colors,
            hovertemplate="%{source.label} -> %{target.label}<br>%{value:.2f}<extra></extra>",
        ),
    )

    fig = go.Figure(sankey)

    layer_order = nodes["layer"].unique().tolist()
    annotations = []
    for i, layer in enumerate(layer_order):
        annotations.append(dict(
            x=i / max(len(layer_order) - 1, 1),
            y=1.06,
            xref="paper",
            yref="paper",
            text=f"<b>{layer}</b>",
            showarrow=False,
            font=dict(size=font_size + 4, color="#111111", family=font_family),
            xanchor="center",
        ))

    fig.update_layout(
        annotations=annotations,
        height=height,
        width=width,
        margin=dict(l=10, r=90, t=60 if title else 55, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family=font_family, size=font_size, color="#2c2c2c"),
        title=title,
        **layout_kwargs,
    )

    return fig
