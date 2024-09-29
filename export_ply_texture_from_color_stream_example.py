# Ref: https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/export_ply_example.py

## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2017 Intel Corporation. All Rights Reserved.

#####################################################
##                  Export to PLY                  ##
#####################################################

# First import the library
import pyrealsense2 as rs


# Declare pointcloud object, for calculating pointclouds and texture mappings
pc = rs.pointcloud()
# We want the points object to be persistent so we can display the last cloud when a frame drops
points = rs.points()

# Declare RealSense pipeline, encapsulating the actual device and sensors
pipe = rs.pipeline()
config = rs.config()

# Enable depth stream
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
# Enable color stream
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming with chosen configuration
pipe.start(config)

# Create an align object
# rs.align allows us to perform alignment of depth frames to others (here to color frame)
align_to = rs.stream.color
align = rs.align(align_to)

# # We'll use the colorizer to generate texture for our PLY
# # (alternatively, texture can be obtained from color or infrared stream)
# colorizer = rs.colorizer()


try:
    # Wait for the next set of frames from the camera
    frames = pipe.wait_for_frames()
    
    # Align the depth frame to the color frame
    aligned_frames = align.process(frames)
    
    # Get aligned frames
    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    
    # Check if both frames are valid
    if not aligned_depth_frame or not color_frame:
        raise RuntimeError("Could not get aligned frames")
    
    # Map the color frame to the point cloud
    pc.map_to(color_frame)
    
    # Calculate the point cloud with the aligned depth frame
    points = pc.calculate(aligned_depth_frame)
    
    # Create save_to_ply object
    ply = rs.save_to_ply("1.ply")

    # Set options to the desired values
    # In this example we'll generate a textual PLY with normals (mesh is already created by default)
    ply.set_option(rs.save_to_ply.option_ply_binary, False)
    ply.set_option(rs.save_to_ply.option_ply_normals, True)

    print("Saving to 1.ply...")
    # Apply the processing block to the frameset which contains the depth frame and the texture
    ply.process(frames)
    print("Done")
finally:
    pipe.stop()