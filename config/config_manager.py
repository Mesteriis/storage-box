"""
ConfigManager - YAML configuration save/load.

Handles saving and loading BoxConfig to/from YAML files.
Supports versioning for forward compatibility.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

from .box_config import (
    BoxConfig,
    GeometryConfig,
    MechanicsConfig,
    PatternConfig,
    DetailsConfig,
)
from .derived_config import DerivedConfig
from .enums import (
    DesignStyle,
    MaterialType,
    ConnectionType,
    DividerLayout,
    DividerMode,
    RailProfile,
    PrinterProfile,
    SoundProfile,
    HandleMode,
    SmartCartridge,
    PrintMode,
    AntiWobbleType,
    WhiskerVariant,
    RunePattern,
    PatternPosition,
    BelovodieColor,
    BelovodiePreset,
    ShellGeometry,
)


# Version constants
FORMAT_VERSION = "1.0"    # YAML structure version
COMPAT_VERSION = "1.0"    # Hardware compatibility version


class ConfigManager:
    """Manager for saving/loading configurations."""
    
    DEFAULT_PATH = Path("configs")
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or self.DEFAULT_PATH
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, config: BoxConfig, filename: str, 
             include_derived: bool = False) -> Path:
        """
        Save configuration to YAML file.
        
        Args:
            config: BoxConfig to save
            filename: Name without extension
            include_derived: Include computed values for debug
        
        Returns:
            Path to saved file
        """
        filepath = self.config_dir / f"{filename}.yaml"
        
        data = self._config_to_dict(config)
        
        # Add meta information
        data["meta"] = {
            "format_version": FORMAT_VERSION,
            "compat_version": COMPAT_VERSION,
            "created": datetime.now().isoformat(),
            "description": config.description,
        }
        
        # Optionally add derived values for debugging
        if include_derived:
            derived = DerivedConfig(config)
            data["_derived"] = {
                "wall_thickness": derived.wall_thickness,
                "tolerance_slide": derived.tolerances["slide"],
                "tolerance_snap": derived.tolerances["snap"],
                "inner_width": derived.effective_inner_width,
                "inner_depth": derived.effective_inner_depth,
                "drawer_width": derived.drawer_width,
                "drawer_depth": derived.drawer_depth,
                "divider_count": list(derived.divider_count),
                "features": derived.features_enabled,
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(
                data, f, 
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
        
        return filepath
    
    def load(self, filename: str) -> BoxConfig:
        """
        Load configuration from YAML file.
        
        Args:
            filename: Name without extension
        
        Returns:
            BoxConfig instance
        """
        filepath = self.config_dir / f"{filename}.yaml"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Config not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Version check
        meta = data.get("meta", {})
        file_format = meta.get("format_version", "1.0")
        file_compat = meta.get("compat_version", "1.0")
        
        if file_format != FORMAT_VERSION:
            print(f"Warning: Format version {file_format} != {FORMAT_VERSION}")
        if file_compat != COMPAT_VERSION:
            print(f"Warning: Compat version {file_compat} != {COMPAT_VERSION}")
        
        return self._dict_to_config(data)
    
    def list_configs(self) -> List[str]:
        """List all saved configurations."""
        return [f.stem for f in self.config_dir.glob("*.yaml")]
    
    def delete(self, filename: str) -> bool:
        """Delete a configuration file."""
        filepath = self.config_dir / f"{filename}.yaml"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def _config_to_dict(self, config: BoxConfig) -> Dict[str, Any]:
        """Convert BoxConfig to dictionary for YAML."""
        return {
            "dimensions": {
                "width": config.width,
                "depth": config.depth,
                "height": config.height,
            },
            "design": {
                "style": config.design.value,
                "belovodie_preset": (
                    config.belovodie_preset.value 
                    if config.belovodie_preset else None
                ),
                "colors": {
                    "body": config.color_body.value,
                    "accent": config.color_accent.value,
                },
            },
            "material": {
                "type": config.material.value,
                "printer": config.printer.value,
                "print_mode": config.print_mode.value,
            },
            "mechanics": {
                "rail_profile": config.mechanics.rail_profile.value,
                "anti_wobble": {
                    "type": config.mechanics.anti_wobble.value,
                    "whisker_variant": config.mechanics.whisker_variant.value,
                },
                "sound_profile": config.mechanics.sound_profile.value,
                "service_channel": config.mechanics.service_channel,
            },
            "dividers": {
                "layout": config.dividers.value,
                "mode": config.divider_mode.value,
                "target_cell_size": list(config.target_cell_size),
            },
            "connection": config.connection.value,
            "context": {
                "mount": config.mount,
                "stack_levels": config.stack_levels,
                "expected_weight": config.expected_weight,
            },
            "handle": {
                "mode": config.handle_mode.value,
                "tactile_zone": config.handle_tactile_zone,
            },
            "label": {
                "frame_style": config.label_frame_style,
            },
            "smart": {
                "cartridge": config.smart_cartridge.value,
                "hub_connector": config.hub_connector,
            },
            "special": {
                "sealed": config.sealed,
            },
            "geometry": {
                "shape": config.geometry.shape.value,
                "slope_angle": config.geometry.slope_angle,
                "slope_direction": config.geometry.slope_direction,
                "maintain_back_vertical": config.geometry.maintain_back_vertical,
            },
            "patterns": {
                "type": config.pattern.type.value,
                "position": config.pattern.position.value,
                "spacing": config.pattern.spacing,
                "band_height": config.pattern.band_height,
                "groove_depth": config.pattern.groove_depth,
                "groove_width": config.pattern.groove_width,
            },
            "details": {
                "shadow_gap": config.details.shadow_gap,
                "guide_cones": config.details.guide_cones,
                "rune_key": config.details.rune_key,
                "rivet_dots": config.details.rivet_dots,
                "version_mark": config.details.version_mark,
            },
        }
    
    def _dict_to_config(self, data: Dict[str, Any]) -> BoxConfig:
        """Convert dictionary to BoxConfig."""
        dims = data.get("dimensions", {})
        design = data.get("design", {})
        material = data.get("material", {})
        mechanics = data.get("mechanics", {})
        dividers_data = data.get("dividers", {})
        context = data.get("context", {})
        handle = data.get("handle", {})
        label = data.get("label", {})
        smart = data.get("smart", {})
        special = data.get("special", {})
        geometry = data.get("geometry", {})
        patterns = data.get("patterns", {})
        details = data.get("details", {})
        meta = data.get("meta", {})
        
        # Parse belovodie_preset
        bp_value = design.get("belovodie_preset")
        belovodie_preset = (
            BelovodiePreset(bp_value) if bp_value else None
        )
        
        return BoxConfig(
            # Dimensions
            width=dims.get("width", 200.0),
            depth=dims.get("depth", 220.0),
            height=dims.get("height", 80.0),
            
            # Design
            design=DesignStyle(design.get("style", "nordic")),
            belovodie_preset=belovodie_preset,
            color_body=BelovodieColor(
                design.get("colors", {}).get("body", "mist_white")
            ),
            color_accent=BelovodieColor(
                design.get("colors", {}).get("accent", "emerald_deep")
            ),
            
            # Material
            material=MaterialType(material.get("type", "hyper_pla")),
            printer=PrinterProfile(material.get("printer", "k1c")),
            print_mode=PrintMode(material.get("print_mode", "normal")),
            
            # Mechanics
            mechanics=MechanicsConfig(
                rail_profile=RailProfile(
                    mechanics.get("rail_profile", "v_profile")
                ),
                anti_wobble=AntiWobbleType(
                    mechanics.get("anti_wobble", {}).get("type", "none")
                ),
                whisker_variant=WhiskerVariant(
                    mechanics.get("anti_wobble", {}).get(
                        "whisker_variant", "med_l"
                    )
                ),
                sound_profile=SoundProfile(
                    mechanics.get("sound_profile", "soft_click")
                ),
                service_channel=mechanics.get("service_channel", False),
            ),
            
            # Dividers
            dividers=DividerLayout(dividers_data.get("layout", "auto")),
            divider_mode=DividerMode(dividers_data.get("mode", "snap")),
            target_cell_size=tuple(
                dividers_data.get("target_cell_size", [50, 50])
            ),
            
            # Connection
            connection=ConnectionType(
                data.get("connection", "dovetail")
            ),
            
            # Context
            mount=context.get("mount", "table"),
            stack_levels=context.get("stack_levels", 1),
            expected_weight=context.get("expected_weight", 500.0),
            
            # Handle
            handle_mode=HandleMode(handle.get("mode", "hook")),
            handle_tactile_zone=handle.get("tactile_zone", True),
            
            # Label
            label_frame_style=label.get("frame_style", "recessed_portal"),
            
            # Smart
            smart_cartridge=SmartCartridge(
                smart.get("cartridge", "plain")
            ),
            hub_connector=smart.get("hub_connector", False),
            
            # Special
            sealed=special.get("sealed", False),
            
            # Geometry
            geometry=GeometryConfig(
                shape=ShellGeometry(
                    geometry.get("shape", "rectangular")
                ),
                slope_angle=geometry.get("slope_angle", 15.0),
                slope_direction=geometry.get("slope_direction", "front"),
                maintain_back_vertical=geometry.get(
                    "maintain_back_vertical", True
                ),
            ),
            
            # Patterns
            pattern=PatternConfig(
                type=RunePattern(patterns.get("type", "none")),
                position=PatternPosition(
                    patterns.get("position", "back_edge")
                ),
                spacing=patterns.get("spacing", 8.0),
                band_height=patterns.get("band_height", 14.0),
                groove_depth=patterns.get("groove_depth", 0.35),
                groove_width=patterns.get("groove_width", 0.8),
            ),
            
            # Details
            details=DetailsConfig(
                shadow_gap=details.get("shadow_gap", 0.4),
                guide_cones=details.get("guide_cones", True),
                rune_key=details.get("rune_key", False),
                rivet_dots=details.get("rivet_dots", False),
                version_mark=details.get("version_mark", True),
            ),
            
            # Description
            description=meta.get("description", ""),
        )


def save_preset(preset_name: str, config_dir: Optional[Path] = None):
    """Save a preset configuration to YAML."""
    from .presets import PRESETS
    
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    config = PRESETS[preset_name]
    manager = ConfigManager(config_dir)
    return manager.save(config, preset_name, include_derived=True)


# CLI support
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Storage Box Config Manager"
    )
    parser.add_argument(
        "action", 
        choices=["save", "load", "list", "preset"],
        help="Action to perform"
    )
    parser.add_argument("--name", help="Config filename")
    parser.add_argument(
        "--preset", 
        help="Preset name (smarthome_desk, workshop_tools, etc.)"
    )
    
    args = parser.parse_args()
    
    manager = ConfigManager()
    
    if args.action == "list":
        configs = manager.list_configs()
        print("Available configs:", configs)
    
    elif args.action == "preset" and args.preset:
        try:
            path = save_preset(args.preset)
            print(f"Saved preset '{args.preset}' to {path}")
        except ValueError as e:
            print(f"Error: {e}")
    
    elif args.action == "load" and args.name:
        try:
            config = manager.load(args.name)
            print(f"Loaded: {config}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
