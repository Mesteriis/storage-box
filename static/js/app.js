// Storage Box Generator - Frontend Logic

let scene, camera, renderer, controls;
let currentModel = null;

// Initialize Three.js 3D Viewer
function init3DViewer() {
    const container = document.getElementById('viewer-container');
    
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    
    // Camera
    camera = new THREE.PerspectiveCamera(
        45,
        container.clientWidth / container.clientHeight,
        1,
        10000
    );
    camera.position.set(300, 300, 300);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    
    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = false;
    controls.minDistance = 100;
    controls.maxDistance = 1000;
    
    // Lights
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);
    
    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(200, 200, 200);
    scene.add(directionalLight1);
    
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-200, -200, -200);
    scene.add(directionalLight2);
    
    // Grid
    const gridHelper = new THREE.GridHelper(500, 50, 0x444444, 0x222222);
    scene.add(gridHelper);
    
    // Axes helper
    const axesHelper = new THREE.AxesHelper(100);
    scene.add(axesHelper);
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}

// Load STL model
function loadSTLModel(url) {
    const loader = new THREE.STLLoader();
    
    loader.load(url, function(geometry) {
        // Remove old model
        if (currentModel) {
            scene.remove(currentModel);
        }
        
        // Create material
        const material = new THREE.MeshPhongMaterial({
            color: 0x667eea,
            specular: 0x111111,
            shininess: 200
        });
        
        // Create mesh
        const mesh = new THREE.Mesh(geometry, material);
        
        // Center geometry
        geometry.center();
        
        // Scale to reasonable size (STL is in mm, scene in units)
        mesh.scale.set(1, 1, 1);
        
        // Add to scene
        scene.add(mesh);
        currentModel = mesh;
        
        // Fit camera to model
        fitCameraToObject(camera, mesh, controls);
        
    }, undefined, function(error) {
        console.error('Error loading STL:', error);
    });
}

// Fit camera to show entire object
function fitCameraToObject(camera, object, controls) {
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    
    cameraZ *= 1.5; // Zoom out a little
    
    camera.position.set(
        center.x + cameraZ,
        center.y + cameraZ,
        center.z + cameraZ
    );
    
    camera.lookAt(center);
    controls.target.copy(center);
    
    camera.updateProjectionMatrix();
}

// Create simple box visualization (when no STL available)
function createSimpleBox(width, depth, height) {
    if (currentModel) {
        scene.remove(currentModel);
    }
    
    // Create box geometry
    const geometry = new THREE.BoxGeometry(width, depth, height);
    const material = new THREE.MeshPhongMaterial({
        color: 0x667eea,
        specular: 0x111111,
        shininess: 200,
        wireframe: false
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    currentModel = mesh;
    
    fitCameraToObject(camera, mesh, controls);
}

// Get current configuration from form
function getConfig() {
    return {
        width: parseFloat(document.getElementById('width').value),
        depth: parseFloat(document.getElementById('depth').value),
        height: parseFloat(document.getElementById('height').value),
        design: document.getElementById('design').value,
        material: document.getElementById('material').value,
        dividers: document.getElementById('dividers').value,
        connection: document.getElementById('connection').value,
        print_mode: document.getElementById('print_mode').value,
        stack_levels: 1,
        mount: 'table',
        expected_weight: 500
    };
}

// Load preset configuration
async function loadPreset(presetName) {
    try {
        const response = await fetch(`/api/preset/${presetName}`);
        const preset = await response.json();
        
        // Update form fields
        document.getElementById('width').value = preset.width;
        document.getElementById('depth').value = preset.depth;
        document.getElementById('height').value = preset.height;
        document.getElementById('design').value = preset.design;
        document.getElementById('material').value = preset.material;
        document.getElementById('dividers').value = preset.dividers;
        document.getElementById('connection').value = preset.connection;
        document.getElementById('print_mode').value = preset.print_mode;
        
        // Auto-calculate
        await calculateDimensions();
        
    } catch (error) {
        console.error('Error loading preset:', error);
        alert('Failed to load preset');
    }
}

// Calculate dimensions
async function calculateDimensions() {
    const config = getConfig();
    
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }
        
        // Display results
        displayDimensions(result.dimensions, result.dividers, result.features, result.tolerances);
        displayWarnings(result.warnings);
        
        // Update simple box visualization
        createSimpleBox(config.width, config.depth, config.height);
        
    } catch (error) {
        console.error('Error calculating:', error);
        alert('Failed to calculate dimensions');
    }
}

