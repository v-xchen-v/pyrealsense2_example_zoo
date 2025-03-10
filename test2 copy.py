import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Capture a frame to get the point cloud
frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
color_frame = frames.get_color_frame()

if not depth_frame or not color_frame:
    raise RuntimeError("Failed to capture frames")

# Create the point cloud from depth data
pc = rs.pointcloud()
pc.map_to(color_frame)  # Map color to point cloud
points = pc.calculate(depth_frame)
vtx = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
tex = np.asanyarray(points.get_texture_coordinates()).view(np.float32).reshape(-1, 2)  # Shape (N, 2)

# Convert color frame to a numpy array
color_image = np.asanyarray(color_frame.get_data())

# Helper function to get RGB values from the texture coordinates
def get_color_from_tex(tex_coords, color_image):
    """Convert normalized texture coordinates to RGB values."""
    h, w, _ = color_image.shape
    # Convert normalized (0-1) coordinates to pixel coordinates
    u = (tex_coords[:, 0] * w).astype(int)
    v = (tex_coords[:, 1] * h).astype(int)
    # Ensure valid pixel range
    u = np.clip(u, 0, w - 1)
    v = np.clip(v, 0, h - 1)
    # Extract RGB values
    return color_image[v, u, :]

# Get RGB values for the vertices
colors = get_color_from_tex(tex, color_image) / 255.0  # Normalize to [0, 1]


# Prepare the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Randomly sample 1000 points from the point cloud for visualization
sample_indices = np.random.choice(vtx.shape[0], 10000, replace=False)
sampled_points = vtx[sample_indices]
sampled_colors = colors[sample_indices]

# Plot the first 1000 points from the point cloud
ax.scatter(sampled_points[:, 0], sampled_points[:, 1], sampled_points[:, 2],  s=5, c=sampled_colors, marker='o')

# Draw coordinate axes
ax.quiver(0, 0, 0, 0.1, 0, 0, color='r', label='X-axis')
ax.quiver(0, 0, 0, 0, 0.1, 0, color='g', label='Y-axis')
ax.quiver(0, 0, 0, 0, 0, 0.1, color='b', label='Z-axis')

# Set axis limits and labels
ax.set_xlim([-0.2, 0.2])
ax.set_ylim([-0.2, 0.2])
ax.set_zlim([0, 0.5])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.legend()
plt.show(block=True)

# Stop the pipeline
pipeline.stop()
