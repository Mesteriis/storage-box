"""
DesignTokens - Visual style parameters.

Unified design language for all box components.
Each style has consistent tokens for geometry and decoration.
"""

from dataclasses import dataclass, field
from typing import Dict

from .enums import DesignStyle


@dataclass
class DesignTokens:
    """Parameters for visual style."""
    
    # Geometry
    radius_outer: float = 5.0       # External corners
    radius_inner: float = 2.0       # Internal corners (fillet)
    chamfer: float = 0.0            # Chamfer width
    chamfer_secondary: float = 0.0  # Second chamfer (Belovodye)
    chamfer_secondary_angle: float = 22.0  # Second chamfer angle
    
    # Grooves/patterns
    groove_width: float = 0.0       # Decorative groove width
    groove_depth: float = 0.0       # Groove depth
    pattern_type: str = "none"      # Pattern type
    pattern_params: Dict = field(default_factory=dict)  # Pattern parameters
    
    # Handle
    handle_profile: str = "hook"            # Handle profile
    handle_inner_radius: float = 2.0        # Inner radius (required >= 2mm)
    handle_tactile_mark: bool = False       # Tactile marker
    handle_width: float = 60.0              # Handle width
    handle_height: float = 15.0             # Handle height
    
    # Label frame
    label_frame_style: str = "flush"        # flush, raised, recessed, recessed_portal
    label_frame_width: float = 2.0          # Frame width
    label_shadow_gap: float = 0.0           # Shadow gap around label
    
    # Belovodye specifics
    shadow_gap: float = 0.0                 # Shadow gap around front
    version_mark: bool = False              # BV-x.x mark on bottom
    rune_key: bool = False                  # Rune-shaped stacking key
    rivet_dots: bool = False                # Decorative rivet dots
    
    @classmethod
    def from_style(cls, style: DesignStyle, wall: float = 2.0) -> "DesignTokens":
        """Factory method to create tokens from style."""
        factories = {
            DesignStyle.NORDIC: cls._nordic_tokens,
            DesignStyle.TECHNO: cls._techno_tokens,
            DesignStyle.BAUHAUS: cls._bauhaus_tokens,
            DesignStyle.ORGANIC: cls._organic_tokens,
            DesignStyle.PARAMETRIC: cls._parametric_tokens,
            DesignStyle.STEALTH: cls._stealth_tokens,
            DesignStyle.BELOVODIE: cls._belovodie_tokens,
        }
        factory = factories.get(style, cls._nordic_tokens)
        return factory(wall)
    
    @classmethod
    def _nordic_tokens(cls, wall: float) -> "DesignTokens":
        """Scandinavian minimalism: soft corners, clean lines."""
        return cls(
            radius_outer=5.0,
            radius_inner=wall * 0.6,
            chamfer=0.0,
            groove_width=0.0,
            groove_depth=0.0,
            pattern_type="none",
            pattern_params={},
            handle_profile="hidden_bottom",
            handle_inner_radius=3.0,
            handle_width=60.0,
            handle_height=12.0,
            label_frame_style="flush",
            label_frame_width=2.0,
            shadow_gap=0.0,
        )
    
    @classmethod
    def _techno_tokens(cls, wall: float) -> "DesignTokens":
        """Techno-futurism: 45° chamfers, accent lines."""
        return cls(
            radius_outer=0.0,
            radius_inner=2.0,
            chamfer=2.0,
            groove_width=0.8,
            groove_depth=0.5,
            pattern_type="lines",
            pattern_params={"spacing": 10, "angle": 0},
            handle_profile="horizontal_slot",
            handle_inner_radius=2.0,
            handle_width=80.0,
            handle_height=10.0,
            label_frame_style="recessed",
            label_frame_width=1.5,
            shadow_gap=0.3,
        )
    
    @classmethod
    def _bauhaus_tokens(cls, wall: float) -> "DesignTokens":
        """Functional modernism: geometry + contrast."""
        return cls(
            radius_outer=2.0,
            radius_inner=wall * 0.5,
            chamfer=0.0,
            groove_width=1.0,
            groove_depth=0.6,
            pattern_type="lines",
            pattern_params={"spacing": 10, "angle": 0},
            handle_profile="pinch",
            handle_inner_radius=2.5,
            handle_width=60.0,
            handle_height=12.0,
            label_frame_style="raised",
            label_frame_width=3.0,
            shadow_gap=0.0,
        )
    
    @classmethod
    def _organic_tokens(cls, wall: float) -> "DesignTokens":
        """Organic: smooth S-curves, natural forms."""
        return cls(
            radius_outer=min(wall * 5, 15.0),  # 10% of min dimension
            radius_inner=wall * 0.8,
            chamfer=0.0,
            groove_width=0.0,
            groove_depth=0.0,
            pattern_type="wave",
            pattern_params={"amplitude": 1.5, "period": 20},
            handle_profile="wave",
            handle_inner_radius=4.0,
            handle_width=70.0,
            handle_height=15.0,
            label_frame_style="flush",
            label_frame_width=2.5,
            shadow_gap=0.0,
        )
    
    @classmethod
    def _parametric_tokens(cls, wall: float) -> "DesignTokens":
        """Parametric: wave patterns, flowing forms."""
        return cls(
            radius_outer=8.0,
            radius_inner=wall * 0.7,
            chamfer=0.0,
            groove_width=0.0,
            groove_depth=0.0,
            pattern_type="sine_wave",
            pattern_params={"amplitude": 1.5, "period": 20, "phase": 0},
            handle_profile="hook",
            handle_inner_radius=3.0,
            handle_width=60.0,
            handle_height=20.0,
            label_frame_style="flush",
            label_frame_width=2.0,
            shadow_gap=0.0,
        )
    
    @classmethod
    def _stealth_tokens(cls, wall: float) -> "DesignTokens":
        """Stealth: sharp edges, hidden connections."""
        return cls(
            radius_outer=0.0,
            radius_inner=1.5,
            chamfer=1.0,
            groove_width=0.0,
            groove_depth=0.0,
            pattern_type="none",
            pattern_params={},
            handle_profile="invisible",
            handle_inner_radius=2.0,
            handle_width=0.0,  # Touch-latch
            handle_height=0.0,
            label_frame_style="recessed",
            label_frame_width=1.0,
            shadow_gap=0.3,
        )
    
    @classmethod
    def _belovodie_tokens(cls, wall: float) -> "DesignTokens":
        """
        Belovodye: warm techno-sacral minimalism.
        
        Features:
        - Two-step chamfer ("sacral edge")
        - Rune patterns (only in 1 of 3 zones!)
        - Shadow gap around front panel
        - Version mark on bottom
        """
        return cls(
            radius_outer=5.0,
            radius_inner=wall * 0.7,
            chamfer=1.2,  # Two-step!
            chamfer_secondary=0.4,
            chamfer_secondary_angle=22,
            groove_width=0.8,
            groove_depth=0.35,  # Inset only!
            pattern_type="runes",
            pattern_params={
                "motif": "chevron_rune",
                "spacing": 8,
                "band_height": 14,
                "band_position": "back_edge",
            },
            handle_profile="hidden_hook_rune",
            handle_inner_radius=2.5,
            handle_tactile_mark=True,
            handle_width=60.0,
            handle_height=12.0,
            label_frame_style="recessed_portal",
            label_frame_width=2.0,
            label_shadow_gap=0.3,
            shadow_gap=0.4,
            version_mark=True,
            rune_key=True,
            rivet_dots=True,
        )
    
    def apply_print_mode(self, mode: str) -> "DesignTokens":
        """Adjust tokens based on print mode."""
        if mode == "draft":
            # Simplify for fast printing
            return DesignTokens(
                radius_outer=self.radius_outer,
                radius_inner=self.radius_inner,
                chamfer=0.0,  # Skip chamfer
                chamfer_secondary=0.0,
                groove_width=0.0,  # Skip grooves
                groove_depth=0.0,
                pattern_type="none",  # Skip patterns
                pattern_params={},
                handle_profile=self.handle_profile,
                handle_inner_radius=self.handle_inner_radius,
                handle_width=self.handle_width,
                handle_height=self.handle_height,
                label_frame_style="flush",  # Simple label
                label_frame_width=self.label_frame_width,
                shadow_gap=0.0,  # Skip shadow gap
            )
        elif mode == "premium":
            # All details enabled (already set)
            return self
        else:
            # Normal - as-is
            return self


# Belovodye preset configurations
BELOVODIE_PRESETS = {
    "desk": {
        "colors": {"body": "mist_white", "accent": "emerald_deep"},
        "pattern": {"motif": "knot_line", "position": "label_frame"},
        "handle": "hidden_hook_rune",
    },
    "workshop": {
        "colors": {"body": "obsidian", "accent": "bronze_warm"},
        "pattern": {"motif": "chevron_rune", "position": "back_edge"},
        "handle": "rune_slot",
    },
    "med": {
        "colors": {"body": "stone_sand", "accent": "frost_blue"},
        "pattern": {"motif": "none"},
        "handle": "hidden_hook_rune",
        "sealed": True,
    },
    "sacred": {
        "colors": {"body": "obsidian", "accent": "bronze_warm"},
        "pattern": {"motif": "chevron_rune", "position": "back_edge"},
        "handle": "rune_slot",
        "rivet_dots": True,
        "rune_key": True,
    },
}
