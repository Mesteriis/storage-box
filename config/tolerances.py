"""
ToleranceProfile - Material-specific tolerance calculations.

Handles different tolerance requirements for various
connection types and materials.
"""

from dataclasses import dataclass
from typing import Dict

from .enums import MaterialType, PrinterProfile


@dataclass
class ToleranceProfile:
    """Material and printer specific tolerances."""
    
    material: MaterialType
    printer: PrinterProfile
    
    # Base tolerances per material
    BASE_TOLERANCES = {
        MaterialType.HYPER_PLA: 0.30,
        MaterialType.PETG: 0.40,
        MaterialType.ABS: 0.35,
    }
    
    # Printer modifiers
    PRINTER_MODIFIERS = {
        PrinterProfile.CREALITY_K1C: 1.0,   # Well calibrated
        PrinterProfile.GENERIC_FDM: 1.1,    # Add 10% margin
        PrinterProfile.HIGH_DETAIL: 0.85,   # Tighter with fine layer
    }
    
    @property
    def base(self) -> float:
        """Base tolerance for current material."""
        return self.BASE_TOLERANCES[self.material]
    
    @property
    def modifier(self) -> float:
        """Printer-specific modifier."""
        return self.PRINTER_MODIFIERS[self.printer]
    
    @property
    def slide(self) -> float:
        """Tolerance for drawer/rail sliding fit."""
        return self.base * self.modifier
    
    @property
    def snap(self) -> float:
        """Tolerance for snap-fit connections (tighter)."""
        return self.base * self.modifier * 0.7
    
    @property
    def pressfit(self) -> float:
        """Tolerance for press-fit (magnets, NFC)."""
        return self.base * self.modifier * 0.5
    
    @property
    def loose(self) -> float:
        """Tolerance for loose/easy fit."""
        return self.base * self.modifier * 1.3
    
    def as_dict(self) -> Dict[str, float]:
        """Return all tolerances as dictionary."""
        return {
            "slide": self.slide,
            "snap": self.snap,
            "pressfit": self.pressfit,
            "loose": self.loose,
        }
    
    def for_clearance(self, clearance_type: str) -> float:
        """Get tolerance for specific clearance type."""
        return getattr(self, clearance_type, self.slide)


# Test kit clearance variants
TEST_KIT_CLEARANCES = {
    "tight": [0.20, 0.25, 0.30],    # For snap/pressfit testing
    "normal": [0.25, 0.30, 0.35],   # For rail testing
    "loose": [0.35, 0.40, 0.45],    # For loose fit testing
}

# Whisker test kit variants
WHISKER_TEST_KIT = {
    "soft_s": {"thickness": 0.8, "length": 12.0, "stiffness": "soft"},
    "soft_l": {"thickness": 0.8, "length": 18.0, "stiffness": "very_soft"},
    "med_s": {"thickness": 1.0, "length": 12.0, "stiffness": "medium"},
    "med_l": {"thickness": 1.0, "length": 18.0, "stiffness": "standard"},
    "firm_s": {"thickness": 1.2, "length": 12.0, "stiffness": "firm"},
    "firm_l": {"thickness": 1.2, "length": 18.0, "stiffness": "very_firm"},
}
