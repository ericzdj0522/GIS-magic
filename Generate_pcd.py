import open3d as o3d
import numpy as np

def create_surface(size=20, resolution=0.5):
    xs = np.arange(-size/2, size/2, resolution)
    ys = np.arange(-size/2, size/2, resolution)
    xv, yv = np.meshgrid(xs, ys)
    zv = np.sin(xv * 0.3) * np.cos(yv * 0.3) * 0.5
    surface = np.stack([xv.flatten(), yv.flatten(), zv.flatten()], axis=1)
    return surface

def create_sphere(center, radius=1.5, density=0.1):
    phi = np.random.uniform(0, 2*np.pi, int(4*np.pi*radius**2/density**2))
    theta = np.random.uniform(0, np.pi, int(4*np.pi*radius**2/density**2))
    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)
    sphere = np.stack([x, y, z], axis=1)
    sphere += np.array(center)
    return sphere

def create_cube(center, size=2, density=0.2):
    x = np.arange(-size/2, size/2, density)
    y = np.arange(-size/2, size/2, density)
    z = np.arange(-size/2, size/2, density)
    points = []

    # Faces of the cube
    for face_x in [-size/2, size/2]:
        yv, zv = np.meshgrid(y, z)
        face_points = np.column_stack([
            np.full(yv.flatten().shape, face_x),
            yv.flatten(),
            zv.flatten()
        ])
        points.append(face_points)

    for face_y in [-size/2, size/2]:
        xv, zv = np.meshgrid(x, z)
        face_points = np.column_stack([
            xv.flatten(),
            np.full(xv.flatten().shape, face_y),
            zv.flatten()
        ])
        points.append(face_points)

    for face_z in [-size/2, size/2]:
        xv, yv = np.meshgrid(x, y)
        face_points = np.column_stack([
            xv.flatten(),
            yv.flatten(),
            np.full(xv.flatten().shape, face_z)
        ])
        points.append(face_points)

    cube = np.vstack(points)
    cube += np.array(center)
    return cube

def create_triangle(center, size=2, height=2, density=0.1):
    # Create a triangular prism
    points = []

    # Base triangle vertices
    v1 = np.array([-size/2, -size/3, 0])
    v2 = np.array([size/2, -size/3, 0])
    v3 = np.array([0, size/2, 0])

    # Generate points on triangle faces
    for i in range(int(height/density)):
        z_level = i * density
        # Bottom face
        for u in np.arange(0, 1, density*2):
            for v in np.arange(0, 1-u, density*2):
                point = u*v1 + v*v2 + (1-u-v)*v3
                point[2] = z_level
                points.append(point)

        # Top face
        for u in np.arange(0, 1, density*2):
            for v in np.arange(0, 1-u, density*2):
                point = u*v1 + v*v2 + (1-u-v)*v3
                point[2] = height + z_level
                points.append(point)

    triangle = np.array(points)
    triangle += np.array(center)
    return triangle

# Create scene with surface and geometric objects
surface = create_surface()

sphere1 = create_sphere(center=[4, 4, 2])
sphere2 = create_sphere(center=[-5, 3, 2], radius=1.2)

cube1 = create_cube(center=[6, -4, 1])
cube2 = create_cube(center=[-3, -6, 1], size=1.5)

triangle1 = create_triangle(center=[2, -2, 0])
triangle2 = create_triangle(center=[-4, 4, 0], size=1.5)

# Combine all objects
points = np.vstack([surface, sphere1, sphere2, cube1, cube2, triangle1, triangle2])

# Add slight noise (simulate LiDAR)
points += np.random.normal(0, 0.02, points.shape)

# Save as PCD
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

o3d.io.write_point_cloud("frame.pcd", pcd, write_ascii=True)
print("Generated frame.pcd with surface and geometric objects")