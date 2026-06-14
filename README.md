<p align="center">
  <img src="Sankey.png" alt="sankey logo" width="180">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-≥3.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="License">
  <img src="https://img.shields.io/badge/presets-Nature%20|%20Cell%20|%20Science-brightgreen" alt="Presets">
  <img src="https://img.shields.io/badge/render-Plotly-3f4f75?logo=plotly&logoColor=white" alt="Plotly">
</p>

# sankey &mdash; Create Flow Diagrams for Data Distribution Analysis

**`sankey`** is a Python package for producing publication-ready Sankey (alluvial)
diagrams styled to match the visual conventions of leading scientific journals
(*Nature*, *Cell*, *Science*).  It provides a unified high-level API that accepts
three common data representations (long-format edge tables, wide-format
observational DataFrames, and capacity dictionaries), computes a flexible
layout, applies journal-specific color schemes, and renders an interactive
Plotly figure exportable to HTML, PNG, or PDF.

---

### Highlights

- **Three input formats** &mdash; long-format `(edges, nodes)`, wide-format `DataFrame`, or capacity dictionaries
- **Journal-grade presets** &mdash; ready-to-use schemes matching *Nature*, *Cell*, and *Science* aesthetics
- **Sinkhorn&ndash;Knopp flow generation** &mdash; automatic flow matrix from per-node capacities
- **Flexible layout engine** &mdash; fixed-gap, uniform, and proportional vertical spacing
- **Multi-format export** &mdash; interactive HTML, high-resolution PNG, and vector PDF

---

## Table of Contents

