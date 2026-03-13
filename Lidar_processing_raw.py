import open3d as o3d
import numpy as np
from sklearn.cluster import DBSCAN

# Load point cloud
pcd = o3d.io.read_point_cloud("frame.pcd")

# Downsample
pcd = pcd.voxel_down_sample(voxel_size=0.2)

# Ground segmentation
plane_model, inliers = pcd.segment_plane(
    distance_threshold=0.2,
    ransac_n=3,
    num_iterations=1000
)

ground = pcd.select_by_index(inliers)
non_ground = pcd.select_by_index(inliers, invert=True)

points = np.asarray(non_ground.points)

# DBSCAN clustering
labels = DBSCAN(eps=0.5, min_samples=10).fit_predict(points)
max_label = labels.max()

print(f"Detected {max_label + 1} clusters")

# Assign random colors to clusters
colors = np.zeros((points.shape[0], 3))

bounding_boxes = []

for cluster_id in range(max_label + 1):
    cluster_indices = np.where(labels == cluster_id)[0]
    cluster_points = points[cluster_indices]

    # Skip very small clusters
    if len(cluster_points) < 20:
        continue

    # Assign random color
    color = np.random.rand(3)
    colors[cluster_indices] = color

    # Create point cloud for cluster
    cluster_pcd = o3d.geometry.PointCloud()
    cluster_pcd.points = o3d.utility.Vector3dVector(cluster_points)

    # Create bounding box (axis-aligned)
    bbox = cluster_pcd.get_axis_aligned_bounding_box()
    bbox.color = (1, 0, 0)  # red

    bounding_boxes.append(bbox)

# Noise points = black
colors[labels == -1] = [0, 0, 0]

non_ground.colors = o3d.utility.Vector3dVector(colors)

# Ground = gray
ground.paint_uniform_color([0.6, 0.6, 0.6])

# Visualize everything
o3d.visualization.draw_geometries([ground, non_ground] + bounding_boxes)