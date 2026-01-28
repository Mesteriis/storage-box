"""
Storage Box System - Parametric 3D Printable Storage Solution

A comprehensive system for generating customizable storage boxes with:
- V-profile rails with self-centering
- Two-stage stops with acoustic profiles
- Premium features (shadow gap, dusty mode, etc.)
- Belovodye design style with rune patterns
- YAML configuration save/load with presets
- Spring whisker anti-wobble (6 variants test kit)
- Smart cartridge bay for NFC/sensors
- Complete calibration test kit

Usage:
    # From Blender Python console:
    from storage_box.storage_box import generate_interactive
    generate_interactive("workshop_tools", "./output")
    
    # From command line:
    blender --background --python storage_box.py -- --preset mvp

Version: 1.0.0
Compatibility: 1.0
"""

__version__ = "1.0.0"
__compat_version__ = "1.0"

from .config import (
    BoxConfig,
    DerivedConfig,
    DesignTokens,
    DesignStyle,
    MaterialType,
    ConnectionType,
    DividerLayout,
    DividerMode,
    RailProfile,
    PrinterProfile,
    SoundProfile,
    RunePattern,
    BelovodieColor,
    WhiskerVariant,
    PrintMode,
    ConfigManager,
    PRESETS,
)

__all__ = [
    # Version
    "__version__",
    "__compat_version__",
    # Config
    "BoxConfig",
    "DerivedConfig", 
    "DesignTokens",
    "ConfigManager",
    "PRESETS",
    # Enums
    "DesignStyle",
    "MaterialType",
    "ConnectionType",
    "DividerLayout",
    "DividerMode",
    "RailProfile",
    "PrinterProfile",
    "SoundProfile",
    "PrintMode",
    "RunePattern",
    "BelovodieColor",
    "WhiskerVariant",
]