- [Motivation](#motivation)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [1. Long-format (edges + nodes)](#1-long-format-edges--nodes)
  - [2. Wide-format DataFrame](#2-wide-format-dataframe)
  - [3. Capacity dictionary](#3-capacity-dictionary)
- [API Reference](#api-reference)
  - [`sankey()`](#sankey)
  - [`from_wide()`](#from_wide)
  - [`from_capacity()`](#from_capacity)
  - [`load_preset()`](#load_preset)
  - [`register_preset()`](#register_preset)
  - [Validation Utilities](#validation-utilities)
- [Journal Presets](#journal-presets)
  - [Built-in Schemes](#built-in-schemes)
  - [Custom Schemes](#custom-schemes)
- [Layout Methods](#layout-methods)
- [Color System](#color-system)
  - [Palettes](#palettes)
  - [Gradient Utilities](#gradient-utilities)
- [Architecture](#architecture)
- [Testing](#testing)
- [Exporting Figures](#exporting-figures)
- [Dependencies](#dependencies)
- [License](#license)
- [Citing](#citing)

## Motivation

Sankey diagrams are widely used in systems biology, epidemiology, clinical
cohort studies, and multi-omics integration to visualise the flow of
observations across a sequence of categorical variables.  Leading journals
employ distinctive visual grammars&mdash;restrained colour palettes, subtle
opacity layering, reserved treatment of residual flows, and clean sans-serif
typography&mdash;that are tedious to reproduce manually in general-purpose
plotting libraries.

**`sankey`** encapsulates these design rules in a set of versioned *presets* so
that researchers can focus on their data rather than on fine-tuning plot
aesthetics.

## Installation

```bash
pip install sankey
```

For optional Matplotlib-backed colormap support and the development toolchain:

```bash
pip install sankey[colormaps]
pip install sankey[dev]
```

**Requirements:** Python &ge; 3.10, NumPy &ge; 1.24, Pandas &ge; 2.0, Plotly &ge; 5.14.

## Quick Start

All three entry points below produce an identical internal representation and
are rendered through the same pipeline.

### 1. Long-format (edges + nodes)

Full control over node identities, layer membership, and individual edge
weights:

```python
import pandas as pd
from sankey import sankey

nodes = pd.DataFrame({
    "name":  ["Amp", "Mut", "Del", "Path_A", "Path_B", "Path_C", "Cancer"],
    "layer": ["Inputs", "Inputs", "Inputs", "H1", "H1", "H1", "Outcome"],
    "is_residual": [False, False, False, False, False, False, False],
})

edges = pd.DataFrame({
    "source": [0, 0, 1, 1, 2, 2, 3, 4, 4, 5],
    "target": [3, 4, 4, 5, 5, 3, 6, 6, 6, 6],
    "value":  [30, 25, 15, 12, 18, 0, 55, 28, 12, 18],
})

fig = sankey((edges, nodes), preset="nature", height=500, width=1400,
             title="Long-format example")
fig.write_html("sankey.html")
```

### 2. Wide-format DataFrame

Each row is an observation; columns encode the successive categorical layers:

```python
import pandas as pd
from sankey import sankey

df = pd.DataFrame({
    "Input":   ["Amp", "Amp", "Amp", "Mut", "Mut", "Mut", "Del", "Del"],
    "Process": ["Immune", "Metab", "Signal", "Immune", "Metab", "CellCycle", "Metab", "Signal"],
    "Outcome": ["Cancer"] * 8,
})

fig = sankey(df, layer_cols=["Input", "Process", "Outcome"], preset="cell")
fig.write_html("sankey_cell.html")
```

### 3. Capacity dictionary

Specify the total flow through each node; flows between layers are inferred
via the Sinkhorn&ndash;Knopp algorithm:

```python
from sankey import sankey

caps = {
    "Inputs":  [550, 270, 180],
    "H1":      [400, 350, 250],
    "Outcome": [1000],
}

fig = sankey(caps, preset="nature", seed=0)
fig.write_html("sankey_capacity.html")
```

## API Reference

### `sankey()`

```python
def sankey(
    data=None,
    preset: str | dict | None = None,
    *,
    main_palette=None,
    input_colors=None,
    residual_color=None,
    outcome_color=None,
    x_method="auto",
    y_method="fixed_gap",
    gap=0.02,
    layer_cols=None,
    layer_pairs=None,
    seed=42,
    node_thickness=None,
    node_pad=None,
    font_family=None,
    font_size=None,
    height=700,
    width=2000,
    title=None,
    **layout_kwargs,
) -> go.Figure
```

| Parameter         | Type                  | Default        | Description                                                              |
|-------------------|-----------------------|----------------|--------------------------------------------------------------------------|
| `data`            | `tuple`, `DataFrame`, or `dict` | &mdash; | Input data (see [Quick Start](#quick-start)).                            |
| `preset`          | `str` \| `dict`       | `"nature"`     | Named preset (`"nature"`, `"cell"`, `"science"`) or a custom `Scheme` dict. |
| `main_palette`    | `list[str]`           | from preset    | Override the main node colour palette.                                   |
| `input_colors`    | `list[str]`           | from preset    | Colours assigned to the first-layer nodes.                               |
| `residual_color`  | `str`                 | from preset    | Fill colour for residual nodes.                                          |
| `outcome_color`   | `str`                 | from preset    | Fill colour for outcome-layer nodes.                                     |
| `x_method`        | `"auto"` \| `dict`    | `"auto"`       | X-positioning: `"auto"` spreads layers evenly; a dict maps layer &rarr; x. |
| `y_method`        | `str`                 | `"fixed_gap"`  | Vertical layout method (`"fixed_gap"`, `"uniform"`, `"proportional"`).   |
| `gap`             | `float`               | `0.02`         | Gap between nodes (used by `"fixed_gap"` only).                          |
| `layer_cols`      | `list[str]`           | `None`         | Column order for wide-format DataFrames.                                 |
| `layer_pairs`     | `list[tuple]`         | auto-derived   | Adjacent-layer pairs for capacity input.                                 |
| `seed`            | `int`                 | `42`           | Random seed for capacity-based flow generation.                          |
| `node_thickness`  | `int`                 | from preset    | Vertical thickness of node rectangles (pixels).                          |
| `node_pad`        | `int`                 | from preset    | Padding between nodes (pixels).                                          |
| `font_family`     | `str`                 | from preset    | Font family for labels and annotations.                                  |
| `font_size`       | `int`                 | from preset    | Base font size.                                                          |
| `height`          | `int`                 | `700`          | Figure height (pixels).                                                  |
| `width`           | `int`                 | `2000`         | Figure width (pixels).                                                   |
| `title`           | `str`                 | `None`         | Optional figure title.                                                   |

**Returns:** `plotly.graph_objects.Figure`

### `from_wide()`

```python
def from_wide(df: pd.DataFrame, layer_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]
```

Converts a wide-format observational DataFrame into `(nodes, edges)` tables.
Nodes named `"Residual"` (case-insensitive) are automatically flagged with
`is_residual = True`.

### `from_capacity()`

```python
def from_capacity(
    capacities: dict[str, list[float]],
    layer_pairs: list[tuple[str, str]],
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]
```

Generates `(nodes, edges)` from per-node total capacities using the
Sinkhorn&ndash;Knopp algorithm to construct a doubly-stochastic flow matrix
between each adjacent layer pair.

### `load_preset()`

```python
def load_preset(name: str, **overrides) -> Scheme
```

Returns a deep copy of the named preset, optionally merged with keyword
overrides.  Raises `ValueError` for unknown preset names.

### `register_preset()`

```python
def register_preset(name: str, config: Scheme) -> None
```

Registers a new named preset globally.  Useful for institutional or
lab-specific style guides.

### Validation Utilities

```python
def validate_conservation(edges: pd.DataFrame, nodes: pd.DataFrame) -> dict[str, float]
def validate_no_cycles(edges: pd.DataFrame) -> None
```

- `validate_conservation` &mdash; checks that total flow is conserved across
  each adjacent layer pair; returns `{"max_row_err": ..., "max_col_err": ...}`.
- `validate_no_cycles` &mdash; raises `ValueError` if any self-loop
  (`source == target`) is present, enforcing the DAG constraint required by
  Sankey diagrams.

## Journal Presets

### Built-in Schemes

| Preset     | Primary Hue  | Font        | Character                        |
|------------|-------------|-------------|----------------------------------|
| `"nature"` | Crimson-red | Arial       | Warm, restrained, high contrast. |
| `"cell"`   | Ocean-blue  | Helvetica   | Cool, clinical, minimalist.      |
| `"science"`| Multichrome | Helvetica   | Bold primaries, neutral grey background. |

Each preset defines a complete visual scheme:

```python
{
    "main_palette":        [...],   # 6-hex list for main nodes
    "gradient_method":     "sequential",
    "gradient_lighten":    0.6,
    "input_colors":        [...],   # 3-hex list for input layer
    "residual_color":      "#...",  # fill for residual nodes
    "residual_link_alpha": 0.38,    # opacity for residual links
    "residual_link_color": "#...",  # stroke for residual links
    "outcome_color":       "#...",  # fill for outcome nodes
    "outcome_link_alpha":  0.35,    # opacity for outcome links
    "default_link_alpha":  0.18,    # opacity for standard links
    "font_family":         "Arial",
    "font_size":           18,
    "node_thickness":      25,
    "node_pad":            80,
}
```

### Custom Schemes

Pass a dictionary conforming to the `Scheme` TypedDict directly as the `preset`
argument, or register it for reuse:

```python
from sankey import sankey, register_preset

register_preset("my_lab", {
    "main_palette":   ["#2C3E50", "#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"],
    "input_colors":   ["#3498DB", "#2ECC71", "#F39C12"],
    "residual_color": "#F5F5F5",
    "outcome_color":  "#2C3E50",
    "font_family":    "Times New Roman",
    "font_size":      14,
    "node_thickness": 20,
    "node_pad":       60,
})

fig = sankey(data, preset="my_lab")
```

## Layout Methods

Three vertical layout strategies are available:

| Method           | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `"fixed_gap"`    | Constant vertical gap between nodes; node height proportional to capacity.  |
| `"uniform"`      | All nodes have equal height regardless of capacity.                         |
| `"proportional"` | Nodes fill the available vertical space in proportion to capacity; no gaps. |

Horizontal (`x`) layout defaults to evenly-spaced layers (`"auto"`) or accepts
a manual `dict` mapping each layer name to an x-coordinate in `[0, 1]`.

## Color System

### Palettes

The package bundles several perceptually-informed colour palettes available as
standalone functions:

```python
from sankey import palette_nature, palette_cell, palette_science
from sankey import palette_lancet, palette_colorbrewer, palette_viridis, palette_batlow
from sankey import palette_custom

# Static presets
nature_colors  = palette_nature()          # → 6-hex list
cell_colors    = palette_cell()            # → 6-hex list
science_colors = palette_science()         # → 6-hex list
lancet_colors  = palette_lancet()          # → 6-hex list

# Parameterised
cb_colors = palette_colorbrewer("Set1", n=5)   # ColorBrewer subsets
viridis   = palette_viridis(n=12)              # Viridis (Matplotlib optional)
batlow    = palette_batlow(n=12)               # Batlow (built-in fallback)
custom    = palette_custom(["#FF0000", "#00FF00", "#0000FF"])
```

### Gradient Utilities

```python
from sankey._colors import gradient_sequential, gradient_diverging, layer_gradient

sequential = gradient_sequential("#7B1515", "#F5D5D5", n=6)
diverging  = gradient_diverging("#313695", "#FFFFBF", "#A50026", n=11)
layer      = layer_gradient("#4A6FAF", n=5, lighten=0.6)
```

## Architecture

```
sankey/
├── __init__.py       # Public API: sankey() entry point
├── _typing.py        # Type aliases: NodeTable, LinkTable, Scheme, ColorRule
├── _data.py          # Data ingestion: from_wide, from_capacity, validators
├── _layout.py        # Layout engine: auto_x, compute_y, compute_layout
├── _colors.py        # Colour system: palettes, gradients, rule matching
├── _presets.py       # Journal presets registry: load, list, register
└── _render.py        # Plotly renderer: node/link colouring, annotations
```

The pipeline follows a strict **data &rarr; layout &rarr; render** sequence:

1. **Data ingestion** (`_data.py`) &mdash; all input formats are normalised to
   `(nodes: DataFrame, edges: DataFrame)`.
2. **Layout computation** (`_layout.py`) &mdash; x-positions are assigned per
   layer; y-positions are computed per node according to the chosen method.
3. **Colour assignment** (`_colors.py`, `_render.py`) &mdash; a rule engine
   matches nodes against conditions (`is_residual`, `is_input`, `is_outcome`,
   key-value equality) and applies colours, palettes, and link opacities.
4. **Rendering** (`_render.py`) &mdash; a Plotly `go.Sankey` trace is
   constructed with layer annotations, hover templates, and layout
   configuration.

## Testing

The test suite covers all public modules and the end-to-end pipeline:

```
tests/
├── test_data.py         # from_wide, from_capacity, validators
├── test_layout.py       # auto_x, compute_y, compute_layout
├── test_colors.py       # palette functions, hex_to_rgba, gradients
├── test_presets.py      # load_preset, list_presets, register_preset
├── test_render.py       # render(), node/link colouring, annotations
├── test_integration.py  # sankey() full pipeline (all 3 input formats)
└── conftest.py          # Shared fixtures
```

Run the suite with:

```bash
pytest tests/ -v
```

## Exporting Figures

Plotly figures support three output formats:

```python
fig = sankey(data, preset="nature")

# Interactive HTML (browser-viewable, self-contained)
fig.write_html("figure.html")

# Raster image (specify scale for print resolution; scale=2 recommended)
fig.write_image("figure.png", width=1800, height=800, scale=2)

# Vector graphics (lossless, preferred for journal submission)
fig.write_image("figure.pdf", width=1800, height=800)
```

**Note:** PNG and PDF export require the `kaleido` package (`pip install kaleido`).

## Dependencies

| Package   | Minimum Version | Required | Purpose                              |
|-----------|-----------------|----------|--------------------------------------|
| `numpy`   | 1.24            | Yes      | Numerical arrays, random sampling    |
| `pandas`  | 2.0             | Yes      | Tabular data structures              |
| `plotly`  | 5.14            | Yes      | Sankey trace construction & rendering |
| `matplotlib` | 3.7          | No       | Extended colormap support            |
| `pytest`  | 7.0             | No       | Test runner (dev only)               |
| `kaleido` | &mdash;         | No       | PNG/PDF static image export          |

## License

This project is distributed under a proprietary license.  See the [LICENSE](LICENSE) file for full terms.

- Free for personal and academic research use.
- Generated figures may be included in academic papers, reports, and presentations.
- **Commercial use of any kind is prohibited.**
- Redistribution, sublicensing, or public disclosure of source code is strictly forbidden.

## Citing

If you use `sankey` in published research, please cite it as:

> Yu, T. (2026). *sankey: Publication-quality Sankey diagrams for scientific
> journals* (Version 0.1.0) [Python package].
> https://github.com/tingxi-yu/sankey

BibTeX:

```bibtex
@software{yu2026sankey,
  author       = {Tingxi Yu},
  title        = {sankey: Publication-quality Sankey diagrams for scientific journals},
  year         = {2026},
  version      = {0.1.0},
  url          = {https://github.com/tingxi-yu/sankey},
}
```