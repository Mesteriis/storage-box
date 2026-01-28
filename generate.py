#!/usr/bin/env python3
"""
Storage Box Generator - Main Entry Point.

Parametric 3D printable storage box system for smart home.
Run this script in Blender Python environment.

Usage:
    blender --background --python storage_box.py -- [options]
    
    Options:
        --preset NAME    Use preset configuration (mvp, smarthome_desk, 
                         workshop_tools, medical_sealed)
        --config FILE    Load YAML configuration file
        --output DIR     Output directory for STL files
        --test-only      Generate only test kit pieces
        
Examples:
    # Generate with MVP preset
    blender --background --python storage_box.py -- --preset mvp
    
    # Generate from YAML config
    blender --background --python storage_box.py -- --config my_config.yaml
    
    # Generate workshop preset
    blender --background --python storage_box.py -- --preset workshop_tools
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("Warning: Blender Python API not available")
    print("This script must be run from within Blender")

from .config import (
    BoxConfig,
    DerivedConfig,
    DesignTokens,
    ConfigManager,
    PRESETS,
)
from .config.enums import DesignStyle


def setup_scene():
    """Set up clean Blender scene."""
    if not HAS_BPY:
        return
    
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Set units to millimeters
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 0.001
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'


def generate_storage_box(
    config: BoxConfig,
    output_dir: Path,
    include_test_kit: bool = True,
) -> dict:
    """
    Generate complete storage box from configuration.
    
    Args:
        config: BoxConfig with all parameters
        output_dir: Directory for STL output
        include_test_kit: Generate calibration test pieces
    
    Returns:
        Dict with generated components
    """
    if not HAS_BPY:
        print("Error: Blender Python API required")
        return {}
    
    # Compute derived parameters
    derived = DerivedConfig(config)
    
    # Validate
    warnings = derived.validate()
    if warnings:
        print("Configuration warnings:")
        for w in warnings:
            print(f"  - {w}")
    
    # Get design tokens
    tokens = DesignTokens.from_style(config.design, derived.wall_thickness)
    tokens = tokens.apply_print_mode(config.print_mode.value)
    
    print(derived.summary())
    
    # Set up scene
    setup_scene()
    
    # Import component builders
    from storage_box.components import build_shell, build_drawer
    from storage_box.components.dividers import build_divider_set
    from storage_box.tests import build_complete_test_kit
    from storage_box.export import export_component_set
    
    components = {}
    
    # Build shell
    print("Building shell...")
    shell = build_shell(derived, tokens, name="Shell")
    components["shell"] = shell
    
    # Build drawer
    print("Building drawer...")
    drawer = build_drawer(derived, tokens, name="Drawer")
    if drawer:
        # Position drawer inside shell
        drawer.location = (0, 0, derived.floor_thickness + 2)
    components["drawer"] = drawer
    
    # Build dividers
    print("Building dividers...")
    dividers = build_divider_set(derived)
    components["dividers"] = dividers
    
    # Build test kit
    if include_test_kit:
        print("Building test kit...")
        test_kit = build_complete_test_kit(derived)
        # Position test pieces outside main model
        if test_kit.get("rail_test"):
            test_kit["rail_test"].location = (config.width + 50, 0, 0)
        if test_kit.get("snap_test"):
            test_kit["snap_test"].location = (config.width + 50, 50, 0)
        if test_kit.get("magnet_test"):
            test_kit["magnet_test"].location = (config.width + 50, 100, 0)
        components["test_kit"] = test_kit
    
    # Export to STL
    print(f"Exporting to {output_dir}...")
    manifest = export_component_set(components, output_dir, derived)
    
    print(f"\nExport complete!")
    print(f"Total print time: {manifest.total_print_time}")
    print(f"Total filament: {manifest.total_filament}g")
    print(f"Files saved to: {output_dir}")
    
    return components


def generate_test_only(
    config: BoxConfig,
    output_dir: Path,
) -> dict:
    """Generate only test kit pieces for calibration."""
    if not HAS_BPY:
        print("Error: Blender Python API required")
        return {}
    
    derived = DerivedConfig(config)
    
    setup_scene()
    
    from storage_box.tests import build_complete_test_kit
    from storage_box.export import export_stl
    
    test_kit = build_complete_test_kit(derived)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for name, piece in test_kit.items():
        if piece and not isinstance(piece, list):
            filepath = output_dir / f"test_{name}.stl"
            export_stl(piece, filepath)
            print(f"Exported: {filepath}")
    
    # Export whiskers separately
    if "whiskers" in test_kit:
        for whisker in test_kit["whiskers"]:
            if whisker:
                filepath = output_dir / f"{whisker.name}.stl"
                export_stl(whisker, filepath)
                print(f"Exported: {filepath}")
    
    return test_kit


def load_config_from_yaml(yaml_path: Path) -> BoxConfig:
    """Load BoxConfig from YAML file."""
    manager = ConfigManager(yaml_path.parent)
    yaml_config = manager.load(yaml_path.stem)
    return manager.to_box_config(yaml_config)


def get_preset_config(preset_name: str) -> BoxConfig:
    """Get BoxConfig from named preset."""
    if preset_name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
    
    yaml_config = PRESETS[preset_name]
    manager = ConfigManager()
    return manager.to_box_config(yaml_config)


def main():
    """Main entry point."""
    # Parse arguments after '--' separator
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(
        description="Generate parametric storage box for 3D printing"
    )
    parser.add_argument(
        "--preset",
        choices=["mvp", "smarthome_desk", "workshop_tools", "medical_sealed"],
        help="Use preset configuration"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Load YAML configuration file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./output"),
        help="Output directory for STL files"
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Generate only test kit pieces"
    )
    parser.add_argument(
        "--width", type=float, default=200.0,
        help="Box width in mm (default: 200)"
    )
    parser.add_argument(
        "--depth", type=float, default=220.0,
        help="Box depth in mm (default: 220)"
    )
    parser.add_argument(
        "--height", type=float, default=80.0,
        help="Box height in mm (default: 80)"
    )
    parser.add_argument(
        "--style",
        choices=["nordic", "techno", "bauhaus", "organic",
                 "parametric", "stealth", "belovodie"],
        default="nordic",
        help="Design style (default: nordic)"
    )
    
    args = parser.parse_args(argv)
    
    # Load configuration
    if args.preset:
        print(f"Using preset: {args.preset}")
        config = get_preset_config(args.preset)
    elif args.config:
        print(f"Loading config: {args.config}")
        config = load_config_from_yaml(args.config)
    else:
        # Use command line arguments
        print("Using command line parameters")
        config = BoxConfig(
            width=args.width,
            depth=args.depth,
            height=args.height,
            design=DesignStyle(args.style),
        )
    
    # Generate
    if args.test_only:
        generate_test_only(config, args.output)
    else:
        generate_storage_box(config, args.output)


# Interactive mode for Blender scripting
def generate_interactive(
    preset: str = "mvp",
    output_dir: str = "./output",
) -> dict:
    """
    Generate storage box interactively from Blender.
    
    Use this function when running as a Blender script:
    
        import storage_box
        storage_box.generate_interactive("workshop_tools", "./my_output")
    
    Args:
        preset: Preset name or "custom" for default config
        output_dir: Output directory path
    
    Returns:
        Dict of generated component objects
    """
    if preset == "custom":
        config = BoxConfig()
    else:
        config = get_preset_config(preset)
    
    return generate_storage_box(config, Path(output_dir))


if __name__ == "__main__":
    main()
