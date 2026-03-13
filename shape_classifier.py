import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, List


class ShapeClassifier(nn.Module):
    """
    Neural network to classify 3D shapes from LiDAR clusters
    Classes: 0=cube, 1=sphere, 2=rectangular_cube
    """

    def __init__(self, input_features=12, hidden_dim=64, num_classes=3):
        super(ShapeClassifier, self).__init__()

        self.fc1 = nn.Linear(input_features, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return F.softmax(x, dim=1)


def extract_geometric_features(points: np.ndarray) -> np.ndarray:
    """
    Extract geometric features from 3D point cluster

    Features extracted:
    1-3: dimensions (length, width, height) of bounding box
    4: volume of bounding box
    5: surface area approximation
    6-8: ratio of dimensions (l/w, l/h, w/h)
    9: sphericity (surface area of equivalent sphere / actual surface area)
    10: compactness (volume^(2/3) / surface area)
    11: aspect ratio (max_dim / min_dim)
    12: elongation ((max_dim - min_dim) / max_dim)
    """

    # Basic bounding box dimensions
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    dimensions = max_coords - min_coords
    length, width, height = sorted(dimensions, reverse=True)

    # Volume and surface area
    volume = length * width * height
    surface_area = 2 * (length * width + length * height + width * height)

    # Dimensional ratios
    l_w_ratio = length / width if width > 0 else 1.0
    l_h_ratio = length / height if height > 0 else 1.0
    w_h_ratio = width / height if height > 0 else 1.0

    # Sphericity (how sphere-like the shape is)
    equiv_sphere_radius = (3 * volume / (4 * np.pi)) ** (1/3)
    equiv_sphere_surface = 4 * np.pi * equiv_sphere_radius**2
    sphericity = equiv_sphere_surface / surface_area if surface_area > 0 else 0

    # Compactness
    compactness = (volume**(2/3)) / surface_area if surface_area > 0 else 0

    # Aspect ratio and elongation
    max_dim = max(dimensions)
    min_dim = min(dimensions)
    aspect_ratio = max_dim / min_dim if min_dim > 0 else 1.0
    elongation = (max_dim - min_dim) / max_dim if max_dim > 0 else 0

    # Normalize features to match training data
    features = np.array([
        length / 5.0,        # Better normalization range
        width / 5.0,
        height / 5.0,
        volume / 125.0,      # Adjusted for new size range
        surface_area / 60.0, # Adjusted for new size range
        l_w_ratio,           # Ratios already normalized
        l_h_ratio,
        w_h_ratio,
        sphericity,          # Already 0-1
        compactness,         # Already normalized
        aspect_ratio / 5.0,  # Better normalization
        elongation           # Already 0-1
    ])

    return features


def classify_shape(points: np.ndarray, model: ShapeClassifier) -> Tuple[str, float]:
    """
    Classify a point cluster into cube, sphere, or rectangular cube
    Uses hybrid approach: ML model + geometric rules

    Returns:
        Tuple of (predicted_class, confidence)
    """

    features = extract_geometric_features(points)
    features_tensor = torch.FloatTensor(features).unsqueeze(0)

    # Get ML model prediction
    model.eval()
    with torch.no_grad():
        outputs = model(features_tensor)
        probabilities = outputs.squeeze()

        predicted_class_idx = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_class_idx].item()

    class_names = ['cube', 'sphere', 'rectangular_cube']
    predicted_class = class_names[predicted_class_idx]

    # Apply geometric rules for better sphere detection
    # Calculate raw dimensions
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    dimensions = max_coords - min_coords
    length, width, height = sorted(dimensions, reverse=True)

    # Dimensional ratios
    l_w_ratio = length / width if width > 0 else 1.0
    l_h_ratio = length / height if height > 0 else 1.0
    w_h_ratio = width / height if height > 0 else 1.0

    # Sphere detection rules (more flexible)
    max_ratio = max(l_w_ratio, l_h_ratio, w_h_ratio)
    avg_ratio = (l_w_ratio + l_h_ratio + w_h_ratio) / 3
    is_sphere_like = (
        max_ratio <= 1.35 and      # Allow slightly more variation
        avg_ratio <= 1.25 and     # Average should be low
        features[8] > 0.78 and     # High sphericity
        sum([r <= 1.20 for r in [l_w_ratio, l_h_ratio, w_h_ratio]]) >= 2  # At least 2 ratios should be very similar
    )

    # Override prediction if geometric rules strongly suggest sphere
    if is_sphere_like and predicted_class != 'sphere':
        # Check if it's not clearly rectangular
        if max_ratio < 1.5:  # Not clearly elongated
            predicted_class = 'sphere'
            confidence = min(0.85, confidence + 0.1)  # Boost confidence but cap it

    return predicted_class, confidence


