"""
Export System for Storage Box.

STL export and Print Manifest generation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import yaml

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


@dataclass
class PrintFile:
    """Single file in print manifest."""
    filename: str
    component: str
    material: str = "Hyper PLA"
    color: str = "RAL 7035"
    quantity: int = 1
    orientation: str = "bottom_down"
    supports: bool = False
    infill: int = 15
    walls: int = 3
    estimated_time: str = ""
    estimated_weight: float = 0.0
    notes: str = ""


@dataclass
class PrintManifest:
    """Complete print manifest for a box configuration."""
    model_name: str
    version: str
    printer: str
    material: str
    files: List[PrintFile] = field(default_factory=list)
    total_print_time: str = ""
    total_filament: float = 0.0
    assembly_notes: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_yaml(self) -> str:
        """Convert manifest to YAML string."""
        data = {
            "model": self.model_name,
            "version": self.version,
            "printer": self.printer,
            "material": self.material,
            "created": self.created,
            "files": [
                {
                    "name": f.filename,
                    "component": f.component,
                    "quantity": f.quantity,
                    "orientation": f.orientation,
                    "supports": f.supports,
                    "infill": f"{f.infill}%",
                    "walls": f.walls,
                    "time": f.estimated_time,
                    "weight": f"{f.estimated_weight}g",
                    "notes": f.notes,
                }
                for f in self.files
            ],
            "total_time": self.total_print_time,
            "total_weight": f"{self.total_filament}g",
            "assembly_notes": self.assembly_notes,
        }
        return yaml.dump(data, default_flow_style=False,
                         allow_unicode=True, sort_keys=False)

    def save(self, filepath: Path) -> None:
        """Save manifest to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_yaml())


def export_stl(
    obj: "bpy.types.Object",
    filepath: Path,
    apply_modifiers: bool = True,
) -> bool:
    """
    Export single object to STL file.
    
    Args:
        obj: Blender object to export
        filepath: Output file path
        apply_modifiers: Apply modifiers before export
    
    Returns:
        True if successful
    """
    ensure_bpy()
    
    # Deselect all, select target
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Export
    bpy.ops.export_mesh.stl(
        filepath=str(filepath),
        use_selection=True,
        use_mesh_modifiers=apply_modifiers,
        ascii=False,
    )
    
    return filepath.exists()


