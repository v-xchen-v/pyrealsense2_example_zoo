import pyrealsense2 as rs
import numpy as np

pipeline = rs.pipeline()
config = rs.config()
pipeline.start(config)
profile = pipeline.get_active_profile()

# Get depth intrinsics
depth_stream = profile.get_stream(rs.stream.depth)
depth_intrinsics = depth_stream.as_video_stream_profile().get_intrinsics()

# Get RGB intrinsics
color_stream = profile.get_stream(rs.stream.color)
rgb_intrinsics = color_stream.as_video_stream_profile().get_intrinsics()

# Get extrinsics from depth to RGB
depth_to_rgb_extrinsics = depth_stream.get_extrinsics_to(color_stream)
T_depth_to_rgb = np.eye(4)
T_depth_to_rgb[0:3, 0:3] = np.reshape(depth_to_rgb_extrinsics.rotation, [3, 3])
T_depth_to_rgb[0:3, 3] = depth_to_rgb_extrinsics.translation
# npdepth_to_rgb_extrinsics.rotation
# depth_to_rgb_extrinsics.translation
np.save('T_depth_to_rgb.npy', T_depth_to_rgb)
pass