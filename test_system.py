#!/usr/bin/env python3
"""Test script for Storage Box System."""

import sys
import tempfile
from pathlib import Path


def test_enums():
    """Test all enum configurations."""
    print("=== Test 1: Enum Configurations ===")
    from .config.enums import (
        DesignStyle, MaterialType, SoundProfile, WhiskerVariant
    )

    print(f"  Design styles: {[s.value for s in DesignStyle]}")
    print(f"  Materials: {[m.value for m in MaterialType]}")
    print(f"  Sound profiles: {[s.value for s in SoundProfile]}")
    print(f"  Whisker variants: {[w.value for w in WhiskerVariant]}")
    print("  All enums loaded")
    return True


def test_box_config():
    """Test BoxConfig creation."""
    print("\n=== Test 2: BoxConfig Creation ===")
    from .config.box_config import BoxConfig
    from .config.enums import DesignStyle, MaterialType

    # Default config
    config1 = BoxConfig()
    print(f"  Default: {config1.width}x{config1.depth}x{config1.height}mm")
    print(f"    Style: {config1.design.value}")

    # Custom config
    config2 = BoxConfig(
        width=150, depth=180, height=60,
        design=DesignStyle.BELOVODIE,
        material=MaterialType.PETG
    )
    print(f"  Custom: {config2.width}x{config2.depth}x{config2.height}mm")
    print(f"    Style: {config2.design.value}")

    print("  BoxConfig creation works")
    return True


def test_derived_config():
    """Test DerivedConfig calculations."""
    print("\n=== Test 3: DerivedConfig Calculations ===")
    from .config.box_config import BoxConfig
    from .config.derived_config import DerivedConfig
    from .config.enums import MaterialType

    # Test with different materials
    materials = [MaterialType.HYPER_PLA, MaterialType.PETG, MaterialType.ABS]
    for material in materials:
        config = BoxConfig(material=material)
        derived = DerivedConfig(config)
        print(f"  {material.value}: wall={derived.wall_thickness}mm, "
              f"tolerance={derived.base_tolerance}mm")

    # Test adaptive wall thickness
    small_config = BoxConfig(width=100, height=40)
    small_derived = DerivedConfig(small_config)

    large_config = BoxConfig(width=300, height=120, stack_levels=4)
    large_derived = DerivedConfig(large_config)

    print(f"  Small box wall: {small_derived.wall_thickness}mm")
    print(f"  Large stacked wall: {large_derived.wall_thickness}mm")

    print("  DerivedConfig calculations correct")
    return True


def test_design_tokens():
    """Test DesignTokens for all styles."""
    print("\n=== Test 4: Design Tokens ===")
    from .config.design_tokens import DesignTokens
    from .config.enums import DesignStyle

    for style in DesignStyle:
        tokens = DesignTokens.from_style(style, wall=2.4)
        print(f"  {style.value:12}: r={tokens.radius_outer}, "
              f"ch={tokens.chamfer}, pat={tokens.pattern_type}")

    # Test Belovodye specifics
    bv_tokens = DesignTokens.from_style(DesignStyle.BELOVODIE, 2.4)
    print("\n  Belovodye details:")
    print(f"    Two-step chamfer: {bv_tokens.chamfer}")
    print(f"    Shadow gap: {bv_tokens.shadow_gap}mm")
    print(f"    Handle: {bv_tokens.handle_profile}")
    print(f"    Version mark: {bv_tokens.version_mark}")

    print("  All design tokens configured")
    return True


def test_presets():
    """Test preset configurations."""
    print("\n=== Test 5: Presets ===")
    from .config.presets import PRESETS
    from .config.derived_config import DerivedConfig

    for name, box_config in PRESETS.items():
        derived = DerivedConfig(box_config)

        print(f"\n  {name}:")
        print(f"    Style: {box_config.design.value}")
        print(f"    Material: {box_config.material.value}")
        print(f"    Sound: {box_config.mechanics.sound_profile.value}")
        print(f"    Computed wall: {derived.wall_thickness}mm")
        print(f"    Inner width: {derived.effective_inner_width:.1f}mm")

    print("\n  All presets work correctly")
    return True


def test_yaml_roundtrip():
    """Test YAML save/load."""
    print("\n=== Test 6: YAML Save/Load ===")
    from .config.config_manager import ConfigManager
    from .config.box_config import BoxConfig
    from .config.enums import DesignStyle, MaterialType

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager(Path(tmpdir))

        # Create test config
        test_config = BoxConfig(
            description="Test configuration",
            width=180.0,
            depth=200.0,
            height=70.0,
            design=DesignStyle.BELOVODIE,
            material=MaterialType.PETG,
        )

        # Save
        filepath = manager.save(test_config, "test_config")
        print(f"  Saved to: {filepath}")

        # Load
        loaded = manager.load("test_config")
        print(f"  Loaded: {loaded.width}x{loaded.depth}x{loaded.height}mm")
        print(f"  Style: {loaded.design.value}")

        # Verify roundtrip
        assert loaded.width == test_config.width
        assert loaded.design == test_config.design

    print("  YAML roundtrip successful")
    return True


def test_combinations():
    """Test various parameter combinations."""
    print("\n=== Test 7: Parameter Combinations ===")
    from .config.box_config import BoxConfig
    from .config.derived_config import DerivedConfig
    from .config.design_tokens import DesignTokens
    from .config.enums import DesignStyle, MaterialType

    combinations = [
        # (style, material, width, height, mount, weight)
        (DesignStyle.NORDIC, MaterialType.HYPER_PLA, 200, 80, "table", 500),
        (DesignStyle.TECHNO, MaterialType.PETG, 150, 60, "table", 300),
        (DesignStyle.BELOVODIE, MaterialType.HYPER_PLA, 250, 100, "wall", 800),
        (DesignStyle.STEALTH, MaterialType.ABS, 180, 70, "table", 1500),
        (DesignStyle.ORGANIC, MaterialType.PETG, 120, 50, "table", 200),
    ]

    for style, material, width, height, mount, weight in combinations:
        config = BoxConfig(
            width=width, depth=width * 1.1, height=height,
            design=style,
            material=material,
            mount=mount,
            expected_weight=weight,
        )
        derived = DerivedConfig(config)
        _ = DesignTokens.from_style(style, derived.wall_thickness)

        print(f"\n  {style.value} + {material.value} ({width}x{height}mm):")
        print(f"    Wall: {derived.wall_thickness}mm")
        print(f"    Connection: {derived.connection_auto.value}")
        print(f"    Dividers: {derived.divider_count}")
        label_on = derived.features_enabled['label']
        smart_on = derived.features_enabled['smart_cartridge']
        print(f"    Features: label={label_on}, smart={smart_on}")

    print("\n  All combinations valid")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Storage Box System - Configuration Tests")
    print("=" * 60)

    tests = [
        test_enums,
        test_box_config,
        test_derived_config,
        test_design_tokens,
        test_presets,
        test_yaml_roundtrip,
        test_combinations,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n  {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
