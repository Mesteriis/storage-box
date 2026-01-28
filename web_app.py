#!/usr/bin/env python3
"""
Storage Box Web Interface.

Flask application for configuring and generating storage boxes.
Includes 3D preview using Three.js STL viewer.
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import tempfile
import subprocess
import json

app = Flask(__name__)

# Import our storage box system
try:
    from config import BoxConfig, DerivedConfig, DesignTokens, PRESETS
    from config.enums import (
        DesignStyle, MaterialType, DividerLayout, ConnectionType,
        RailProfile, PrintMode, BelovodieColor
    )
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("Warning: Config modules not available")


@app.route('/')
def index():
    """Main page with configuration form and 3D preview."""
    return render_template('index.html',
                         design_styles=list(DesignStyle),
                         materials=list(MaterialType),
                         divider_layouts=list(DividerLayout),
                         connection_types=list(ConnectionType),
                         print_modes=list(PrintMode),
                         presets=list(PRESETS.keys()) if HAS_CONFIG else [])


@app.route('/api/presets')
def get_presets():
    """Get list of available presets."""
    if not HAS_CONFIG:
        return jsonify({"error": "Config not available"}), 500
    
    presets_data = {}
    for name, config in PRESETS.items():
        presets_data[name] = {
            "width": config.width,
            "depth": config.depth,
            "height": config.height,
            "design": config.design.value,
            "material": config.material.value,
            "description": config.description
        }
    
    return jsonify(presets_data)


@app.route('/api/preset/<preset_name>')
def get_preset(preset_name):
    """Get specific preset configuration."""
    if not HAS_CONFIG:
        return jsonify({"error": "Config not available"}), 500
    
    if preset_name not in PRESETS:
        return jsonify({"error": f"Preset '{preset_name}' not found"}), 404
    
    config = PRESETS[preset_name]
    
    return jsonify({
        "width": config.width,
        "depth": config.depth,
        "height": config.height,
        "design": config.design.value,
        "material": config.material.value,
        "dividers": config.dividers.value,
        "connection": config.connection.value,
        "print_mode": config.print_mode.value,
        "description": config.description,
        "mount": config.mount,
        "stack_levels": config.stack_levels
    })


@app.route('/api/calculate', methods=['POST'])
def calculate_dimensions():
    """Calculate derived dimensions from user config."""
    if not HAS_CONFIG:
        return jsonify({"error": "Config not available"}), 500
    
    data = request.json
    
    try:
        # Create BoxConfig from request
        config = BoxConfig(
            width=float(data.get('width', 200)),
            depth=float(data.get('depth', 220)),
            height=float(data.get('height', 80)),
            design=DesignStyle(data.get('design', 'nordic')),
            material=MaterialType(data.get('material', 'hyper_pla')),
            dividers=DividerLayout(data.get('dividers', 'auto')),
            connection=ConnectionType(data.get('connection', 'dovetail')),
            print_mode=PrintMode(data.get('print_mode', 'normal')),
            stack_levels=int(data.get('stack_levels', 1)),
            mount=data.get('mount', 'table'),
            expected_weight=float(data.get('expected_weight', 500))
        )
        
        # Calculate derived parameters
        derived = DerivedConfig(config)
        
        # Get design tokens
        tokens = DesignTokens.from_style(config.design, derived.wall_thickness)
        
        # Validate
        warnings = derived.validate()
        
        return jsonify({
            "success": True,
            "dimensions": {
                "wall_thickness": derived.wall_thickness,
                "floor_thickness": derived.floor_thickness,
                "effective_inner_width": derived.effective_inner_width,
                "effective_inner_depth": derived.effective_inner_depth,
                "effective_inner_height": derived.effective_inner_height,
                "drawer_width": derived.drawer_width,
                "drawer_depth": derived.drawer_depth,
                "drawer_height": derived.drawer_height,
            },
            "dividers": {
                "count": derived.divider_count,
            },
            "features": derived.features_enabled,
            "tolerances": derived.tolerances,
            "warnings": warnings,
            "summary": derived.summary()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/generate', methods=['POST'])
def generate_model():
    """Generate 3D model STL files."""
    if not HAS_CONFIG:
        return jsonify({"error": "Config not available"}), 500
    
    data = request.json
    
    try:
        # Create config
        config = BoxConfig(
            width=float(data.get('width', 200)),
            depth=float(data.get('depth', 220)),
            height=float(data.get('height', 80)),
            design=DesignStyle(data.get('design', 'nordic')),
            material=MaterialType(data.get('material', 'hyper_pla')),
            dividers=DividerLayout(data.get('dividers', 'auto')),
            connection=ConnectionType(data.get('connection', 'dovetail')),
            print_mode=PrintMode(data.get('print_mode', 'normal')),
            stack_levels=int(data.get('stack_levels', 1)),
            mount=data.get('mount', 'table'),
        )
        
        # Create temp directory for output
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            
            # Run Blender generation
            script_path = Path(__file__).parent / "generate.py"
            
            cmd = [
                "blender",
                "--background",
                "--python", str(script_path),
                "--",
                "--width", str(config.width),
                "--depth", str(config.depth),
                "--height", str(config.height),
                "--style", config.design.value,
                "--output", str(output_dir)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            
            if result.returncode != 0:
                return jsonify({
                    "error": "Generation failed",
                    "stderr": result.stderr
                }), 500
            
            # List generated files
            stl_files = list(output_dir.glob("*.stl"))
            
            return jsonify({
                "success": True,
                "files": [f.name for f in stl_files],
                "output_dir": str(output_dir)
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Generation timeout"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/download/<filename>')
def download_stl(filename):
    """Download generated STL file."""
    # In production, you'd validate the file path more carefully
    # For now, this is a simplified version
    file_path = Path(tempfile.gettempdir()) / filename
    
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/examples')
def examples():
    """Gallery of example configurations."""
    examples_list = [
        {
            "name": "Smart Home Desk",
            "preset": "smarthome_desk",
            "image": "/static/examples/smarthome_desk.png",
            "description": "Quiet smart home box for desktop use"
        },
        {
            "name": "Workshop Tools",
            "preset": "workshop_tools",
            "image": "/static/examples/workshop_tools.png",
            "description": "PETG box for tools with satisfying click"
        },
        {
            "name": "Medical Sealed",
            "preset": "medical_sealed",
            "image": "/static/examples/medical_sealed.png",
            "description": "Medicine/optics with O-profile seal"
        },
        {
            "name": "MVP",
            "preset": "mvp",
            "image": "/static/examples/mvp.png",
            "description": "Minimal version for quick start"
        }
    ]
    
    return render_template('examples.html', examples=examples_list)


@app.route('/docs')
def documentation():
    """Documentation page."""
    return render_template('docs.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
