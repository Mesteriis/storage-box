#!/usr/bin/env python3
"""
Test script for validating mathematical calculations.

Verifies that all dimensions are correctly calculated and
that the drawer will physically fit inside the shell.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from config import BoxConfig, DerivedConfig
from config.enums import DesignStyle, MaterialType

def test_basic_dimensions():
    """Test basic 200x220x80 box."""
    print("=" * 60)
    print("TEST 1: Basic Dimensions (200×220×80, HYPER_PLA)")
    print("=" * 60)
    
    config = BoxConfig(
        width=200,
        depth=220,
        height=80,
        design=DesignStyle.NORDIC,
        material=MaterialType.HYPER_PLA
    )
    
    derived = DerivedConfig(config)
    
    print("\n" + derived.summary())
    
    # Validate dimensions
    print("\n" + "=" * 60)
    print("VALIDATION CHECKS")
    print("=" * 60)
    
    # Check 1: Drawer width fits between rails
    assert derived.drawer_width <= derived.space_between_rails, \
        f"Drawer too wide! {derived.drawer_width} > {derived.space_between_rails}"
    print(f"✓ Drawer width ({derived.drawer_width:.1f}mm) fits between rails ({derived.space_between_rails:.1f}mm)")
    
    # Check 2: Drawer body width is wider (before V-grooves)
    assert derived.drawer_body_width > derived.drawer_width, \
        "Drawer body should be wider than final width!"
    print(f"✓ Drawer body ({derived.drawer_body_width:.1f}mm) > final width ({derived.drawer_width:.1f}mm)")
    
    # Check 3: Drawer depth fits inside shell
    assert derived.drawer_depth < derived.shell_inner_depth, \
        "Drawer too deep!"
    print(f"✓ Drawer depth ({derived.drawer_depth:.1f}mm) < shell inner ({derived.shell_inner_depth:.1f}mm)")
    
    # Check 4: Drawer height fits inside shell (accounting for rail height)
    max_drawer_height = derived.config.height - derived.rail_height_from_floor - 5
    assert derived.drawer_height <= max_drawer_height, \
        f"Drawer too tall! {derived.drawer_height} > {max_drawer_height}"
    print(f"✓ Drawer height ({derived.drawer_height:.1f}mm) fits above rails")
    
    # Check 5: Front opening is large enough for drawer
    assert derived.front_opening_width >= derived.drawer_width, \
        "Front opening too narrow!"
    assert derived.front_opening_height >= derived.drawer_height, \
        "Front opening too short!"
    print(f"✓ Front opening ({derived.front_opening_width:.1f}×{derived.front_opening_height:.1f}mm) " \
          f">= drawer ({derived.drawer_width:.1f}×{derived.drawer_height:.1f}mm)")
    
    # Check 6: Floor is not thinner than walls
    assert derived.floor_thickness >= derived.wall_thickness, \
        "Floor should not be thinner than walls!"
    print(f"✓ Floor ({derived.floor_thickness}mm) >= walls ({derived.wall_thickness}mm)")
    
    # Check 7: Drawer inner dimensions are positive
    assert derived.drawer_inner_width > 0, "Drawer inner width negative!"
    assert derived.drawer_inner_depth > 0, "Drawer inner depth negative!"
    assert derived.drawer_inner_height > 0, "Drawer inner height negative!"
    print(f"✓ Drawer internal space: {derived.drawer_inner_width:.1f}×{derived.drawer_inner_depth:.1f}×{derived.drawer_inner_height:.1f}mm")
    
    # Check 8: Tolerances are reasonable
    tolerance = derived.tolerances["slide"]
    assert 0.15 <= tolerance <= 0.5, "Tolerance out of range!"
    print(f"✓ Slide tolerance: {tolerance}mm (reasonable)")
    
    # Check 9: Warnings
    warnings = derived.validate()
    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\n✓ No warnings")
    
    print("\n" + "=" * 60)
    print("TEST 1 PASSED ✓")
    print("=" * 60)


def test_small_box():
    """Test small box (100x100x40)."""
    print("\n\n" + "=" * 60)
    print("TEST 2: Small Box (100×100×40, PETG)")
    print("=" * 60)
    
    config = BoxConfig(
        width=100,
        depth=100,
        height=40,
        design=DesignStyle.NORDIC,
        material=MaterialType.PETG
    )
    
    derived = DerivedConfig(config)
    
    print("\n" + derived.summary())
    
    # Check critical dimensions
    assert derived.drawer_width > 0, "Drawer width must be positive!"
    assert derived.drawer_height > 0, "Drawer height must be positive!"
    assert derived.drawer_inner_width > 20, "Drawer too narrow for use!"
    
    print("\n✓ Small box dimensions valid")


def test_large_box():
    """Test large box (300x250x100)."""
    print("\n\n" + "=" * 60)
    print("TEST 3: Large Box (300×250×100, ABS)")
    print("=" * 60)
    
    config = BoxConfig(
        width=300,
        depth=250,
        height=100,  # Area = 300*100/1000 = 30 cm², stack +0.4 = 2.4mm
        design=DesignStyle.BELOVODIE,
        material=MaterialType.ABS,
        stack_levels=3
    )
    
    derived = DerivedConfig(config)
    
    print("\n" + derived.summary())
    
    # Check wall reinforcement for stacked box
    assert derived.wall_thickness >= 2.4, "Stacked box needs reinforcement!"
    print(f"\n✓ Stacked box has reinforced walls: {derived.wall_thickness}mm")


def test_mathematical_consistency():
    """Test mathematical relationships."""
    print("\n\n" + "=" * 60)
    print("TEST 4: Mathematical Consistency")
    print("=" * 60)
    
    config = BoxConfig(width=200, depth=220, height=80)
    d = DerivedConfig(config)
    
    # Shell inner = external - walls
    assert abs(d.shell_inner_width - (d.config.width - 2*d.wall_thickness)) < 0.01
    assert abs(d.shell_inner_depth - (d.config.depth - 2*d.wall_thickness)) < 0.01
    assert abs(d.shell_inner_height - (d.config.height - d.floor_thickness)) < 0.01
    print("✓ Shell inner dimensions correct")
    
    # Space between rails = shell_inner_width - 2*RAIL_WIDTH
    assert abs(d.space_between_rails - (d.shell_inner_width - 2*d.RAIL_WIDTH)) < 0.01
    print("✓ Space between rails correct")
    
    # Drawer width = space_between_rails - 2*tolerance
    assert abs(d.drawer_width - (d.space_between_rails - 2*d.tolerances["slide"])) < 0.01
    print("✓ Drawer width correct")
    
    # Drawer body width = drawer_width + 2*v_groove_depth
    v_groove_depth = 2.0
    expected_body = d.drawer_width + 2*v_groove_depth
    assert abs(d.drawer_body_width - expected_body) < 0.01
    print("✓ Drawer body width correct")
    
    # Drawer inner width = drawer_width - 2*drawer_wall
    expected_inner_w = d.drawer_width - 2*d.drawer_wall_thickness
    assert abs(d.drawer_inner_width - expected_inner_w) < 0.01
    print("✓ Drawer inner width correct")
    
    print("\n✓ All mathematical relationships verified!")


def main():
    """Run all tests."""
    try:
        test_basic_dimensions()
        test_small_box()
        test_large_box()
        test_mathematical_consistency()
        
        print("\n\n" + "=" * 60)
        print("ALL TESTS PASSED ✓✓✓")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
