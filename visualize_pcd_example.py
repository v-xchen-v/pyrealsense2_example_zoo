import open3d as o3d

# Load and visualize the saved point cloud
pcd = o3d.io.read_point_cloud("data/debug_data/pointcloud_data/camera_captures/test.pcd")
o3d.visualization.draw_geometries([pcd])