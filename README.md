# Raw Vulkan Integration Plan for CellQuant

This document outlines the alternative plan to build a custom rendering engine directly with the Raw Vulkan API instead of using an intermediate framework like Datoviz.

While Datoviz provides a higher-level abstraction that accelerates development for scientific applications, building directly on Raw Vulkan offers the absolute maximum performance ceiling and total control over the rendering pipeline. This approach is akin to building a graphics engine from scratch and requires significant engineering investment.

## Trade-offs

| Approach        | Performance Ceiling | Development Speed | Risk    | Best For                     |
|-----------------|---------------------|-------------------|---------|------------------------------|
| Raw Vulkan      | Highest             | Slowest           | Highest | Building a graphics engine   |
| Datoviz         | Very high           | Faster            | Lower   | Building scientific software |
| OpenGL/ModernGL | Moderate to high    | Fast initially    | Medium  | Simpler apps, lower ceiling  |

### What You Gain
1. **Absolute Control**: Unfettered access to every render path, pipeline state, and memory allocation decision.
2. **No Abstraction Mismatch**: Ability to build exactly the primitives, shaders, and interaction models required for microscopy without wrestling with a third-party framework's assumptions.
3. **Extreme Optimization**: Potential for slightly better performance at the extreme end by eliminating abstraction overhead.

### What You Must Build (The "Lost" Datoviz Features)
1. **Scene and Visual Abstraction Layer**: Mapping domain objects (cells, spots, meshes) to draw calls and pipeline states.
2. **Memory Management**: Custom buffer/suballocation strategies to handle Vulkan's low-level memory requirements efficiently (avoiding small-buffer penalties).
3. **Camera and Interaction Framework**: Handling projections, view matrices, and mapping UI events to 3D navigation.
4. **GUI Integration**: Bridging Vulkan rendering with Qt or ImGui seamlessly.
5. **Object Picking System**: Translating 2D screen coordinates into 3D raycasts or implementing read-back buffers for object selection.
6. **Cross-Platform Infrastructure**: Managing Vulkan instance creation, physical device selection, and swapchains across Windows, macOS (via MoltenVK), and Linux.
7. **Debugging and Validation**: Extensive Vulkan Validation Layers integration, pipeline statistics, and custom rendering debug tools.

## Phased Execution Roadmap

### Phase 1: Core Infrastructure & Initialization
*   **Vulkan Context & Device Management**: Implement robust initialization, selecting appropriate physical devices (preferring discrete GPUs), setting up logical devices, queues, and command pools.
*   **Memory Allocator**: Integrate a robust allocator (e.g., VMA - Vulkan Memory Allocator) or write a custom suballocation system tailored for large microscopy datasets (chunked volumes, large geometry buffers).
*   **Swapchain & Render Pass Setup**: Establish the bridge between Vulkan and the application window system (Qt integration). Define base render passes and framebuffers.
*   **Shader Pipeline System**: Build a system to compile (e.g., using `glslangValidator` or `shaderc`), load, and cache SPIR-V shaders, along with defining pipeline layouts and descriptor sets.

### Phase 2: Scientific Primitives & Rendering
*   **Volume Raymarching**: Implement custom compute or fragment shaders for high-performance volume rendering (MIP, compositing, transfer functions).
*   **Geometry Pipelines**: Pipelines for meshes (surfaces, organelle boundaries) and points/sprites (spots, condensates).
*   **Texture Streaming**: Develop an asynchronous upload queue to stream multi-gigabyte OME-TIFF/Zarr chunks from CPU RAM to GPU memory without stalling the render thread.

### Phase 3: Interaction & GUI
*   **Camera System**: Implement Arcball, Fly, and Orthographic cameras with smooth interpolation and synchronized 2D/3D views.
*   **Hardware Picking**: Implement a dedicated render pass that outputs object IDs to an offscreen color attachment for pixel-perfect, hardware-accelerated object selection.
*   **UI Overlay Layer**: Integrate Dear ImGui (or map directly to Qt overlay widgets) to draw UI elements over the Vulkan viewport.

### Phase 4: Hardening & Tooling
*   **Extensive Debugging**:
    *   Enable and rigorously handle Vulkan Validation Layer output.
    *   Implement custom debug markers (using `VK_EXT_debug_utils`) for tools like RenderDoc or Nsight Graphics.
    *   Create internal telemetry for memory usage, buffer fragmentation, and frame timing.
*   **Cross-Platform QA**: Test on various IHV drivers (NVIDIA, AMD, Intel) on Windows and validate MoltenVK behavior on macOS.
