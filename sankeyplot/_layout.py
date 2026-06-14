from __future__ import annotations

import numpy as np


# ── X coordinates ───────────────────────────────────────

def auto_x(n_layers: int) -> list[float]:
    if n_layers == 1:
        return [0.5]
    return [i / (n_layers - 1) for i in range(n_layers)]


# ── Y coordinates ───────────────────────────────────────

def compute_y(
    caps: list[float],
    method: str = "fixed_gap",
    gap: float = 0.02,
    total_height: float = 1.0,
) -> list[float]:
    caps = np.asarray(caps, dtype=float)
    n = len(caps)
    total_cap = caps.sum()

    if method == "uniform":
        if n == 1:
            return [0.5]
        return [(i + 0.5) / n for i in range(n)]

    if method == "proportional":
        if n == 1:
            return [0.5]
        cursor = 0.0
        centers = []
        for cap in caps:
            h = (cap / total_cap) * total_height
            centers.append(float(cursor + h / 2))
            cursor += h
        return centers

    if method == "fixed_gap":
        if n == 1:
            return [0.5]
        total_gap = gap * (n - 1)
        available = total_height - total_gap
        if available <= 0:
            raise ValueError(
                f"Gap ({gap}) too large for {n} nodes in height {total_height}. "
                f"Reduce gap or reduce node count."
            )
        scale = available / total_cap
        cursor = 0.0
        centers = []
        for cap in caps:
            h = cap * scale
            centers.append(float(cursor + h / 2))
            cursor += h + gap
        return centers

    raise ValueError(f"Unknown method: {method!r}. Use 'fixed_gap', 'uniform', or 'proportional'.")


# ── Combined layout ─────────────────────────────────────

def compute_layout(
    layers: list[str],
    caps_by_layer: dict[str, list[float]],
    x_method: str | dict[str, float] = "auto",
    y_method: str = "fixed_gap",
    gap: float = 0.02,
    total_height: float = 1.0,
) -> tuple[list[float], list[float]]:
    if x_method == "auto":
        x_positions = {layer: xi for layer, xi in zip(layers, auto_x(len(layers)))}
    elif isinstance(x_method, dict):
        x_positions = x_method
    else:
        raise ValueError(f"x_method must be 'auto' or a dict, got {type(x_method)}")

    x_list = []
    y_list = []
    for layer in layers:
        caps = np.asarray(caps_by_layer[layer], dtype=float)
        xi = float(x_positions.get(layer, 0.0))
        yi = compute_y(caps.tolist(), method=y_method, gap=gap, total_height=total_height)
        x_list.extend([xi] * len(caps))
        y_list.extend(yi)
    return x_list, y_list
