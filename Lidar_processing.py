import open3d as o3d
import numpy as np
from sklearn.cluster import DBSCAN
import random
from shape_classifier import ShapeClassifier, classify_shape, train_model
import torch
import os


# Load cloud
pcd = o3d.io.read_point_cloud("frame.pcd")

# Downsample
# pcd = pcd.voxel_down_sample(0.2)

# Plane segmentation
plane_model, inliers = pcd.segment_plane(
    distance_threshold=0.1,
    ransac_n=3,
    num_iterations=1000
)

# Select ground points and non ground points
ground = pcd.select_by_index(inliers)
non_ground = pcd.select_by_index(inliers, invert=True)

# Clustering obstacles
points = np.asarray(non_ground.points)
labels = DBSCAN(eps=0.6, min_samples=10).fit_predict(points)

# Number of clusters
max_label = labels.max()
print(f"Detected {max_label + 1} clusters")

# Assign colors
colors = np.zeros((points.shape[0], 3))

# Define bounding_boxes
bounding_boxes = []

# Load or train shape classification model
model_path = 'shape_classifier_model.pth'
if os.path.exists(model_path):
    model = ShapeClassifier()
    model.load_state_dict(torch.load(model_path))
    print("Loaded existing shape classifier model")
else:
    print("Training new shape classifier model...")
    model = train_model()
    print("Model training completed")

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

    # Debug: Print geometric features for analysis
    from shape_classifier import extract_geometric_features
    features = extract_geometric_features(cluster_points)

    # Calculate raw dimensions for debugging
    min_coords = np.min(cluster_points, axis=0)
    max_coords = np.max(cluster_points, axis=0)
    dimensions = max_coords - min_coords
    length, width, height = sorted(dimensions, reverse=True)

    print(f"Cluster {cluster_id} raw dimensions: L={length:.2f}, W={width:.2f}, H={height:.2f}")
    print(f"  Ratios: L/W={length/width:.2f}, L/H={length/height:.2f}, W/H={width/height:.2f}")
    print(f"  Sphericity: {features[8]:.3f}, Compactness: {features[9]:.3f}")
    print(f"  Aspect ratio: {features[10]*5:.2f}, Elongation: {features[11]:.3f}")

    # Classify shape using PyTorch model
    predicted_shape, confidence = classify_shape(cluster_points, model)

    # Create bounding box (axis-aligned) with color based on shape
    bbox = cluster_pcd.get_axis_aligned_bounding_box()

    # Color coding: cube=red, sphere=green, rectangular_cube=blue
    if predicted_shape == 'cube':
        bbox.color = (1, 0, 0)  # red
    elif predicted_shape == 'sphere':
        bbox.color = (0, 1, 0)  # green
    else:  # rectangular_cube
        bbox.color = (0, 0, 1)  # blue

    print(f"  Predicted: {predicted_shape} (confidence: {confidence:.3f})\n")

    bounding_boxes.append(bbox)

# Noise points = black
colors[labels == -1] = [0, 0, 0]

non_ground.colors = o3d.utility.Vector3dVector(colors)

# Ground = gray
ground.paint_uniform_color([0.6, 0.6, 0.6])

# Visualize everything
o3d.visualization.draw_geometries([ground, non_ground] + bounding_boxes)
