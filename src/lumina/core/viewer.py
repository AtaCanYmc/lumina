import base64
import os
import tempfile
import webbrowser
from typing import Any

from stl import mesh


def get_mesh_stats(mesh_obj: mesh.Mesh, density_g_cm3: float = 1.24) -> dict[str, Any]:
    """Calculates physical and geometric statistics for a 3D STL mesh.

    Args:
        mesh_obj: numpy-stl Mesh object.
        density_g_cm3: Material density in g/cm³ (default: 1.24 for PLA).

    Returns:
        dict containing facets, vertices, dimensions (width, height, depth),
        volume in cm³, and estimated weight in grams.
    """
    facets = len(mesh_obj.vectors)
    minx, maxx = float(mesh_obj.x.min()), float(mesh_obj.x.max())
    miny, maxy = float(mesh_obj.y.min()), float(mesh_obj.y.max())
    minz, maxz = float(mesh_obj.z.min()), float(mesh_obj.z.max())

    width = round(maxx - minx, 2)
    height = round(maxy - miny, 2)
    depth = round(maxz - minz, 2)

    try:
        vol_mm3, _, _ = mesh_obj.get_mass_properties()
        volume_mm3 = max(0.0, float(vol_mm3))
    except Exception:
        volume_mm3 = 0.0

    volume_cm3 = round(volume_mm3 / 1000.0, 2)
    weight_g = round(volume_cm3 * density_g_cm3, 2)

    return {
        "facets": facets,
        "width_mm": width,
        "height_mm": height,
        "depth_mm": depth,
        "min_z": round(minz, 2),
        "max_z": round(maxz, 2),
        "volume_cm3": volume_cm3,
        "weight_grams": weight_g,
    }


def generate_viewer_html(
    stl_path_or_bytes: str | bytes,
    title: str = "Lumina 3D Lithophane Viewer",
    mesh_stats: dict[str, Any] | None = None,
) -> str:
    """Generates a self-contained, interactive WebGL 3D viewer HTML page.

    Features:
      - Interactive Three.js OrbitControls (rotate, pan, zoom).
      - Dual rendering modes:
          * Backlit Lithophane: Subsurface scattering / physical light transmission simulation.
          * Solid Shaded: Matte 3D relief with directional lighting and shadows.
          * Wireframe: Mesh facet topology.
      - Light temperature controls (Warm 2700K, Neutral 4000K, Cool 6500K, or custom).
      - Light intensity, backlight distance, and absorption contrast sliders.
      - Real-time mesh statistics (dimensions, facets, estimated PLA weight).
      - Drag-and-drop support for loading any external STL files.
    """
    if isinstance(stl_path_or_bytes, bytes):
        stl_b64 = base64.b64encode(stl_path_or_bytes).decode("ascii")
        filename = "lithophane.stl"
    else:
        if not os.path.exists(stl_path_or_bytes):
            raise FileNotFoundError(f"STL file not found: {stl_path_or_bytes}")
        with open(stl_path_or_bytes, "rb") as f:
            stl_b64 = base64.b64encode(f.read()).decode("ascii")
        filename = os.path.basename(stl_path_or_bytes)

        if mesh_stats is None:
            try:
                m = mesh.Mesh.from_file(stl_path_or_bytes)
                mesh_stats = get_mesh_stats(m)
            except Exception:
                mesh_stats = None

    stats_json = "{}"
    if mesh_stats:
        import json

        stats_json = json.dumps(mesh_stats)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} - {filename}</title>
  <style>
    :root {{
      --bg: #0d1117;
      --panel-bg: rgba(22, 27, 34, 0.85);
      --border: rgba(240, 246, 252, 0.12);
      --text: #e6edf3;
      --text-dim: #8b949e;
      --accent: #58a6ff;
      --accent-hover: #1f6feb;
      --radius: 10px;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    body {{
      background: var(--bg);
      color: var(--text);
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }}
    #canvas-container {{
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
    }}
    .ui-panel {{
      position: absolute;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
      z-index: 10;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
      user-select: none;
    }}
    #header-panel {{
      top: 16px;
      left: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .logo-badge {{
      background: linear-gradient(135deg, #238636, #2ea043);
      color: #fff;
      font-weight: 700;
      font-size: 11px;
      letter-spacing: 0.5px;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }}
    .title-text {{
      font-size: 14px;
      font-weight: 600;
    }}
    .filename-text {{
      font-size: 12px;
      color: var(--text-dim);
    }}
    #controls-panel {{
      top: 16px;
      right: 16px;
      width: 300px;
      max-height: calc(100vh - 32px);
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .control-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .group-label {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }}
    .btn-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
    }}
    button.btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    button.btn:hover {{
      background: rgba(255, 255, 255, 0.1);
      border-color: var(--accent);
    }}
    button.btn.active {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }}
    .slider-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-size: 12px;
    }}
    .slider-row input[type="range"] {{
      flex: 1;
      accent-color: var(--accent);
      cursor: pointer;
    }}
    .slider-val {{
      min-width: 44px;
      text-align: right;
      color: var(--text-dim);
      font-variant-numeric: tabular-nums;
    }}
    #stats-panel {{
      bottom: 16px;
      left: 16px;
      min-width: 240px;
      font-size: 12px;
      line-height: 1.6;
    }}
    .stat-row {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }}
    .stat-label {{
      color: var(--text-dim);
    }}
    .stat-val {{
      font-weight: 600;
      color: var(--text);
    }}
    #drop-overlay {{
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(13, 17, 23, 0.85);
      backdrop-filter: blur(8px);
      z-index: 100;
      border: 3px dashed var(--accent);
      justify-content: center;
      align-items: center;
      flex-direction: column;
      gap: 12px;
      pointer-events: none;
    }}
    #drop-overlay.visible {{
      display: flex;
    }}
    #instructions {{
      position: absolute;
      bottom: 16px;
      right: 16px;
      font-size: 11px;
      color: var(--text-dim);
      background: var(--panel-bg);
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      pointer-events: none;
    }}
  </style>
  <script type="importmap">
    {{
      "imports": {{
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
      }}
    }}
  </script>