// Display calculated dimensions
function displayDimensions(dimensions, dividers, features, tolerances) {
    const display = document.getElementById('dimensions-display');
    
    let html = '<div class="row">';
    
    // Dimensions
    html += '<div class="col-md-6">';
    html += '<h6 class="text-primary">Wall & Floor</h6>';
    html += `<p><strong>Wall:</strong> ${dimensions.wall_thickness.toFixed(2)} mm</p>`;
    html += `<p><strong>Floor:</strong> ${dimensions.floor_thickness.toFixed(2)} mm</p>`;
    html += '</div>';
    
    html += '<div class="col-md-6">';
    html += '<h6 class="text-primary">Inner Space</h6>';
    html += `<p><strong>Width:</strong> ${dimensions.effective_inner_width.toFixed(1)} mm</p>`;
    html += `<p><strong>Depth:</strong> ${dimensions.effective_inner_depth.toFixed(1)} mm</p>`;
    html += `<p><strong>Height:</strong> ${dimensions.effective_inner_height.toFixed(1)} mm</p>`;
    html += '</div>';
    
    html += '<div class="col-md-6 mt-3">';
    html += '<h6 class="text-primary">Drawer</h6>';
    html += `<p><strong>Width:</strong> ${dimensions.drawer_width.toFixed(1)} mm</p>`;
    html += `<p><strong>Depth:</strong> ${dimensions.drawer_depth.toFixed(1)} mm</p>`;
    html += `<p><strong>Height:</strong> ${dimensions.drawer_height.toFixed(1)} mm</p>`;
    html += '</div>';
    
    html += '<div class="col-md-6 mt-3">';
    html += '<h6 class="text-primary">Dividers</h6>';
    html += `<p><strong>Grid:</strong> ${dividers.count[0] + 1} × ${dividers.count[1] + 1}</p>`;
    html += '</div>';
    
    html += '</div>';
    
    // Tolerances
    html += '<div class="mt-3">';
    html += '<h6 class="text-primary">Tolerances</h6>';
    html += `<p><small>Slide: ${tolerances.slide} mm | Snap: ${tolerances.snap} mm | Pressfit: ${tolerances.pressfit} mm</small></p>`;
    html += '</div>';
    
    display.innerHTML = html;
}

// Display warnings
function displayWarnings(warnings) {
    const display = document.getElementById('warnings-display');
    
    if (warnings && warnings.length > 0) {
        let html = '<div class="warning-box mt-3">';
        html += '<h6><i class="bi bi-exclamation-triangle"></i> Warnings</h6>';
        html += '<ul class="mb-0">';
        warnings.forEach(warning => {
            html += `<li>${warning}</li>`;
        });
        html += '</ul>';
        html += '</div>';
        display.innerHTML = html;
    } else {
        display.innerHTML = '';
    }
}

// Generate 3D model
async function generateModel() {
    const config = getConfig();
    const loadingOverlay = document.getElementById('loading-overlay');
    
    try {
        loadingOverlay.classList.add('active');
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Generation failed: ' + result.error);
            return;
        }
        
        alert(`Generated ${result.files.length} files:\n${result.files.join('\n')}`);
        
        // Load first STL file into viewer
        if (result.files.length > 0) {
            const stlUrl = `/api/download/${result.files[0]}`;
            loadSTLModel(stlUrl);
        }
        
    } catch (error) {
        console.error('Error generating:', error);
        alert('Failed to generate model');
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize 3D viewer
    init3DViewer();
    
    // Create initial simple box
    createSimpleBox(200, 220, 80);
    
    // Event listeners for preset buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const preset = this.dataset.preset;
            loadPreset(preset);
        });
    });
    
    // Calculate button
    document.getElementById('calculate-btn').addEventListener('click', calculateDimensions);
    
    // Generate button
    document.getElementById('generate-btn').addEventListener('click', generateModel);
    
    // Auto-update visualization when dimensions change
    ['width', 'depth', 'height'].forEach(id => {
        document.getElementById(id).addEventListener('change', function() {
            const width = parseFloat(document.getElementById('width').value);
            const depth = parseFloat(document.getElementById('depth').value);
            const height = parseFloat(document.getElementById('height').value);
            createSimpleBox(width, depth, height);
        });
    });
});
