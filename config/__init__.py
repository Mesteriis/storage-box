"""Configuration module for Storage Box System."""

from .enums import (
    DesignStyle,
    ConnectionType,
    MaterialType,
    DividerLayout,
    DividerMode,
    RailProfile,
    PrinterProfile,
    SoundProfile,
    RunePattern,
    BelovodieColor,
    BelovodiePreset,
    HandleMode,
    ShellGeometry,
    ColorInsert,
    SmartCartridge,
    InsertType,
    PrintMode,
    WhiskerVariant,
)

from .box_config import BoxConfig
from .derived_config import DerivedConfig
from .design_tokens import DesignTokens
from .tolerances import ToleranceProfile
from .presets import PRESETS, BoxPreset
from .rules import Rule, RulesEngine
from .config_manager import ConfigManager

__all__ = [
    # Enums
    "DesignStyle",
    "ConnectionType",
    "MaterialType",
    "DividerLayout",
    "DividerMode",
    "RailProfile",
    "PrinterProfile",
    "SoundProfile",
    "RunePattern",
    "BelovodieColor",
    "BelovodiePreset",
    "HandleMode",
    "ShellGeometry",
    "ColorInsert",
    "SmartCartridge",
    "InsertType",
    "PrintMode",
    "WhiskerVariant",
    # Config classes
    "BoxConfig",
    "DerivedConfig",
    "DesignTokens",
    "ToleranceProfile",
    "ConfigManager",
    # Presets
    "PRESETS",
    "BoxPreset",
    # Rules
    "Rule",
    "RulesEngine",
]
