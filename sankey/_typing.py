from __future__ import annotations

from typing import Callable, Dict, TypedDict

import pandas as pd

# Core data tables
NodeTable = pd.DataFrame
LinkTable = pd.DataFrame


class ColorRule(TypedDict, total=False):
    match: str | Callable[[pd.Series], bool]
    color: str
    palette: list[str]
    link_alpha: float


class Scheme(TypedDict, total=False):
    main_palette: list[str]
    gradient_method: str
    gradient_lighten: float
    gradient_low: str
    gradient_mid: str
    gradient_high: str
    input_colors: list[str]
    residual_color: str
    residual_link_alpha: float
    residual_link_color: str
    outcome_color: str
    outcome_link_alpha: float
    default_link_alpha: float
    font_family: str
    font_size: int
    node_thickness: int
    node_pad: int


class LayoutConfig(TypedDict, total=False):
    method: str
    gap: float
    residual_position: str
    residual_gap_above: float
    canvas_height: int


PresetRegistry = Dict[str, Scheme]