def export_component_set(
    components: dict,
    output_dir: Path,
    config,  # DerivedConfig
) -> PrintManifest:
    """
    Export all components and generate print manifest.
    
    Expected components dict:
    {
        "shell": bpy.types.Object,
        "drawer": bpy.types.Object,
        "dividers": [bpy.types.Object, ...],
        "test_kit": [bpy.types.Object, ...],
    }
    
    Args:
        components: Dict of component objects
        output_dir: Output directory
        config: DerivedConfig
    
    Returns:
        PrintManifest
    """
    ensure_bpy()
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build manifest
    cfg = config.config
    manifest = PrintManifest(
        model_name=f"Storage Box {cfg.width}x{cfg.depth}x{cfg.height} {cfg.design.value.upper()}",
        version="1.0.0",
        printer=cfg.printer.value,
        material=cfg.material.value,
        assembly_notes=[
            "1. Insert drawer into shell",
            "2. Snap in dividers (see grid layout)",
            "3. Optional: glue magnets into pockets",
        ],
    )
    
    total_time_min = 0
    total_weight = 0.0
    
    # Export shell
    if "shell" in components and components["shell"]:
        shell_file = output_dir / "shell.stl"
        export_stl(components["shell"], shell_file)
        
        shell_time = _estimate_print_time(cfg.width, cfg.depth, cfg.height, 15)
        shell_weight = _estimate_weight(cfg.width, cfg.depth, cfg.height, 15)
        
        manifest.files.append(PrintFile(
            filename="shell.stl",
            component="shell",
            material=cfg.material.value,
            orientation="bottom_down",
            infill=15,
            walls=3,
            estimated_time=_format_time(shell_time),
            estimated_weight=shell_weight,
            notes="Print with brim for adhesion",
        ))
        total_time_min += shell_time
        total_weight += shell_weight
    
    # Export drawer
    if "drawer" in components and components["drawer"]:
        drawer_file = output_dir / "drawer.stl"
        export_stl(components["drawer"], drawer_file)
        
        drawer_time = _estimate_print_time(
            config.drawer_width, config.drawer_depth, config.drawer_height, 15
        )
        drawer_weight = _estimate_weight(
            config.drawer_width, config.drawer_depth, config.drawer_height, 15
        )
        
        manifest.files.append(PrintFile(
            filename="drawer.stl",
            component="drawer",
            material=cfg.material.value,
            orientation="front_down",
            infill=15,
            walls=3,
            estimated_time=_format_time(drawer_time),
            estimated_weight=drawer_weight,
        ))
        total_time_min += drawer_time
        total_weight += drawer_weight
    
    # Export dividers
    if "dividers" in components and components["dividers"]:
        for i, div in enumerate(components["dividers"]):
            if div:
                div_file = output_dir / f"divider_{i}.stl"
                export_stl(div, div_file)
        
        div_count = len([d for d in components["dividers"] if d])
        if div_count > 0:
            div_time = 8 * div_count  # ~8 min each
            div_weight = 3.0 * div_count  # ~3g each
            
            manifest.files.append(PrintFile(
                filename="divider_*.stl",
                component="dividers",
                material=cfg.material.value,
                quantity=div_count,
                orientation="flat",
                infill=20,
                walls=2,
                estimated_time=f"{div_time // div_count}m each",
                estimated_weight=div_weight / div_count,
            ))
            total_time_min += div_time
            total_weight += div_weight
    
    # Export test kit
    if "test_kit" in components and components["test_kit"]:
        for name, piece in components["test_kit"].items():
            if piece and not isinstance(piece, list):
                test_file = output_dir / f"test_{name}.stl"
                export_stl(piece, test_file)
        
        manifest.files.append(PrintFile(
            filename="test_*.stl",
            component="test_kit",
            material=cfg.material.value,
            quantity=1,
            orientation="flat",
            infill=20,
            walls=2,
            estimated_time="10m",
            estimated_weight=2.0,
            notes="Print first to verify tolerances",
        ))
        total_time_min += 10
        total_weight += 2.0
    
    # Finalize totals
    manifest.total_print_time = _format_time(total_time_min)
    manifest.total_filament = round(total_weight, 1)
    
    # Save manifest
    manifest_file = output_dir / "print_manifest.yaml"
    manifest.save(manifest_file)
    
    return manifest


def _estimate_print_time(
    width: float,
    depth: float,
    height: float,
    infill: int,
) -> int:
    """
    Estimate print time in minutes.
    
    Very rough approximation based on volume.
    Real estimates would come from slicer.
    """
    # Volume in cm³
    volume_cm3 = (width * depth * height) / 1000
    
    # Shell volume (rough: 15% of bounding box)
    shell_volume = volume_cm3 * 0.15
    
    # Base rate: ~2 min per cm³ at 300mm/s
    base_rate = 2.0
    
    # Adjust for infill
    infill_factor = 1.0 + (infill / 100) * 0.5
    
    return int(shell_volume * base_rate * infill_factor)


def _estimate_weight(
    width: float,
    depth: float,
    height: float,
    infill: int,
) -> float:
    """
    Estimate print weight in grams.
    
    Rough approximation based on shell volume.
    """
    # Volume in cm³
    volume_cm3 = (width * depth * height) / 1000
    
    # Shell volume (rough: 15% of bounding box)
    shell_volume = volume_cm3 * 0.15
    
    # PLA density: ~1.24 g/cm³
    density = 1.24
    
    # Adjust for infill
    infill_factor = 1.0 + (infill / 100) * 0.5
    
    return round(shell_volume * density * infill_factor, 1)


def _format_time(minutes: int) -> str:
    """Format minutes as '1h 30m' or '45m'."""
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        if mins > 0:
            return f"{hours}h {mins}m"
        return f"{hours}h"
    return f"{minutes}m"


def export_single_component(
    obj: "bpy.types.Object",
    output_dir: Path,
    component_name: str,
) -> Optional[Path]:
    """
    Export a single component to STL.
    
    Args:
        obj: Object to export
        output_dir: Output directory
        component_name: Name for the STL file
    
    Returns:
        Path to exported file or None
    """
    if obj is None:
        return None
    
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{component_name}.stl"
    
    if export_stl(obj, filepath):
        return filepath
    return None
