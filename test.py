import pyrealsense2 as rs
import numpy as np
import cv2
import open3d as o3d

def _show_point_cloud_window(points: np.ndarray):
    viewer = o3d.visualization.Visualizer()
    viewer.create_window()
    opt = viewer.get_render_option()
    pcd = o3d.geometry.PointCloud()
    vtx = points #np.asanyarray( point_cloud.points)  # XYZ
    flipy_points = vtx
    flipy_points[:, 1] *= -1 
    flipy_points[:, 2] *= -1 
    # # flipy_points[:, 0] *= 0.001   
    # R_x_90 = np.array([[1, 0, 0],
    #                [0, 0, -1],
    #                [0, 1, 0]])
    # R_y_90 = np.array([[0, 0, 1],
    #                [0, 1, 0],
    #                [-1, 0, 0]])
    # R_z_90 = np.array([[0, -1, 0],
    #                [1, 0, 0],
    #                [0, 0, 1]])
    # T_depth_to_rgb = np.load('calibration/calibration_data/camera1/depth_to_rgb/T_depth_to_rgb.npy')
    # T_rot180_x = np.eye(4)
    # T_rot180_x[1, 1] = -1
    # T_rot180_x[2, 2] = -1
    # flipy_points = _make_point_cloud_xyz_array(np.array([
    #                  T_depth_to_rgb @ T_rot180_x @ p 
    #                  for p in _make_point_cloud_homogeneous(flipy_points)]))
    pcd.points = o3d.utility.Vector3dVector(flipy_points)
    # viewer.add_geometry(pcd)
    
    # draw the point cloud with texture color
    # pcd.colors = point_cloud.colors
    viewer.add_geometry(pcd)
    opt.show_coordinate_frame = True
    opt.background_color = np.asarray([0, 0, 0])
    viewer.run()
    viewer.destroy_window()
        
# Configure the pipeline
pipeline = rs.pipeline()
config = rs.config()

# Enable depth and color streams
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Initialize the point cloud object
pc = rs.pointcloud()

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        # Generate point cloud using depth frame
        pc.map_to(color_frame)  # Map color frame to the point cloud
        points = pc.calculate(depth_frame)  # Calculate the point cloud

        # Convert the point cloud to numpy array (x, y, z) points
        vtx = np.asanyarray(points.get_vertices(2))  # Shape: (640*480, 3)
        tex = np.asanyarray(points.get_texture_coordinates(2))
        _show_point_cloud_window(vtx)
        # Reshape to 2D: (480, 640, 3) for easy processing
        vtx = vtx.reshape((480, 640, 3))

        # Display color frame using OpenCV
        color_image = np.asanyarray(color_frame.get_data())
        cv2.imshow("RealSense Color Stream", color_image)

        # Accessing the 3D point at (row, col) = (240, 320)
        point = vtx[240, 320]  # Example: center point
        x, y, z = point  # Extract the coordinates
        print(f"3D coordinates at (240, 320): X={x}, Y={y}, Z={z}")
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
