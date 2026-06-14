from __future__ import annotations


# ── Utilities ───────────────────────────────────────────

def hex_to_rgba(h: str, a: float) -> str:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


def lerp_color(c1: str, c2: str, t: float) -> str:
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


# ── Built-in color arrays (matplotlib-free fallbacks) ───

_COLORBREWER = {
    "Set1":  ["#E41A1C","#377EB8","#4DAF4A","#984EA3","#FF7F00","#A65628","#F781BF","#999999"],
    "Set2":  ["#66C2A5","#FC8D62","#8DA0CB","#E78AC3","#A6D854","#FFD92F","#E5C494","#B3B3B3"],
    "Set3":  ["#8DD3C7","#FFFFB3","#BEBADA","#FB8072","#80B1D3","#FDB462","#B3DE69","#FCCDE5","#D9D9D9"],
    "Paired":["#A6CEE3","#1F78B4","#B2DF8A","#33A02C","#FB9A99","#E31A1C","#FDBF6F","#FF7F00","#CAB2D6","#6A3D9A","#FFFF99","#B15928"],
    "Dark2": ["#1B9E77","#D95F02","#7570B3","#E7298A","#66A61E","#E6AB02","#A6761D","#666666"],
    "Accent":["#7FC97F","#BEAED4","#FDC086","#FFFF99","#386CB0","#F0027F","#BF5B17","#666666"],
}

_VIRIDIS_10 = ["#440154","#481567","#482677","#453781","#3F4788","#39558C","#32648E","#2D718E","#287D8E","#238A8D"]
_BATLOW_10 = ["#011A4A","#11316B","#2A468D","#425BA9","#5B71BF","#7787CF","#969EDA","#B6B5E2","#D6CDE8","#F7E6EC"]


def _interp_colors(anchors: list[str], n: int) -> list[str]:
    """Interpolate n colors from anchor color stops."""
    if n <= 0:
        return []
    if n == 1:
        return [anchors[0]]
    result = []
    m = len(anchors) - 1
    for i in range(n):
        t = i / (n - 1) * m
        lo = min(int(t), m)
        hi = min(lo + 1, m)
        frac = t - lo
        result.append(lerp_color(anchors[lo], anchors[hi], frac))
    return result


def _try_matplotlib_colormap(name: str, n: int) -> list[str] | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib import colormaps as mpl_cmaps
        from matplotlib.colors import rgb2hex
        cmap = mpl_cmaps.get(name)
        if cmap is None:
            return None
        return [rgb2hex(cmap(i / max(n - 1, 1))) for i in range(n)]
    except Exception:
        return None


# ── Palettes ────────────────────────────────────────────

def palette_nature() -> list[str]:
    return ["#7B1515", "#B54848", "#D4956A", "#8BBDD4", "#4A6FAF", "#C4A35A"]


def palette_cell() -> list[str]:
    return ["#1B6CA8", "#3DA5D9", "#73BFB8", "#9ED9CC", "#F4A261", "#E76F51"]


def palette_science() -> list[str]:
    return ["#D32F2F", "#1976D2", "#757575", "#FFA000", "#388E3C", "#7B1FA2"]


def palette_lancet() -> list[str]:
    return ["#00468B", "#ED0000", "#42B540", "#0099B4", "#925E9F", "#FDAF91"]


def palette_colorbrewer(name: str, n: int | None = None) -> list[str]:
    if name not in _COLORBREWER:
        valid = list(_COLORBREWER.keys())
        raise ValueError(f"Unknown ColorBrewer palette '{name}'. Valid: {valid}")
    colors = _COLORBREWER[name]
    if n is not None:
        if n > len(colors):
            raise ValueError(f"'{name}' has only {len(colors)} colors, requested {n}")
        return colors[:n]
    return list(colors)


def palette_viridis(n: int = 10) -> list[str]:
    mpl = _try_matplotlib_colormap("viridis", n)
    if mpl is not None:
        return mpl
    return _interp_colors(_VIRIDIS_10, n)


def palette_batlow(n: int = 10) -> list[str]:
    return _interp_colors(_BATLOW_10, n)


def palette_custom(hex_list: list[str]) -> list[str]:
    if not hex_list:
        raise ValueError("Custom palette requires at least one color.")
    for c in hex_list:
        if not (isinstance(c, str) and c.startswith("#") and len(c) == 7):
            raise ValueError(f"Invalid hex color: {c!r}")
    return list(hex_list)


# ── Gradients ───────────────────────────────────────────

def gradient_sequential(dark: str, light: str, n: int) -> list[str]:
    if n == 1:
        return [dark]
    return [lerp_color(dark, light, i / (n - 1)) for i in range(n)]


def gradient_diverging(low: str, mid: str, high: str, n: int) -> list[str]:
    if n == 1:
        return [mid]
    half = (n - 1) / 2
    result = []
    for i in range(n):
        if i <= half:
            t = i / half if half > 0 else 0
            result.append(lerp_color(low, mid, t))
        else:
            t = (i - half) / half if half > 0 else 1
            result.append(lerp_color(mid, high, t))
    return result


def layer_gradient(base_color: str, n: int, lighten: float = 0.6) -> list[str]:
    light_color = lerp_color(base_color, "#FFFFFF", lighten)
    return gradient_sequential(base_color, light_color, n)


# ── Color Rules ─────────────────────────────────────────

def _eval_match(match, node) -> bool:
    """Evaluate a match condition against a node (dict or pd.Series)."""
    if callable(match):
        return bool(match(node))
    expr = str(match).strip()
    if expr == "is_residual":
        return bool(node.get("is_residual", False))
    if expr == "is_input":
        return bool(node.get("is_input", False))
    if expr == "is_outcome":
        return bool(node.get("is_outcome", False))
    if "==" in expr:
        parts = expr.split("==")
        key = parts[0].strip()
        val = parts[1].strip().strip("'").strip('"')
        return str(node.get(key, "")) == val
    return False


def _apply_color_rules(node, rules: list[dict]) -> dict:
    """Apply the first matching rule to a single node."""
    for rule in rules:
        if _eval_match(rule.get("match", ""), node):
            return {k: v for k, v in rule.items() if k != "match"}
    return {}


def _apply_color_rules_to_df(
    nodes_df,
    rules: list[dict],
    default_color: str = "#CCCCCC",
    default_link_alpha: float = 0.22,
) -> tuple[list[str], list[float]]:
    """Apply rules to all nodes in a DataFrame. Returns (colors, link_alphas)."""
    colors = []
    alphas = []
    for _, node in nodes_df.iterrows():
        result = _apply_color_rules(node, rules)
        color = result.get("color") or result.get("palette")
        if color is None:
            color = default_color
        if isinstance(color, list):
            color = default_color
        colors.append(color)
        alphas.append(float(result.get("link_alpha", default_link_alpha)))
    return colors, alphas
