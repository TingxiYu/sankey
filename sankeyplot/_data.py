from __future__ import annotations

import numpy as np
import pandas as pd


# ── from_wide ───────────────────────────────────────────

def from_wide(
    df: pd.DataFrame,
    layer_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    node_rows = []
    node_id: dict[tuple[str, str], int] = {}
    for layer in layer_cols:
        names = df[layer].unique()
        for name in names:
            key = (layer, str(name))
            if key not in node_id:
                node_id[key] = len(node_rows)
                node_rows.append({
                    "name": str(name),
                    "layer": layer,
                    "is_residual": str(name).lower() == "residual",
                })
    nodes = pd.DataFrame(node_rows)

    edge_counts: dict[tuple[int, int], float] = {}
    for src_col, tgt_col in zip(layer_cols[:-1], layer_cols[1:]):
        counts = df.groupby([src_col, tgt_col]).size()
        for (src_name, tgt_name), count in counts.items():
            src_key = (src_col, str(src_name))
            tgt_key = (tgt_col, str(tgt_name))
            si = node_id[src_key]
            ti = node_id[tgt_key]
            key = (si, ti)
            edge_counts[key] = edge_counts.get(key, 0.0) + float(count)

    edge_rows = [
        {"source": s, "target": t, "value": v}
        for (s, t), v in edge_counts.items()
    ]
    edges = pd.DataFrame(edge_rows)
    return nodes, edges


# ── from_capacity ───────────────────────────────────────

def _sinkhorn(
    src_caps: np.ndarray,
    tgt_caps: np.ndarray,
    rng: np.random.Generator,
    n_iter: int = 500,
    tol: float = 1e-12,
) -> np.ndarray:
    ns, nt = len(src_caps), len(tgt_caps)
    eps = 1e-12
    W = rng.exponential(1.0, size=(ns, nt)) + 0.1
    for _ in range(n_iter):
        row_sums = W.sum(axis=1) + eps
        if np.all(np.abs(row_sums - src_caps) < tol * 10):
            break
        W = W / row_sums[:, np.newaxis] * src_caps[:, np.newaxis]
        col_sums = W.sum(axis=0) + eps
        if np.all(np.abs(col_sums - tgt_caps) < tol * 10):
            break
        W = W / col_sums[np.newaxis, :] * tgt_caps[np.newaxis, :]
    return W


def from_capacity(
    capacities: dict[str, list[float]],
    layer_pairs: list[tuple[str, str]],
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)

    node_rows = []
    node_id: dict[tuple[str, str], int] = {}
    for layer, caps in capacities.items():
        for i, cap in enumerate(caps):
            if len(caps) == 1 and layer == "Outcome":
                name = "outcome"
            elif layer == "Inputs":
                name = f"Input_{i + 1}"
            else:
                name = f"{layer}_{i + 1}"
            key = (layer, name)
            node_id[key] = len(node_rows)
            node_rows.append({
                "name": name,
                "layer": layer,
                "is_residual": False,
                "capacity": cap,
            })
    nodes = pd.DataFrame(node_rows)

    edge_rows = []
    for src_layer, tgt_layer in layer_pairs:
        src_caps = np.array(capacities[src_layer])
        tgt_caps = np.array(capacities[tgt_layer])
        W = _sinkhorn(src_caps, tgt_caps, rng)

        src_mask = nodes["layer"] == src_layer
        tgt_mask = nodes["layer"] == tgt_layer
        src_idxs = nodes.index[src_mask].tolist()
        tgt_idxs = nodes.index[tgt_mask].tolist()

        for i, si in enumerate(src_idxs):
            for j, ti in enumerate(tgt_idxs):
                v = float(W[i, j])
                if v > 1e-6:
                    edge_rows.append({"source": si, "target": ti, "value": v})

    edges = pd.DataFrame(edge_rows)
    return nodes, edges


# ── Validation ──────────────────────────────────────────

def validate_conservation(
    edges: pd.DataFrame,
    nodes: pd.DataFrame,
) -> dict[str, float]:
    layers = nodes["layer"].unique().tolist()
    max_row_err = 0.0
    max_col_err = 0.0
    for src_l, tgt_l in zip(layers[:-1], layers[1:]):
        src_idxs = nodes.index[nodes["layer"] == src_l].tolist()
        tgt_idxs = nodes.index[nodes["layer"] == tgt_l].tolist()
        edge_mask = edges["source"].isin(src_idxs) & edges["target"].isin(tgt_idxs)
        sub = edges[edge_mask]

        src_out = sub.groupby("source")["value"].sum()
        tgt_in = sub.groupby("target")["value"].sum()

        total_flow = sub["value"].sum()
        row_err = abs(src_out.sum() - total_flow) / max(total_flow, 1e-10)
        col_err = abs(tgt_in.sum() - total_flow) / max(total_flow, 1e-10)
        max_row_err = max(max_row_err, row_err)
        max_col_err = max(max_col_err, col_err)

    return {"max_row_err": max_row_err, "max_col_err": max_col_err}


def validate_no_cycles(edges: pd.DataFrame) -> None:
    self_loops = edges[edges["source"] == edges["target"]]
    if len(self_loops) > 0:
        raise ValueError(
            f"Detected {len(self_loops)} self-loop(s). "
            "Sankey diagrams must be DAG; remove edges where source == target."
        )
