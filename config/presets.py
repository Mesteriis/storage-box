"""
Presets - Ready-made configurations for common scenarios.

Pre-configured BoxConfig instances for different use cases.
"""

from enum import Enum
from typing import Dict

from .box_config import (
    BoxConfig,
    MechanicsConfig,
    PatternConfig,
    DetailsConfig,
)
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
    RunePattern,
    PatternPosition,
    BelovodieColor,
    BelovodiePreset,
)


class BoxPreset(Enum):
    """Named presets for common use cases."""
    
    # Smart home
    SMARTHOME_DESK = "smarthome_desk"
    
    # Workshop
    WORKSHOP_TOOLS = "workshop_tools"
    
    # Medical/Optics
    MEDICAL_SEALED = "medical_sealed"
    
    # MVP (minimal)
    MVP = "mvp"
    
    # Standard presets by location
    ENTRYWAY_KEYS = "entryway_keys"
    DESK_TECH = "desk_tech"
    WORKSHOP_SCREWS = "workshop_screws"
    BATHROOM_MEDS = "bathroom_meds"


def create_smarthome_desk() -> BoxConfig:
    """K1C + Hyper PLA, quiet smart home (desk)."""
    return BoxConfig(
        width=200.0,
        depth=220.0,
        height=80.0,
        description="Quiet smart home: K1C + Hyper PLA, desktop",
        design=DesignStyle.BELOVODIE,
        belovodie_preset=BelovodiePreset.DESK,
        color_body=BelovodieColor.MIST_WHITE,
        color_accent=BelovodieColor.EMERALD_DEEP,
        material=MaterialType.HYPER_PLA,
        printer=PrinterProfile.CREALITY_K1C,
        print_mode=PrintMode.PREMIUM,
        dividers=DividerLayout.AUTO,
        divider_mode=DividerMode.SNAP,
        connection=ConnectionType.MAGNET,
        mount="table",
        handle_mode=HandleMode.HIDDEN_HOOK_RUNE,
        label_frame_style="recessed_portal",
        smart_cartridge=SmartCartridge.NFC_13MM,
        mechanics=MechanicsConfig(
            rail_profile=RailProfile.V_PROFILE,
            anti_wobble=AntiWobbleType.SPRING_WHISKER,
            sound_profile=SoundProfile.SILENT,
            service_channel=False,
        ),
        pattern=PatternConfig(
            type=RunePattern.KNOT_LINE,
            position=PatternPosition.LABEL_FRAME,
        ),
        details=DetailsConfig(
            shadow_gap=0.4,
            guide_cones=True,
        ),
    )


def create_workshop_tools() -> BoxConfig:
    """PETG workshop: tools, satisfying click."""
    return BoxConfig(
        width=200.0,
        depth=220.0,
        height=80.0,
        description="Workshop: PETG, tools, satisfying click",
        design=DesignStyle.BELOVODIE,
        belovodie_preset=BelovodiePreset.WORKSHOP,
        color_body=BelovodieColor.OBSIDIAN,
        color_accent=BelovodieColor.BRONZE_WARM,
        material=MaterialType.PETG,
        printer=PrinterProfile.CREALITY_K1C,
        print_mode=PrintMode.NORMAL,
        dividers=DividerLayout.AUTO,
        divider_mode=DividerMode.LOCK,
        connection=ConnectionType.DOVETAIL,
        mount="table",
        handle_mode=HandleMode.RUNE_SLOT,
        label_frame_style="recessed_portal",
        smart_cartridge=SmartCartridge.PLAIN,
        mechanics=MechanicsConfig(
            rail_profile=RailProfile.V_PROFILE,
            anti_wobble=AntiWobbleType.SPRING_WHISKER,
            sound_profile=SoundProfile.MECH_CLICK,
            service_channel=True,  # Dusty mode
        ),
        pattern=PatternConfig(
            type=RunePattern.CHEVRON_RUNE,
            position=PatternPosition.BACK_EDGE,
        ),
        details=DetailsConfig(
            shadow_gap=0.4,
            guide_cones=True,
        ),
    )


