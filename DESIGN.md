# Storage Box - Parametric Design System

## Overview

Parametric storage box with sliding drawer for FDM 3D printing. Configurable dimensions, wall thickness, and drawer mechanism.

## Geometry

### Shell (П-shape)
```
Top view:
┌─────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │  ← Back wall
│ ▓                 ▓ │
│ ▓                 ▓ │  ← Side walls
│ ▓                 ▓ │
│                     │  ← Front OPEN
└─────────────────────┘
```

- Hollow box with front wall removed
- Uniform wall thickness
- Floor thickness (can differ from walls)

### Drawer Slide Mechanism

**Ledges** on shell side walls:
```
Side view (cross-section):
┌────────────────────┐
│    ┌──────────────┐│  Drawer top
│    │              ││
│ ═══╪══════════════╪│═══  ← Ledge (shelf on wall)
│    │   Flange     ││
│    └──────────────┘│
└────────────────────┘
```

**Flanges** on drawer bottom sides:
- Extend outward from drawer body
- Rest on ledges
- Allow free sliding motion

### Drawer
- Hollow box (open top)
- Flanges on bottom edges
- Finger pull cutout at front

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| WIDTH | 200mm | External width (X) |
| DEPTH | 220mm | External depth (Y) |
| HEIGHT | 80mm | External height (Z) |
| WALL | 2mm | Wall thickness |
| FLOOR | 2mm | Floor thickness |
| RAIL_WIDTH | 5mm | Ledge/flange width |
| TOLERANCE | 0.3mm | Clearance for PLA |

## Derived Dimensions

```python
# Shell interior
inner_w = WIDTH - 2 * WALL
inner_d = DEPTH - 2 * WALL
inner_h = HEIGHT - FLOOR

# Ledge position
ledge_z = FLOOR + 15  # Height above floor
ledge_width = RAIL_WIDTH

# Drawer body
drawer_w = inner_w - 2 * ledge_width - 2 * TOLERANCE
drawer_d = inner_d - 10  # Room to slide
drawer_h = HEIGHT - ledge_z - 5

# Total drawer width with flanges
total_drawer_w = drawer_w + 2 * (flange_width - overlap)
```

## Files

```
storage_box/
├── config/
│   ├── enums.py          # BoxType, Material enums
│   ├── box_config.py     # BoxConfig dataclass
│   ├── derived_config.py # Calculated values
│   ├── design_tokens.py  # Material constants
│   ├── rules.py          # Validation rules
│   ├── presets.py        # Preset configurations
│   └── config_manager.py # YAML load/save
├── components/
│   ├── shell.py          # Shell geometry
│   ├── rails.py          # Ledge geometry
│   └── drawer.py         # Drawer geometry
├── test_geometry.py      # Standalone geometry test
├── test_system.py        # Configuration tests
└── generate.py           # Main generator
```

## Usage

### Test geometry in Blender:
```bash
blender --python test_geometry.py
```

### Generate from config:
```python
from config import ConfigManager, presets

# Load preset
config = presets.create_desk_organizer()

# Or load from YAML
config = ConfigManager.load("my_box.yaml")

# Generate
from generate import generate_storage_box
generate_storage_box(config)
```

## Print Settings

- Layer height: 0.2mm
- Infill: 15-20%
- No supports needed (П-shape prints fine)
- Print shell upside-down for better overhangs
- Print drawer normally

## Sliding Mechanism Notes

1. **Ledges** are horizontal shelves attached to shell side walls
2. **Flanges** extend from drawer bottom, rest on ledges
3. Tolerance (0.3mm for PLA) ensures smooth sliding
4. No V-rails needed - simple flat surfaces work better for FDM

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| П-shape shell | Front opening allows drawer to slide out |
| Ledge mechanism | Simpler than V-rails, works better for FDM |
| Flanges on drawer | Drawer body stays narrow, flanges provide support |
| Hollow drawer | Saves material, provides storage space |
| Finger pull | Easy to grab and pull drawer out |