</head>
<body>
  <div id="canvas-container"></div>

  <div id="drop-overlay">
    <div style="font-size: 40px;">📂</div>
    <div style="font-size: 16px; font-weight: 600;">Drop any .stl file to load</div>
  </div>

  <div id="header-panel" class="ui-panel">
    <span class="logo-badge">Lumina 3D</span>
    <div>
      <div class="title-text">Lithophane Viewport</div>
      <div class="filename-text" id="display-filename">{filename}</div>
    </div>
  </div>

  <div id="controls-panel" class="ui-panel">
    <div class="control-group">
      <div class="group-label">Display Mode</div>
      <div class="btn-row">
        <button id="mode-backlit" class="btn active">Backlit</button>
        <button id="mode-solid" class="btn">Solid</button>
        <button id="mode-wire" class="btn">Wireframe</button>
      </div>
    </div>

    <div class="control-group" id="group-light-temp">
      <div class="group-label">Light Temperature</div>
      <div class="btn-row">
        <button id="temp-warm" class="btn active">Warm 2700K</button>
        <button id="temp-neutral" class="btn">Neutral</button>
        <button id="temp-cool" class="btn">Cool 6500K</button>
      </div>
    </div>

    <div class="control-group">
      <div class="group-label">Backlight Intensity</div>
      <div class="slider-row">
        <input type="range" id="slider-intensity" min="0.2" max="3.0" step="0.1" value="1.5" />
        <span class="slider-val" id="val-intensity">1.5×</span>
      </div>
    </div>

    <div class="control-group">
      <div class="group-label">Absorption Contrast</div>
      <div class="slider-row">
        <input type="range" id="slider-contrast" min="0.5" max="3.5" step="0.1" value="1.8" />
        <span class="slider-val" id="val-contrast">1.8</span>
      </div>
    </div>

    <div class="control-group">
      <div class="group-label">Backlight Distance</div>
      <div class="slider-row">
        <input type="range" id="slider-distance" min="10" max="150" step="5" value="40" />
        <span class="slider-val" id="val-distance">40 mm</span>
      </div>
    </div>

    <div class="control-group">
      <div class="group-label">Camera Angle</div>
      <div class="btn-row">
        <button id="view-front" class="btn">Front</button>
        <button id="view-back" class="btn">Back</button>
        <button id="view-iso" class="btn">Isometric</button>
      </div>
    </div>

    <div class="control-group">
      <div class="btn-row" style="grid-template-columns: 1fr 1fr;">
        <button id="btn-autorotate" class="btn">Auto Rotate</button>
        <button id="btn-snapshot" class="btn">Capture Image</button>
      </div>
    </div>
  </div>

  <div id="stats-panel" class="ui-panel">
    <div class="group-label" style="margin-bottom: 8px;">Mesh Statistics</div>
    <div class="stat-row">
      <span class="stat-label">Dimensions:</span>
      <span class="stat-val" id="stat-dims">-</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Thickness Range:</span>
      <span class="stat-val" id="stat-thick">-</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Facets (Triangles):</span>
      <span class="stat-val" id="stat-facets">-</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Estimated PLA Weight:</span>
      <span class="stat-val" id="stat-weight">-</span>
    </div>
  </div>

  <div id="instructions">
    Left Click: Rotate • Right Click: Pan • Scroll: Zoom
  </div>

  <script type="module">
    import * as THREE from 'three';
    import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
    import {{ STLLoader }} from 'three/addons/loaders/STLLoader.js';

    // Application state
    let scene, camera, renderer, controls, currentMesh = null;
    let backlight, frontLight, ambientLight;
    let initialStats = {stats_json};
    let currentMode = 'backlit';
    let lightColor = new THREE.Color(1.0, 0.85, 0.65); // Warm white default
    let minZ = 0, maxZ = 3;

    const embeddedBase64 = "{stl_b64}";

    const container = document.getElementById('canvas-container');

    // Shader for Backlight Lithophane Transmission
    const LithophaneShader = {{
      uniforms: {{
        uLightColor: {{ value: lightColor }},
        uLightPos: {{ value: new THREE.Vector3(0, 0, -40) }},
        uIntensity: {{ value: 1.5 }},
        uContrast: {{ value: 1.8 }},
        uMinZ: {{ value: 0.0 }},
        uMaxZ: {{ value: 3.0 }},
        uBaseColor: {{ value: new THREE.Color(0.95, 0.94, 0.91) }} // White resin/PLA tone
      }},
      vertexShader: `
        varying vec3 vWorldPosition;
        varying vec3 vNormal;
        varying float vLocalZ;

        void main() {{
          vNormal = normalize(normalMatrix * normal);
          vLocalZ = position.z;
          vec4 worldPos = modelMatrix * vec4(position, 1.0);
          vWorldPosition = worldPos.xyz;
          gl_Position = projectionMatrix * viewMatrix * worldPos;
        }}
      `,
      fragmentShader: `
        uniform vec3 uLightColor;
        uniform vec3 uLightPos;
        uniform float uIntensity;
        uniform float uContrast;
        uniform float uMinZ;
        uniform float uMaxZ;
        uniform vec3 uBaseColor;

        varying vec3 vWorldPosition;
        varying vec3 vNormal;
        varying float vLocalZ;

        void main() {{
          // Thickness calculation: normalize local relief depth
          float rangeZ = max(0.001, uMaxZ - uMinZ);
          float normThick = clamp((vLocalZ - uMinZ) / rangeZ, 0.0, 1.0);

          // Beer-Lambert physical absorption: thinner areas glow brighter
          float transmission = exp(-normThick * uContrast * 2.5);

          // Backlight directional falloff
          vec3 lightDir = normalize(uLightPos - vWorldPosition);
          float dist = length(uLightPos - vWorldPosition);
          float attenuation = 1.0 / (1.0 + 0.0005 * dist * dist);

          // Face illuminated from behind: dot product with surface normal
          float backFacing = max(0.2, dot(-vNormal, lightDir));

          // Combine transmitted light with gentle front ambient reflection
          vec3 backlitCol = uLightColor * transmission * uIntensity * attenuation * backFacing;
          vec3 ambientReflection = uBaseColor * 0.15;

          vec3 finalColor = backlitCol + ambientReflection;
          gl_FragColor = vec4(finalColor, 1.0);
        }}
      `
    }};

    function init() {{
      // Scene setup
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0d1117);

      camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
      camera.position.set(0, 0, 220);

      renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.0;
      container.appendChild(renderer.domElement);

      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;

      // Lights
      ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
      scene.add(ambientLight);

      frontLight = new THREE.DirectionalLight(0xffffff, 0.8);
      frontLight.position.set(50, 50, 100);
      scene.add(frontLight);

      backlight = new THREE.PointLight(lightColor, 2000, 300);
      backlight.position.set(0, 0, -40);
      scene.add(backlight);

      // Backlight visual helper
      const lightSphere = new THREE.Mesh(
        new THREE.SphereGeometry(3, 16, 16),
        new THREE.MeshBasicMaterial({{ color: lightColor }})
      );
      backlight.add(lightSphere);

      // Load embedded STL
      if (embeddedBase64 && embeddedBase64.length > 0) {{
        loadBase64STL(embeddedBase64);
      }}

      setupUI();
      setupDragAndDrop();

      window.addEventListener('resize', onWindowResize);
      animate();
    }}

    function loadBase64STL(b64) {{
      const binaryString = atob(b64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {{
        bytes[i] = binaryString.charCodeAt(i);
      }}
      parseSTLBuffer(bytes.buffer);
    }}

    function parseSTLBuffer(arrayBuffer) {{
      const loader = new STLLoader();
      const geometry = loader.parse(arrayBuffer);
      geometry.computeVertexNormals();
      geometry.center();

      geometry.computeBoundingBox();
      const bbox = geometry.boundingBox;
      minZ = bbox.min.z;
      maxZ = bbox.max.z;

      // Update shader relief bounds
      LithophaneShader.uniforms.uMinZ.value = minZ;
      LithophaneShader.uniforms.uMaxZ.value = maxZ;

      if (currentMesh) {{
        scene.remove(currentMesh);
        currentMesh.geometry.dispose();
      }}

      const material = createMaterial(currentMode);
      currentMesh = new THREE.Mesh(geometry, material);
      scene.add(currentMesh);

      // Fit camera
      const maxDim = Math.max(bbox.max.x - bbox.min.x, bbox.max.y - bbox.min.y, bbox.max.z - bbox.min.z);
      camera.position.set(0, 0, maxDim * 2.2);
      camera.lookAt(0, 0, 0);
      controls.target.set(0, 0, 0);

      // Backlight placement behind model
      backlight.position.set(0, 0, minZ - 40);
      LithophaneShader.uniforms.uLightPos.value = backlight.position;

      updateStatsUI(geometry, bbox);
    }}

    function createMaterial(mode) {{
      if (mode === 'backlit') {{
        frontLight.intensity = 0.1;
        ambientLight.intensity = 0.1;
        backlight.visible = true;
        return new THREE.ShaderMaterial({{
          uniforms: LithophaneShader.uniforms,
          vertexShader: LithophaneShader.vertexShader,
          fragmentShader: LithophaneShader.fragmentShader,
          side: THREE.DoubleSide
        }});
      }} else if (mode === 'solid') {{
        frontLight.intensity = 1.0;
        ambientLight.intensity = 0.5;
        backlight.visible = false;
        return new THREE.MeshStandardMaterial({{
          color: 0xe6edf3,
          roughness: 0.4,
          metalness: 0.1,
          side: THREE.DoubleSide
        }});
      }} else if (mode === 'wire') {{
        frontLight.intensity = 1.0;
        ambientLight.intensity = 0.5;
        backlight.visible = false;
        return new THREE.MeshBasicMaterial({{
          color: 0x58a6ff,
          wireframe: true
        }});
      }}
    }}

    function setMode(mode) {{
      currentMode = mode;
      document.querySelectorAll('#mode-backlit, #mode-solid, #mode-wire').forEach(b => b.classList.remove('active'));
      document.getElementById(`mode-${{mode}}`).classList.add('active');

      const isBacklit = (mode === 'backlit');
      document.getElementById('group-light-temp').style.display = isBacklit ? 'flex' : 'none';
      document.getElementById('slider-intensity').parentElement.parentElement.style.display = isBacklit ? 'flex' : 'none';
      document.getElementById('slider-contrast').parentElement.parentElement.style.display = isBacklit ? 'flex' : 'none';
      document.getElementById('slider-distance').parentElement.parentElement.style.display = isBacklit ? 'flex' : 'none';

      if (currentMesh) {{
        currentMesh.material = createMaterial(mode);
      }}
    }}

    function updateStatsUI(geometry, bbox) {{
      const w = (bbox.max.x - bbox.min.x).toFixed(1);
      const h = (bbox.max.y - bbox.min.y).toFixed(1);
      const d = (bbox.max.z - bbox.min.z).toFixed(1);
      const facets = geometry.attributes.position.count / 3;

      document.getElementById('stat-dims').textContent = `${{w}} × ${{h}} × ${{d}} mm`;
      document.getElementById('stat-thick').textContent = `${{bbox.min.z.toFixed(2)}} .. ${{bbox.max.z.toFixed(2)}} mm`;
      document.getElementById('stat-facets').textContent = facets.toLocaleString() + ' facets';

      if (initialStats && initialStats.weight_grams) {{
        document.getElementById('stat-weight').textContent = `${{initialStats.weight_grams}} g (PLA)`;
      }} else {{
        // Volume approx from bounding box volume * 0.4 estimated fill
        const approxVolCm3 = (w * h * d * 0.4) / 1000.0;
        document.getElementById('stat-weight').textContent = `~${{(approxVolCm3 * 1.24).toFixed(1)}} g (PLA)`;
      }}
    }}

    function setupUI() {{
      document.getElementById('mode-backlit').onclick = () => setMode('backlit');
      document.getElementById('mode-solid').onclick = () => setMode('solid');
      document.getElementById('mode-wire').onclick = () => setMode('wire');

      // Light temperature presets
      document.getElementById('temp-warm').onclick = (e) => {{
        setTemp(new THREE.Color(1.0, 0.85, 0.65), e.target);
      }};
      document.getElementById('temp-neutral').onclick = (e) => {{
        setTemp(new THREE.Color(1.0, 0.95, 0.90), e.target);
      }};
      document.getElementById('temp-cool').onclick = (e) => {{
        setTemp(new THREE.Color(0.85, 0.92, 1.0), e.target);
      }};

      function setTemp(col, targetBtn) {{
        lightColor = col;
        backlight.color = col;
        LithophaneShader.uniforms.uLightColor.value = col;
        document.querySelectorAll('#temp-warm, #temp-neutral, #temp-cool').forEach(b => b.classList.remove('active'));
        targetBtn.classList.add('active');
      }}

      // Sliders
      const intensitySlider = document.getElementById('slider-intensity');
      intensitySlider.oninput = (e) => {{
        const v = parseFloat(e.target.value);
        LithophaneShader.uniforms.uIntensity.value = v;
        document.getElementById('val-intensity').textContent = `${{v.toFixed(1)}}×`;
      }};

      const contrastSlider = document.getElementById('slider-contrast');
      contrastSlider.oninput = (e) => {{
        const v = parseFloat(e.target.value);
        LithophaneShader.uniforms.uContrast.value = v;
        document.getElementById('val-contrast').textContent = v.toFixed(1);
      }};

      const distSlider = document.getElementById('slider-distance');
      distSlider.oninput = (e) => {{
        const v = parseFloat(e.target.value);
        backlight.position.z = minZ - v;
        LithophaneShader.uniforms.uLightPos.value.z = minZ - v;
        document.getElementById('val-distance').textContent = `${{v}} mm`;
      }};

      // Camera views
      document.getElementById('view-front').onclick = () => {{
        controls.reset();
        camera.position.set(0, 0, 200);
        controls.target.set(0, 0, 0);
      }};
      document.getElementById('view-back').onclick = () => {{
        controls.reset();
        camera.position.set(0, 0, -200);
        controls.target.set(0, 0, 0);
      }};
      document.getElementById('view-iso').onclick = () => {{
        controls.reset();
        camera.position.set(140, 100, 140);
        controls.target.set(0, 0, 0);
      }};

      let autoRotate = false;
      document.getElementById('btn-autorotate').onclick = (e) => {{
        autoRotate = !autoRotate;
        controls.autoRotate = autoRotate;
        controls.autoRotateSpeed = 2.0;
        e.target.classList.toggle('active', autoRotate);
      }};

      document.getElementById('btn-snapshot').onclick = () => {{
        renderer.render(scene, camera);
        const dataURL = renderer.domElement.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = 'lithophane_viewport.png';
        link.href = dataURL;
        link.click();
      }};
    }}

    function setupDragAndDrop() {{
      const overlay = document.getElementById('drop-overlay');
      window.addEventListener('dragover', (e) => {{
        e.preventDefault();
        overlay.classList.add('visible');
      }});
      window.addEventListener('dragleave', (e) => {{
        if (e.relatedTarget === null) {{
          overlay.classList.remove('visible');
        }}
      }});
      window.addEventListener('drop', (e) => {{
        e.preventDefault();
        overlay.classList.remove('visible');
        if (e.dataTransfer.files.length > 0) {{
          const file = e.dataTransfer.files[0];
          if (file.name.toLowerCase().endsWith('.stl')) {{
            document.getElementById('display-filename').textContent = file.name;
            const reader = new FileReader();
            reader.onload = (event) => {{
              parseSTLBuffer(event.target.result);
            }};
            reader.readAsArrayBuffer(file);
          }}
        }}
      }});
    }}

    function onWindowResize() {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }}

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }}

    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
"""
    return html_content


def open_viewer(
    stl_path: str,
    output_html: str | None = None,
    open_browser: bool = True,
) -> str:
    """Renders the 3D viewer for an STL file and optionally opens it in the browser.

    Args:
        stl_path: Path to the target .stl file.
        output_html: Optional explicit path to save the generated HTML file.
                     If None, a temporary HTML file is generated.
        open_browser: Whether to open the generated HTML file in the default browser.

    Returns:
        Path to the generated HTML file.
    """
    html_content = generate_viewer_html(stl_path)

    if output_html is None:
        fd, output_html = tempfile.mkstemp(prefix="lumina_viewer_", suffix=".html")
        with open(fd, "w", encoding="utf-8") as f:
            f.write(html_content)
    else:
        out_dir = os.path.dirname(os.path.abspath(output_html))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)

    if open_browser:
        webbrowser.open(f"file://{os.path.abspath(output_html)}")

    return output_html
