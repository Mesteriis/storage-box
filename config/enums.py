"""
Enum configurations for Storage Box System.

All enum types defining styles, materials, profiles, and options.
"""

from enum import Enum


class DesignStyle(Enum):
    """Design styles for the storage box - futuristic but subtle for smart home."""
    NORDIC = "nordic"           # Scandinavian minimalism: soft corners R=5mm, clean lines
    TECHNO = "techno"           # Techno: 45° chamfers, thin accent lines
    BAUHAUS = "bauhaus"         # Bauhaus: geometry + function, contrast inserts
    ORGANIC = "organic"         # Organic: smooth S-curves, natural forms
    PARAMETRIC = "parametric"   # Parametric: wave pattern on sides
    STEALTH = "stealth"         # Stealth: sharp edges, hidden connections
    BELOVODIE = "belovodie"     # Belovodye: warm techno-sacral minimalism


class ConnectionType(Enum):
    """Connection types for stacking/joining boxes."""
    DOVETAIL = "dovetail"       # Dovetail joint
    MAGNET = "magnet"           # For 6×3 mm magnets
    CLIP = "clip"               # Snap clips
    NONE = "none"               # No connection


class MaterialType(Enum):
    """Material types with specific tolerance values."""
    HYPER_PLA = "hyper_pla"     # Tolerance 0.3 mm
    PETG = "petg"               # Tolerance 0.4 mm
    ABS = "abs"                 # Tolerance 0.35 mm


class DividerLayout(Enum):
    """Divider layout options."""
    AUTO = "auto"               # Auto-calculate based on dimensions
    GRID_2X2 = "grid_2x2"       # 2×2 grid
    GRID_2X3 = "grid_2x3"       # 2×3 grid
    GRID_3X3 = "grid_3x3"       # 3×3 grid
    NONE = "none"               # No dividers


class DividerMode(Enum):
    """Divider attachment mode."""
    SNAP = "snap"               # Quick-release (by hand)
    LOCK = "lock"               # With lock (for workshop)


class RailProfile(Enum):
    """Rail profile types for drawer slides."""
    RECTANGULAR = "rectangular" # Simple rectangular (basic)
    V_PROFILE = "v_profile"     # V-shaped (self-centering)
    DOVETAIL = "dovetail"       # Dovetail (anti-wobble)
    T_SLOT = "t_slot"           # T-profile (rigid)


class PrinterProfile(Enum):
    """Printer profiles with specific settings."""
    CREALITY_K1C = "k1c"        # Creality K1C (0.4 nozzle, 0.2 layer)
    GENERIC_FDM = "fdm"         # Standard FDM
    HIGH_DETAIL = "hd"          # High quality (0.12 layer)


class SoundProfile(Enum):
    """Sound profile for drawer closing."""
    SILENT = "silent"           # Soft close, TPU damper
    SOFT_CLICK = "soft_click"   # Pleasant short click
    MECH_CLICK = "mech_click"   # Distinct "tuning fork" (resonator)


class RunePattern(Enum):
    """Rune patterns for Belovodye style."""
    NONE = "none"               # No pattern
    CHEVRON_RUNE = "chevron"    # Chevron - protection
    KNOT_LINE = "knot"          # Interrupted line - knot
    WAVE_RUNE = "wave"          # Broken wave (not sine!)
    GRID_RUNE = "grid"          # Grid with dots


class BelovodieColor(Enum):
    """Color palette for Belovodye style."""
    # Base colors (body)
    MIST_WHITE = "mist_white"       # Matte white (RAL 9016)
    STONE_SAND = "stone_sand"       # Warm sand (RAL 1015)
    ASH_GREY = "ash_grey"           # Light grey (RAL 7035)
    OBSIDIAN = "obsidian"           # Matte black (RAL 9005)
    
    # Accent colors
    EMERALD_DEEP = "emerald_deep"   # Deep emerald (signature)
    BRONZE_WARM = "bronze_warm"     # Warm bronze (not yellow gold!)
    RUNE_RED = "rune_red"           # Muted red (only for tools/urgent)
    FROST_BLUE = "frost_blue"       # Cold blue (electronics)


class BelovodiePreset(Enum):
    """Belovodye style presets."""
    DESK = "desk"               # White/grey + emerald frame
    WORKSHOP = "workshop"       # Anthracite + bronze accent
    MED = "med"                 # Sand + white tablet + seal
    SACRED = "sacred"           # Full rune set + bronze (exhibition)


class HandleMode(Enum):
    """Handle profile modes."""
    PINCH = "pinch"             # Pinch grip - narrow slot 12×60 mm
    HOOK = "hook"               # Hook from below - finger catches from bottom
    GLOVE = "glove"             # Enlarged - for gloves/workshop
    INVISIBLE = "invisible"     # Hidden (push-latch or under panel)
    HIDDEN_HOOK_RUNE = "hidden_hook_rune"  # Belovodye hidden hook with mark
    RUNE_SLOT = "rune_slot"     # Belovodye hexagonal slot


