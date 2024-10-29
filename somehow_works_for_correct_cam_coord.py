import pyrealsense2 as rs
import numpy as np
import open3d as o3d

# Configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Capture frames: depth and color
frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
color_frame = frames.get_color_frame()

if not depth_frame or not color_frame:
    raise RuntimeError("Failed to capture frames")

# Create point cloud object and map color to it
pc = rs.pointcloud()
pc.map_to(color_frame)
points = pc.calculate(depth_frame)

# Convert the point cloud to numpy arrays
vtx = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)  # Shape: (N, 3)
tex = np.asanyarray(points.get_texture_coordinates()).view(np.float32).reshape(-1, 2)  # Shape: (N, 2)

# Convert the color frame to a numpy array
color_image = np.asanyarray(color_frame.get_data())

# Helper function to map texture coordinates to RGB colors
def get_rgb_from_tex(tex_coords, color_image):
    """Convert normalized texture coordinates to RGB values."""
    h, w, _ = color_image.shape
    # Convert normalized coordinates to pixel indices
    u = (tex_coords[:, 0] * w).astype(int)
    v = (tex_coords[:, 1] * h).astype(int)
    # Clamp the indices to ensure valid range
    u = np.clip(u, 0, w - 1)
    v = np.clip(v, 0, h - 1)
    # Extract RGB values
    rgb = color_image[v, u, :] / 255.0  # Normalize to [0, 1]
    return rgb

# Map RGB colors to the vertices
colors = get_rgb_from_tex(tex, color_image)

# Create Open3D PointCloud object and assign points and colors
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(vtx)
pcd.colors = o3d.utility.Vector3dVector(colors)

#  Create a coordinate frame (axes) centered at the origin
axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2, origin=[0, 0, 0])

# Visualize the point cloud and the coordinate axes
o3d.visualization.draw_geometries([pcd, axes])

# Stop the RealSense pipeline
pipeline.stop()
