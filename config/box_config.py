"""
BoxConfig - Input parameters for Storage Box generation.

User specifies only external dimensions and preferences,
everything else is calculated automatically.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional

from .enums import (
    DesignStyle,
    MaterialType,
    DividerLayout,
    DividerMode,
    ConnectionType,
    RailProfile,
    PrinterProfile,
    SoundProfile,
    HandleMode,
    ShellGeometry,
    SmartCartridge,
    PrintMode,
    AntiWobbleType,
    WhiskerVariant,
    RunePattern,
    PatternPosition,
    BelovodieColor,
    BelovodiePreset,
)


@dataclass
class GeometryConfig:
    """Geometry configuration for shell shape."""
    shape: ShellGeometry = ShellGeometry.RECTANGULAR
    slope_angle: float = 15.0  # degrees
    slope_direction: str = "front"  # front, left, right
    maintain_back_vertical: bool = True  # back face always vertical


@dataclass
class MechanicsConfig:
    """Mechanics configuration for drawer operation."""
    rail_profile: RailProfile = RailProfile.V_PROFILE
    anti_wobble: AntiWobbleType = AntiWobbleType.SPRING_WHISKER
    whisker_variant: WhiskerVariant = WhiskerVariant.MED_L
    sound_profile: SoundProfile = SoundProfile.SOFT_CLICK
    service_channel: bool = False  # dusty mode blowout channel


@dataclass
class PatternConfig:
    """Pattern configuration for Belovodye style."""
    type: RunePattern = RunePattern.NONE
    position: PatternPosition = PatternPosition.BACK_EDGE
    spacing: float = 8.0  # mm
    band_height: float = 14.0  # mm
    groove_depth: float = 0.35  # mm (inset only!)
    groove_width: float = 0.8  # mm


@dataclass
class DetailsConfig:
    """Detail configuration for premium features."""
    shadow_gap: float = 0.4  # mm
    guide_cones: bool = True  # alignment cones at rail entry
    rune_key: bool = False  # rune-shaped stacking key
    rivet_dots: bool = False  # decorative rivet dots
    version_mark: bool = True  # BV-x.x mark on bottom


@dataclass
class BoxConfig:
    """
    Main configuration for Storage Box.
    
    User specifies external dimensions and preferences.
    Internal calculations are done by DerivedConfig.
    """
    
    # === Dimensions (user input) ===
    width: float = 200.0   # mm
    depth: float = 220.0   # mm
    height: float = 80.0   # mm
    
    # === Design ===
    design: DesignStyle = DesignStyle.NORDIC
    belovodie_preset: Optional[BelovodiePreset] = None
    color_body: BelovodieColor = BelovodieColor.MIST_WHITE
    color_accent: BelovodieColor = BelovodieColor.EMERALD_DEEP
    
    # === Material & Printing ===
    material: MaterialType = MaterialType.HYPER_PLA
    printer: PrinterProfile = PrinterProfile.CREALITY_K1C
    print_mode: PrintMode = PrintMode.NORMAL
    
    # === Dividers ===
    dividers: DividerLayout = DividerLayout.AUTO
    divider_mode: DividerMode = DividerMode.SNAP
    target_cell_size: Tuple[float, float] = (50.0, 50.0)  # mm
    
    # === Connections ===
    connection: ConnectionType = ConnectionType.DOVETAIL
    
    # === Context ===
    stack_levels: int = 1  # number of boxes in stack
    mount: str = "table"   # table / wall
    expected_weight: float = 500.0  # expected content weight, grams
    
    # === Handle ===
    handle_mode: HandleMode = HandleMode.HOOK
    handle_tactile_zone: bool = True
    
    # === Label ===
    label_frame_style: str = "recessed_portal"
    
    # === Smart features ===
    smart_cartridge: SmartCartridge = SmartCartridge.PLAIN
    hub_connector: bool = False
    
    # === Special versions ===
    sealed: bool = False  # O-profile seal groove
    
    # === Sub-configurations ===
    geometry: GeometryConfig = field(default_factory=GeometryConfig)
    mechanics: MechanicsConfig = field(default_factory=MechanicsConfig)
    pattern: PatternConfig = field(default_factory=PatternConfig)
    details: DetailsConfig = field(default_factory=DetailsConfig)
    
    # === Meta ===
    description: str = ""
    
    def __post_init__(self):
        """Apply Belovodye preset if specified."""
        if self.design == DesignStyle.BELOVODIE and self.belovodie_preset:
            self._apply_belovodie_preset()
    
    def _apply_belovodie_preset(self):
        """Apply Belovodye preset settings."""
        presets = {
            BelovodiePreset.DESK: {
                "color_body": BelovodieColor.MIST_WHITE,
                "color_accent": BelovodieColor.EMERALD_DEEP,
                "pattern_type": RunePattern.KNOT_LINE,
                "pattern_position": PatternPosition.LABEL_FRAME,
            },
            BelovodiePreset.WORKSHOP: {
                "color_body": BelovodieColor.OBSIDIAN,
                "color_accent": BelovodieColor.BRONZE_WARM,
                "pattern_type": RunePattern.CHEVRON_RUNE,
                "pattern_position": PatternPosition.BACK_EDGE,
            },
            BelovodiePreset.MED: {
                "color_body": BelovodieColor.STONE_SAND,
                "color_accent": BelovodieColor.FROST_BLUE,
                "pattern_type": RunePattern.NONE,
                "sealed": True,
            },
            BelovodiePreset.SACRED: {
                "color_body": BelovodieColor.OBSIDIAN,
                "color_accent": BelovodieColor.BRONZE_WARM,
                "pattern_type": RunePattern.CHEVRON_RUNE,
                "pattern_position": PatternPosition.BACK_EDGE,
                "rune_key": True,
                "rivet_dots": True,
            },
        }
        
        preset = presets.get(self.belovodie_preset, {})
        for key, value in preset.items():
            if key == "pattern_type":
                self.pattern.type = value
            elif key == "pattern_position":
                self.pattern.position = value
            elif key == "sealed":
                self.sealed = value
            elif key == "rune_key":
                self.details.rune_key = value
            elif key == "rivet_dots":
                self.details.rivet_dots = value
            elif hasattr(self, key):
                setattr(self, key, value)
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of warnings."""
        warnings = []
        
        # Size limits
        if self.width < 60:
            warnings.append("Width < 60mm may be too small for drawer")
        if self.width > 400:
            warnings.append("Width > 400mm may have warping issues")
        if self.depth < 80:
            warnings.append("Depth < 80mm may be too shallow")
        if self.height < 30:
            warnings.append("Height < 30mm very limited drawer depth")
        
        # Material + feature compatibility
        if self.sealed and self.material == MaterialType.HYPER_PLA:
            warnings.append("Sealed version recommended with PETG")
        
        # Pattern position rule (only 1 of 3)
        if self.pattern.type != RunePattern.NONE:
            if self.design != DesignStyle.BELOVODIE:
                warnings.append("Rune patterns only for BELOVODIE style")
        
        return warnings
