"""
DerivedConfig - Computed parameters from BoxConfig.

All dimensional calculations, tolerances, and feature flags
are computed here based on user input.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

from .box_config import BoxConfig
from .enums import (
    MaterialType,
    DividerLayout,
    ConnectionType,
    PrintMode,
)


@dataclass
class DerivedConfig:
    """
    Computed parameters ready for geometry generation.
    
    All calculations based on BoxConfig input.
    Validates constraints and provides sensible defaults.
    """
    
    config: BoxConfig
    
    # Boundaries (validation)
    MIN_WALL = 1.6
    MAX_WALL = 4.8
    MIN_CLEARANCE = 0.15
    MIN_INNER_WIDTH = 40  # Minimum for drawer
    
    # Standard dimensions
    RAIL_WIDTH = 5.0  # Rail width mm
    RAIL_DEPTH = 4.0  # Rail depth mm
    DUST_LIP = 1.0    # Dust lip height mm
    DUST_SHELF = 0.8  # Dust shelf on drawer mm
    RAIL_WINDOW_SPACING = 35.0  # Rail window spacing mm
    
    # Stops
    STOP1_THICKNESS = 1.2  # PETG spring tab mm
    STOP1_LENGTH = 8.0     # Tab length mm
    STOP2_HEIGHT = 3.0     # Hard stop mm
    RELEASE_SLOT_W = 15.0  # Release slot width mm
    RELEASE_SLOT_H = 5.0   # Release slot height mm
    
    # Smart cartridge
    CARTRIDGE_W = 30.0     # Cartridge width mm
    CARTRIDGE_H = 25.0     # Cartridge height mm
    CARTRIDGE_D = 12.0     # Cartridge depth mm
    
    # Magnet pocket
    MAGNET_DIA = 6.1       # Magnet pocket diameter (pressfit) mm
    MAGNET_DEPTH = 3.1     # Magnet pocket depth mm
    
    # Universal slot (dividers/inserts)
    SLOT_WIDTH = 2.4       # Universal slot width mm
    SLOT_DEPTH = 3.0       # Universal slot depth mm
    
    @property
    def base_tolerance(self) -> float:
        """Base tolerance for material."""
        tolerances = {
            MaterialType.HYPER_PLA: 0.30,
            MaterialType.PETG: 0.40,
            MaterialType.ABS: 0.35,
        }
        return tolerances[self.config.material]
    
    @property
    def tolerances(self) -> Dict[str, float]:
        """Separate tolerances by use case."""
        base = self.base_tolerance
        return {
            "slide": base,              # Drawer/rails
            "snap": base * 0.7,         # Snap-fits (tighter)
            "pressfit": base * 0.5,     # Magnets/NFC (very tight)
            "loose": base * 1.3,        # Easy fit
        }
    
    @property
    def wall_thickness(self) -> float:
        """Adaptive wall thickness based on size and load."""
        base = 2.0
        
        # Reinforce based on side wall area
        area = self.config.width * self.config.height / 1000  # cm²
        if area > 160:      # > 200×80
            base = 3.2
        elif area > 100:    # > 200×50
            base = 2.4
        
        # Reinforce for stacking
        if self.config.stack_levels > 2:
            base += 0.4
        
        # Reinforce for wall mount
        if self.config.mount == "wall":
            base += 0.4
        
        # Round to nozzle multiple (0.4mm)
        return round(base / 0.4) * 0.4
    
    @property
    def floor_thickness(self) -> float:
        """Floor thickness (slightly thicker than walls)."""
        return max(1.6, self.wall_thickness * 0.8)
    
    @property
    def effective_inner_width(self) -> float:
        """Real internal width after rails and tolerances."""
        return (
            self.config.width
            - 2 * self.wall_thickness
            - 2 * self.RAIL_WIDTH
            - 2 * self.tolerances["slide"]
        )
    
    @property
    def effective_inner_depth(self) -> float:
        """Real internal depth."""
        return self.config.depth - 2 * self.wall_thickness
    
    @property
    def effective_inner_height(self) -> float:
        """Real internal height (drawer height)."""
        return (
            self.config.height
            - self.floor_thickness  # Shell floor
            - 2.0                   # Top clearance
        )
    
    @property
    def drawer_width(self) -> float:
        """Drawer outer width - fits between rails.
        
        Note: effective_inner_width already accounts for:
        - wall thickness
        - rail width  
        - slide tolerances
        
        So drawer just uses this value directly.
        """
        return self.effective_inner_width
    
    @property
    def drawer_depth(self) -> float:
        """Drawer outer depth."""
        return self.effective_inner_depth - 10.0  # Front clearance
    
    @property
    def drawer_height(self) -> float:
        """Drawer outer height."""
        return self.effective_inner_height - self.tolerances["slide"]
    
    @property
    def drawer_inner_depth(self) -> float:
        """Drawer internal depth for content."""
        return self.drawer_height - self.floor_thickness - 2.0
    
    @property
    def front_panel_thickness(self) -> float:
        """Front panel thickness."""
        return max(2.0, self.wall_thickness)
    
    @property
    def divider_count(self) -> Tuple[int, int]:
        """Auto-calculate divider count based on target cell size."""
        if self.config.dividers == DividerLayout.NONE:
            return (0, 0)
        
        if self.config.dividers != DividerLayout.AUTO:
            # Fixed layout mapping
            layouts = {
                DividerLayout.GRID_2X2: (1, 1),
                DividerLayout.GRID_2X3: (1, 2),
                DividerLayout.GRID_3X3: (2, 2),
            }
            return layouts.get(self.config.dividers, (0, 0))
        
        # Auto-calculate
        target_w, target_d = self.config.target_cell_size
        inner_w = self.drawer_width - 2 * self.wall_thickness
        inner_d = self.drawer_depth - 2 * self.wall_thickness
        
        cols = max(0, round(inner_w / target_w) - 1)
        rows = max(0, round(inner_d / target_d) - 1)
        
        # Validate: don't create too small cells
        while cols > 0 and inner_w / (cols + 1) < 25:
            cols -= 1
        while rows > 0 and inner_d / (rows + 1) < 30:
            rows -= 1
        
        return (cols, rows)
    
    @property
    def features_enabled(self) -> Dict[str, bool]:
        """Auto-disable features for small sizes."""
        inner_w = self.effective_inner_width
        return {
            "label": inner_w >= 60,
            "led_slot": inner_w >= 100,
            "dividers": inner_w >= 50,
            "smart_cartridge": inner_w >= 80,
            "handle_large": inner_w >= 80,
            "shadow_gap": self.config.print_mode != PrintMode.DRAFT,
            "guide_cones": True,
            "service_channel": self.config.mechanics.service_channel,
        }
    
    @property
    def connection_auto(self) -> ConnectionType:
        """Smart connection type selection."""
        cfg = self.config
        
        # Wall mount -> magnets or clips
        if cfg.mount == "wall":
            return ConnectionType.MAGNET if cfg.width > 150 else ConnectionType.CLIP
        
        # Heavy content -> dovetail
        if cfg.expected_weight > 1000:
            return ConnectionType.DOVETAIL
        
        # Tall stack -> dovetail
        if cfg.stack_levels > 3:
            return ConnectionType.DOVETAIL
        
        # Small -> clips
        if cfg.height < 50:
            return ConnectionType.CLIP
        
        # Default to user selection
        return cfg.connection
    
    @property
    def lead_in_length(self) -> float:
        """Lead-in zone length for anti-jam."""
        return min(15.0, self.effective_inner_depth * 0.1)
    
    @property
    def lead_in_tolerance(self) -> float:
        """Extra tolerance at lead-in zone."""
        return 0.1  # +0.1mm at entry
    
    @property
    def acoustic_tab_dims(self) -> Tuple[float, float, float]:
        """Acoustic resonator tab dimensions (w, h, d)."""
        return (0.8, 6.0, 18.0)
    
    @property
    def whisker_params(self) -> Dict[str, float]:
        """Spring whisker parameters based on variant."""
        variants = {
            "soft_s":  {"thickness": 0.8, "length": 12.0},
            "soft_l":  {"thickness": 0.8, "length": 18.0},
            "med_s":   {"thickness": 1.0, "length": 12.0},
            "med_l":   {"thickness": 1.0, "length": 18.0},
            "firm_s":  {"thickness": 1.2, "length": 12.0},
            "firm_l":  {"thickness": 1.2, "length": 18.0},
        }
        return variants.get(
            self.config.mechanics.whisker_variant.value,
            variants["med_l"]
        )
    
    @property
    def shadow_gap_size(self) -> float:
        """Shadow gap size based on print mode."""
        if self.config.print_mode == PrintMode.DRAFT:
            return 0.0
        elif self.config.print_mode == PrintMode.PREMIUM:
            return 0.5
        return 0.4
    
    @property
    def pattern_params(self) -> Dict:
        """Pattern parameters for Belovodye."""
        if self.config.pattern.type.value == "none":
            return {}
        
        return {
            "type": self.config.pattern.type.value,
            "position": self.config.pattern.position.value,
            "spacing": self.config.pattern.spacing,
            "band_height": self.config.pattern.band_height,
            "groove_depth": self.config.pattern.groove_depth,
            "groove_width": self.config.pattern.groove_width,
        }
    
    def validate(self) -> list[str]:
        """Validate derived parameters and return warnings."""
        warnings = []
        
        # Wall thickness bounds
        if self.wall_thickness < self.MIN_WALL:
            warnings.append(f"Wall thickness {self.wall_thickness} < minimum {self.MIN_WALL}")
        if self.wall_thickness > self.MAX_WALL:
            warnings.append(f"Wall thickness {self.wall_thickness} > maximum {self.MAX_WALL}")
        
        # Inner width check
        if self.effective_inner_width < self.MIN_INNER_WIDTH:
            warnings.append(f"Inner width {self.effective_inner_width} < minimum {self.MIN_INNER_WIDTH}")
        
        # Drawer depth check
        if self.drawer_inner_depth < 15:
            warnings.append(f"Drawer inner depth {self.drawer_inner_depth} too shallow")
        
        return warnings + self.config.validate()
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        return f"""
Storage Box Configuration Summary
=================================
External: {self.config.width} × {self.config.depth} × {self.config.height} mm
Internal: {self.effective_inner_width:.1f} × {self.effective_inner_depth:.1f} × {self.effective_inner_height:.1f} mm
Drawer: {self.drawer_width:.1f} × {self.drawer_depth:.1f} × {self.drawer_height:.1f} mm

Wall thickness: {self.wall_thickness} mm
Tolerance (slide): {self.tolerances['slide']} mm
Tolerance (snap): {self.tolerances['snap']} mm

Dividers: {self.divider_count[0]}×{self.divider_count[1]}
Connection: {self.connection_auto.value}

Features enabled:
  - Label: {self.features_enabled['label']}
  - Smart cartridge: {self.features_enabled['smart_cartridge']}
  - Shadow gap: {self.features_enabled['shadow_gap']}
  - Service channel: {self.features_enabled['service_channel']}
"""
