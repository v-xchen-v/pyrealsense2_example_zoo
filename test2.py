import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipeline.start(config)

# Capture a frame to get the point cloud
frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
if not depth_frame:
    raise RuntimeError("Failed to capture depth frame")

# Create the point cloud from depth data
pc = rs.pointcloud()
points = pc.calculate(depth_frame)
vtx = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)

# Prepare the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Randomly sample 1000 points from the point cloud for visualization
sample_indices = np.random.choice(vtx.shape[0], 10000, replace=False)
sampled_points = vtx[sample_indices]

# Plot the first 1000 points from the point cloud
ax.scatter(sampled_points[:, 0], sampled_points[:, 1], sampled_points[:, 2], s=1, c='blue')

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