def create_medical_sealed() -> BoxConfig:
    """Medicine/optics: PETG sealed, minimal relief."""
    return BoxConfig(
        width=180.0,
        depth=150.0,
        height=70.0,
        description="Medicine/optics: PETG sealed, minimal relief",
        design=DesignStyle.BELOVODIE,
        belovodie_preset=BelovodiePreset.MED,
        color_body=BelovodieColor.STONE_SAND,
        color_accent=BelovodieColor.FROST_BLUE,
        material=MaterialType.PETG,
        printer=PrinterProfile.CREALITY_K1C,
        print_mode=PrintMode.PREMIUM,
        dividers=DividerLayout.GRID_2X2,
        divider_mode=DividerMode.SNAP,
        connection=ConnectionType.CLIP,
        mount="table",
        handle_mode=HandleMode.HIDDEN_HOOK_RUNE,
        label_frame_style="recessed_portal",
        smart_cartridge=SmartCartridge.PLAIN,
        sealed=True,  # O-profile seal groove
        mechanics=MechanicsConfig(
            rail_profile=RailProfile.V_PROFILE,
            anti_wobble=AntiWobbleType.NONE,  # Less dust traps
            sound_profile=SoundProfile.SILENT,
            service_channel=False,
        ),
        pattern=PatternConfig(
            type=RunePattern.NONE,  # Minimal relief = less dust
        ),
        details=DetailsConfig(
            shadow_gap=0.3,
            guide_cones=True,
        ),
    )


def create_mvp() -> BoxConfig:
    """Minimal version for quick start."""
    return BoxConfig(
        width=200.0,
        depth=220.0,
        height=80.0,
        description="Minimal version for quick start",
        design=DesignStyle.NORDIC,
        material=MaterialType.HYPER_PLA,
        printer=PrinterProfile.CREALITY_K1C,
        print_mode=PrintMode.DRAFT,
        dividers=DividerLayout.NONE,
        connection=ConnectionType.CLIP,
        mechanics=MechanicsConfig(
            anti_wobble=AntiWobbleType.NONE,
        ),
        pattern=PatternConfig(
            type=RunePattern.NONE,
        ),
    )


def create_entryway_keys() -> BoxConfig:
    """Small box for keys and pocket items."""
    return BoxConfig(
        width=150.0,
        depth=120.0,
        height=50.0,
        description="Entryway: keys and pocket items",
        design=DesignStyle.NORDIC,
        material=MaterialType.HYPER_PLA,
        printer=PrinterProfile.CREALITY_K1C,
        dividers=DividerLayout.NONE,
        connection=ConnectionType.CLIP,
    )


def create_desk_tech() -> BoxConfig:
    """Desktop box for gadgets and cables."""
    return BoxConfig(
        width=200.0,
        depth=220.0,
        height=80.0,
        description="Desktop: gadgets and cables",
        design=DesignStyle.TECHNO,
        material=MaterialType.HYPER_PLA,
        printer=PrinterProfile.CREALITY_K1C,
        dividers=DividerLayout.AUTO,
        connection=ConnectionType.MAGNET,
    )


def create_workshop_screws() -> BoxConfig:
    """Workshop box for screws and small parts."""
    return BoxConfig(
        width=150.0,
        depth=200.0,
        height=50.0,
        description="Workshop: screws and small parts",
        design=DesignStyle.NORDIC,
        material=MaterialType.PETG,
        printer=PrinterProfile.CREALITY_K1C,
        dividers=DividerLayout.GRID_3X3,
        divider_mode=DividerMode.LOCK,
        connection=ConnectionType.DOVETAIL,
    )


def create_bathroom_meds() -> BoxConfig:
    """Bathroom box for medications."""
    return BoxConfig(
        width=120.0,
        depth=100.0,
        height=60.0,
        description="Bathroom: medications storage",
        design=DesignStyle.NORDIC,
        material=MaterialType.PETG,  # Moisture resistant
        printer=PrinterProfile.CREALITY_K1C,
        dividers=DividerLayout.GRID_2X2,
        divider_mode=DividerMode.SNAP,
        connection=ConnectionType.CLIP,
        sealed=True,
    )


# Preset factory functions
PRESET_FACTORIES = {
    BoxPreset.SMARTHOME_DESK: create_smarthome_desk,
    BoxPreset.WORKSHOP_TOOLS: create_workshop_tools,
    BoxPreset.MEDICAL_SEALED: create_medical_sealed,
    BoxPreset.MVP: create_mvp,
    BoxPreset.ENTRYWAY_KEYS: create_entryway_keys,
    BoxPreset.DESK_TECH: create_desk_tech,
    BoxPreset.WORKSHOP_SCREWS: create_workshop_screws,
    BoxPreset.BATHROOM_MEDS: create_bathroom_meds,
}


def get_preset(preset: BoxPreset) -> BoxConfig:
    """Get BoxConfig for a preset."""
    factory = PRESET_FACTORIES.get(preset)
    if factory is None:
        raise ValueError(f"Unknown preset: {preset}")
    return factory()


# Export ready-made presets as dictionary
PRESETS: Dict[str, BoxConfig] = {
    "smarthome_desk": create_smarthome_desk(),
    "workshop_tools": create_workshop_tools(),
    "medical_sealed": create_medical_sealed(),
    "mvp": create_mvp(),
}