class ShellGeometry(Enum):
    """Shell geometry variations."""
    RECTANGULAR = "rectangular"     # Standard parallelepiped
    SLOPED_TOP = "sloped_top"       # Sloped top (trapezoid, front lower)
    SLOPED_BACK = "sloped_back"     # Sloped back (for desktop)
    WEDGE = "wedge"                 # Wedge (both sides sloped)
    CURVED_TOP = "curved_top"       # Convex top (arc)
    STEPPED = "stepped"             # Stepped (2-3 levels)
    ASYMMETRIC = "asymmetric"       # Asymmetric (one side higher)


class ColorInsert(Enum):
    """Color insert types for single-color printer."""
    # Functional
    LABEL_FRAME = "label_frame"       # Frame around label
    HANDLE_ACCENT = "handle_accent"   # Accent strip on handle
    EDGE_TRIM = "edge_trim"           # Perimeter trim
    
    # Decorative
    STRIPE_HORIZONTAL = "stripe_h"    # Horizontal stripe
    STRIPE_VERTICAL = "stripe_v"      # Vertical stripe
    CORNER_CAPS = "corner_caps"       # Corner caps (4 pcs)
    CENTER_BADGE = "badge"            # Center badge/logo
    WAVE_PATTERN = "wave"             # Wave overlay
    
    # Informational
    NUMBER_PLATE = "number"           # Drawer number (1, 2, 3...)
    ICON_SYMBOL = "icon"              # Content icon
    COLOR_DOT = "dot"                 # Color indicator dot


class SmartCartridge(Enum):
    """Smart cartridge module types."""
    PLAIN = "plain"             # Blank cover (basic version)
    NFC_13MM = "nfc"            # For NFC tag ∅13 mm
    HALL_SENSOR = "hall"        # Hall sensor (reed switch)
    ESP_MODULE = "esp"          # ESP32/ESP8266 + micro-USB
    CABLE_PASS = "cable"        # Cable pass ∅5 mm
    TEMP_HUMID = "dht"          # DHT22 (temperature/humidity)


class InsertType(Enum):
    """Modular bottom insert types."""
    FLAT = "flat"               # Flat bottom (standard)
    HONEYCOMB = "honeycomb"     # Honeycomb for round items
    CABLE_WAVES = "cable"       # Waves for cables
    BIT_HOLDER = "bits"         # Bit/drill holder
    COIN_TRAY = "coins"         # Coin tray
    FOAM_GRID = "foam"          # Grid for foam/padding
    PENCIL_GROOVES = "pencils"  # Grooves for pens
    WATCH_CUSHION = "watch"     # Cushions for watches
    VELOUR = "velour"           # Velour-lined tray


class PrintMode(Enum):
    """Print mode for quality/speed tradeoff."""
    DRAFT = "draft"             # Fast, no fine details
    NORMAL = "normal"           # Standard
    PREMIUM = "premium"         # Maximum detail


class MountType(Enum):
    """Wall mount types."""
    FRENCH_CLEAT = "french_cleat"   # French cleat (45°)
    KEYHOLE = "keyhole"             # Keyhole for screw
    RAIL_SYSTEM = "rail"            # Compatible with IKEA SKÅDIS
    MAGNETIC = "magnetic"           # Metal plate + magnets
    ADHESIVE = "adhesive"           # Platform for 3M Command


class LabelSystem(Enum):
    """Label system types."""
    PAPER_SLOT = "paper"          # Classic - paper under clear cover
    E_INK_MOUNT = "e_ink"         # Mount for e-ink display (2.9")
    DRY_ERASE = "dry_erase"       # White surface for marker
    EMBOSSED = "embossed"         # Embossed text (generated)
    BRAILLE = "braille"           # Braille (accessibility)
    QR_CODE = "qr"                # Relief QR code (scannable)
    ICON_GRID = "icons"           # Icon grid (from library)


class AntiWobbleType(Enum):
    """Anti-wobble mechanism types."""
    NONE = "none"               # No anti-wobble
    WEDGE = "wedge"             # Adjustable wedge
    SPRING_WHISKER = "spring_whisker"  # Spring whisker insert


class WhiskerVariant(Enum):
    """Spring whisker insert variants for test kit."""
    SOFT_S = "soft_s"           # 0.8 mm × 12 mm (soft)
    SOFT_L = "soft_l"           # 0.8 mm × 18 mm (very soft)
    MED_S = "med_s"             # 1.0 mm × 12 mm (medium)
    MED_L = "med_l"             # 1.0 mm × 18 mm (standard)
    FIRM_S = "firm_s"           # 1.2 mm × 12 mm (firm)
    FIRM_L = "firm_l"           # 1.2 mm × 18 mm (very firm)


class PatternPosition(Enum):
    """Pattern position for Belovodye (only 1 of 3!)."""
    BACK_EDGE = "back_edge"     # Sidewall near back edge
    FRONT_BAND = "front_band"   # Thin band under front
    LABEL_FRAME = "label_frame" # Label frame decoration
