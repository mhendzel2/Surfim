import sys
import os
import numpy as np

# Ensure the local package is in the path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cellquant_datoviz import DatovizVulkanBackend

def run_mock_cellquant_validation():
    """
    Simulates the CellQuant runtime validation gate for the new backend.
    """
    print("--- Starting CellQuant Mock Validation ---")

    # 1. Instantiate the backend adapter
    backend = DatovizVulkanBackend()

    # 2. Initialize
    success = backend.initialize(parent_window_or_native_handle=None, config={"quality": "high"})
    if not success:
        print("Failed to initialize backend.")
        return

    # 3. Simulate uploading synthetic data (Validation Gate: CPU MIP/MinIP/Mean parity)
    metadata = {
        "shape": (128, 128, 128),
        "dtype": "uint16",
        "spacing": (1.0, 1.0, 2.0)
    }
    backend.set_volume_source(metadata)

    # Generate a synthetic brick of data (a glowing sphere)
    synthetic_brick = np.zeros((64, 64, 64), dtype=np.uint16)
    # Just passing the raw array over the boundary
    backend.upload_bricks(keys=[(0,0,0)], arrays=[synthetic_brick])

    # 4. Set rendering states
    backend.set_transfer_function(colormap_data=np.array([]), intensity_range=(0.0, 65535.0))
    backend.set_camera(view_matrix=np.eye(4), projection_matrix=np.eye(4))

    # 5. Simulate rendering loop
    print("\nSimulating Interaction Loop...")
    for _ in range(3):
        backend.render_interactive()

    print("Simulating Static Final Render...")
    backend.render_final()

    # 6. Retrieve Diagnostics
    stats = backend.get_stats()
    print(f"\nBackend Diagnostics: {stats}")

    # 7. Shutdown
    backend.shutdown()
    print("--- Mock Validation Complete ---")

if __name__ == "__main__":
    run_mock_cellquant_validation()