def create_synthetic_training_data(num_samples_per_class=1000) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Generate synthetic training data for the three shape classes with clear distinctions
    """

    features_list = []
    labels_list = []

    for class_idx in range(3):
        for _ in range(num_samples_per_class):
            if class_idx == 0:  # Cube - all dimensions similar but with some variation (ratio 1.0-1.25)
                base_size = np.random.uniform(0.8, 4.0)
                # Small variation but still cube-like
                noise = np.random.normal(0, 0.03 * base_size, 3)
                dims = np.array([base_size, base_size, base_size]) + noise
                dims = np.maximum(dims, 0.1)
                # Keep it cube-like but allow more variation than spheres
                dims = np.sort(dims)
                if dims[2]/dims[0] > 1.25:  # Allow more variation for cubes
                    dims = dims * (dims[0]/dims[2] * 1.2)

            elif class_idx == 1:  # Sphere - very similar dimensions but more tolerant (ratio 1.0-1.15)
                base_size = np.random.uniform(0.8, 4.0)
                # Spheres should have the most similar dimensions
                noise = np.random.normal(0, 0.02 * base_size, 3)
                dims = np.array([base_size, base_size, base_size]) + noise
                dims = np.maximum(dims, 0.1)
                # Keep spheres very tight in dimensional ratios
                dims = np.sort(dims)
                if dims[2]/dims[0] > 1.12:  # Very tight constraint for spheres
                    dims = dims * (dims[0]/dims[2] * 1.08)

            else:  # Rectangular cube - clearly different dimensions (aspect ratio > 2.0)
                # Generate dimensions with clear differences
                base = np.random.uniform(0.8, 2.0)
                small_dim = base
                medium_dim = base * np.random.uniform(1.8, 2.5)
                large_dim = base * np.random.uniform(3.0, 4.5)

                # Randomize the order
                dims = np.array([small_dim, medium_dim, large_dim])
                np.random.shuffle(dims)

            # Calculate features with more emphasis on shape characteristics
            length, width, height = sorted(dims, reverse=True)
            volume = length * width * height

            # More accurate surface area calculation
            surface_area = 2 * (length * width + length * height + width * height)

            # Dimensional ratios - key for distinguishing shapes
            l_w_ratio = length / width if width > 0 else 1.0
            l_h_ratio = length / height if height > 0 else 1.0
            w_h_ratio = width / height if height > 0 else 1.0

            # Enhanced sphericity calculation
            equiv_sphere_radius = (3 * volume / (4 * np.pi)) ** (1/3)
            equiv_sphere_surface = 4 * np.pi * equiv_sphere_radius**2
            sphericity = equiv_sphere_surface / surface_area if surface_area > 0 else 0

            # Compactness - spheres should have highest compactness
            compactness = (volume**(2/3)) / surface_area if surface_area > 0 else 0

            # Aspect ratio and elongation - important for rectangular shapes
            max_dim = max(dims)
            min_dim = min(dims)
            aspect_ratio = max_dim / min_dim if min_dim > 0 else 1.0
            elongation = (max_dim - min_dim) / max_dim if max_dim > 0 else 0

            # Enhanced features with better discrimination
            # Add variance in dimensions as a key feature
            dim_variance = np.var([length, width, height])

            # Add ratio standard deviation as discrimination feature
            ratios = [l_w_ratio, l_h_ratio, w_h_ratio]
            ratio_std = np.std(ratios)

            # Normalize features to improve training stability
            features = np.array([
                length / 5.0,        # Better normalization range
                width / 5.0,
                height / 5.0,
                volume / 125.0,      # Adjusted for new size range
                surface_area / 60.0, # Adjusted for new size range
                l_w_ratio,           # Ratios already normalized
                l_h_ratio,
                w_h_ratio,
                sphericity,          # Already 0-1
                compactness,         # Already normalized
                aspect_ratio / 5.0,  # Better normalization
                elongation           # Already 0-1
            ])

            features_list.append(features)
            labels_list.append(class_idx)

    features_array = np.array(features_list)
    labels_array = np.array(labels_list)

    return torch.FloatTensor(features_array), torch.LongTensor(labels_array)


def train_model(num_epochs=200, learning_rate=0.003) -> ShapeClassifier:
    """
    Train the shape classifier model
    """

    # Generate training data
    X_train, y_train = create_synthetic_training_data()

    # Initialize model
    model = ShapeClassifier()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop
    model.train()
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

    # Calculate accuracy
    model.eval()
    with torch.no_grad():
        outputs = model(X_train)
        _, predicted = torch.max(outputs.data, 1)
        accuracy = (predicted == y_train).float().mean().item()
        print(f'Training Accuracy: {accuracy:.4f}')

    return model


if __name__ == "__main__":
    # Train and save model
    print("Training shape classifier...")
    model = train_model()

    # Save the trained model
    torch.save(model.state_dict(), 'shape_classifier_model.pth')
    print("Model saved as 'shape_classifier_model.pth'")