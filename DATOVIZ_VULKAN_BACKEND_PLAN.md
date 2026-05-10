# Datoviz/Vulkan Volume Rendering Backend Plan

## Summary
Bring CellQuant’s rendering stack up to Imaris-style visualization by adding a dedicated Datoviz/Vulkan rendering backend in a separate optional package. The backend will provide perspective ray marching, smooth interaction, bounded VRAM residency, and lit/exportable surface rendering. CellQuant will load it through the existing `VolumeRenderBackend` validation contract and will only enable it in Auto mode after runtime validation passes. CPU reference rendering remains the correctness fallback, and `pygfx-wgpu` remains the current Windows direct-display path.

## 1. Backend Boundary & API Contract
The separate repository will not have direct knowledge of CellQuant's internals. It will expose a narrow, explicit renderer API:

- `initialize(parent_window_or_native_handle, config)`
- `set_volume_source(metadata)`
- `upload_bricks(keys, arrays)`
- `set_transfer_function(...)`
- `set_camera(...)`
- `set_lighting(...)`
- `set_meshes(...)`
- `render_interactive()`
- `render_final()`
- `pick(x, y)`
- `get_stats()`
- `shutdown()`

## 2. CellQuant Existing Backend Policy
CellQuant's backend strategy prioritizes stability and progressive enhancement:

1. `pygfx-wgpu`: Used for current Windows direct display and fast projection/volume preview.
2. `datoviz-vulkan`: Will be used once the separate repo exposes a validated adapter.
3. `zengl-opengl`: Only considered as a possible fallback experiment.
4. `cpu-reference`: Always available as the correctness baseline.
5. No `moderngl-compute`.

## 3. Validation Gates
The Datoviz/Vulkan backend will not be automatically selected simply because it imports successfully. It must pass strict validation gates:

- **Nonblank frame check**: Ensure the output is not empty.
- **CPU MIP/MinIP/Mean parity**: Output must match CPU reference rendering on a synthetic volume.
- **No stale artifacts**: Ensure no stale framebuffer or window-copy artifacts persist.
- **Responsiveness**: Validate camera drag responsiveness.
- **Memory-pressure test**: Ensure stability under high memory load.
- **Clean failure**: The backend must fail cleanly without crashing the GUI if Vulkan device allocation fails.

## 4. Projection vs Raymarching Separation
- CPU reference projection and pygfx-wgpu preview path remains the correctness baseline and handles fast direct-display projection.
- Datoviz/Vulkan targets high-quality interactive raymarching, surfaces, lighting, and residency.
- Projection parity tests are required, but Datoviz does not need to replace every projection path immediately.

## 5. Core Rendering Features
- **Progressive Quality**: Render low-resolution proxies during interaction and refine to high-quality raymarching when static.
- **Bounded VRAM Residency**: Implement a chunked texture upload strategy so massive datasets do not exhaust GPU memory.
- **Surface Rendering**: Add lit, exportable mesh rendering overlays synchronized with the volume.
- **Diagnostics**: Surface performance metrics (VRAM usage, frame times) directly through the backend's `get_stats()` API.

## 6. Revised Assumptions
- **Primary target**: Windows with Vulkan through Datoviz.
- OpenGL/ModernGL is not a production target.
- Datoviz integration lives in a separate package/repo.
- CellQuant loads the adapter optionally through `VolumeRenderBackend`.
- CPU fallback remains mandatory.

## 7. Packaging & API Deliverables (Acceptance Criteria)
- The Vulkan repo can be installed independently.
- CellQuant can detect it without importing a heavy runtime at startup.
- The backend reports device name, Vulkan backend, VRAM budget, feature support, and validation status.
- Failure of the backend never crashes the GUI.