# Lumina Project Roadmap

This document outlines the architectural milestones and feature pipeline for Lumina, focusing on core engine enhancements and the macOS desktop application.

## Table of Contents

- [Current State (v1.0.x)](#current-state-v10x)
- [Milestone 1: Desktop Application Prototype (v1.1.0)](#milestone-1-desktop-application-prototype-v110)
- [Milestone 2: Real-Time 3D Viewport and Light Simulation (v1.2.0)](#milestone-2-real-time-3d-viewport-and-light-simulation-v120)
- [Milestone 3: Advanced Geometry and Lamp Enclosures (v1.3.0)](#milestone-3-advanced-geometry-and-lamp-enclosures-v130)
- [Architecture Decision Matrix: Desktop UI](#architecture-decision-matrix-desktop-ui)

---

## Current State (v1.0.x)

- [x] High-performance heightmap generation from 2D raster images (JPG, PNG).
- [x] Archimedean Spiral Betty generator with brightness-to-stroke width modulation.
- [x] Boundary shape strategies: Rectangle, Circle, Heart.
- [x] Shape-conforming frame extrusion and Z-depth clamping.
- [x] Click-based CLI (`lumina flat`, `lumina spiral`).
- [x] Comprehensive CI test matrix (Python 3.10, 3.11, 3.12), pre-commit formatting, and automated semantic releases via Release Please.

---

## Milestone 1: Desktop Application Prototype (v1.1.0)

Goal: Deliver a standalone macOS desktop application (`.app` bundle) wrapping the Lumina core engine with an intuitive graphical user interface.

- [x] **Desktop GUI Foundation**:
  - Implement native file drag-and-drop zone for input images.
  - Interactive parameter controls: Width, Height, Min/Max Thickness, Resolution, and Frame Dimensions.
  - Shape selector dropdown (`rect`, `circle`, `heart`) with instantaneous 2D boundary preview.
- [x] **Dual Mode UI**:
  - Tab 1: Lithophane Generator (STL Export, live statistics, 3D viewport launch).
  - Tab 2: Spiral Betty Studio (PNG Export, radius/line sliders).
  - Single-click action to chain Spiral output into a Lithophane STL.
- [ ] **Packaging and Distribution**:
  - Standalone macOS application bundle (`Lumina.app`) using PyInstaller / Briefcase.
  - Apple Silicon (M-series) and Intel universal binary support.
  - Zero terminal prerequisite for end users.

---

## Milestone 2: Real-Time 3D Viewport and Light Simulation (v1.2.0)

Goal: Allow users to preview and inspect the 3D model and its physical light-transmission behavior before exporting.

- [x] **Integrated 3D Mesh Viewport**:
  - Interactive WebGL/Three.js 3D canvas (rotate, pan, zoom, auto-rotate, viewport snapshot).
  - Wireframe, solid matte shading, and physical backlit display modes.
  - Real-time mesh statistics: Dimensions, facet count, thickness range, and estimated physical PLA weight in grams.
  - Drag-and-drop support for any STL file with instant standalone browser preview.
- [x] **Backlight Transmission Shader**:
  - Physical lighting simulation showing how the lithophane appears when illuminated from behind (Beer-Lambert absorption model).
  - Adjustable light color temperature (Warm White 2700K, Neutral 4000K, Cool White 6500K).
  - Dynamic thickness-to-opacity absorption contrast, distance, and intensity sliders.

---

## Milestone 3: Advanced Geometry and Lamp Enclosures (v1.3.0)

Goal: Expand beyond flat/planar geometries to functional 3D home decor products.

- [ ] **Curved and Cylindrical Geometries**:
  - Cylindrical 360-degree lampshade generator.
  - Curved arc lithophanes with self-standing stable bases.
- [ ] **Mounting Accessories and Bases**:
  - Integrated LED tea-light base generator with snap-fit tolerance offsets.
  - Standard nightlight socket clip mounts.
- [ ] **Batch Processing and Slicer Presets**:
  - Multi-image batch export queue.
  - Turnkey slicer configuration exports (.ini / .json) optimized for Bambu Studio, PrusaSlicer, and Cura.

---

## Architecture Decision Matrix: Desktop UI

| Criteria | Option A: PySide6 (Qt) | Option B: Tauri + Three.js | Option C: Native SwiftUI |
| :--- | :--- | :--- | :--- |
| **Language** | Python | Rust + TypeScript | Swift |
| **Lumina Integration** | Direct in-process API calls | Python subprocess / IPC | Subprocess / C Foreign Interface |
| **3D Rendering** | Qt Quick 3D / PyVista | Three.js (WebGL / WebGPU) | SceneKit / RealityKit |
| **Bundle Size** | ~80–110 MB | ~40–60 MB (with embedded Python) | ~30 MB (requires external Python) |
| **macOS Native Feel** | High (macOS style integration) | High (macOS WebKit window) | Perfect (100% Cocoa native) |
| **Development Velocity** | Fast (single codebase in Python) | Moderate (dual frontend/backend) | Moderate (Swift bridging required) |

*Recommendation: Begin with Option A (PySide6) for rapid, zero-overhead direct integration with existing Lumina modules, while evaluating Option B for web-based 3D shader portability.*
