import numpy as np
import cv2
from scipy.spatial.distance import directed_hausdorff
from shapely.geometry import Polygon
    
def get_contour_from_points(points):
    """Convert a list of points to a contour format used by OpenCV."""
    return np.array(points, dtype=np.int32).reshape((-1, 1, 2))

def compare_contours(contour1, contour2):
    """Compare two contours using OpenCV's shape matching."""
    return cv2.matchShapes(contour1, contour2, cv2.CONTOURS_MATCH_I3, 0)

def hausdorff_distance(poly1, poly2):
    """
    Calculate the Hausdorff Distance between two polygons.
    
    :param poly1: List of (latitude, longitude) tuples for the first polygon.
    :param poly2: List of (latitude, longitude) tuples for the second polygon.
    :return: Hausdorff distance.
    """
    u = np.array(poly1)
    v = np.array(poly2)
    return max(directed_hausdorff(u, v)[0], directed_hausdorff(v, u)[0])

def calculate_angle(p1, p2, p3):
    """
    Calculate the angle formed by three points p1, p2, and p3.
    The angle is at p2.
    """
    v1 = np.array(p1) - np.array(p2)
    v2 = np.array(p3) - np.array(p2)
    ang1 = np.arctan2(*v1[::-1])
    ang2 = np.arctan2(*v2[::-1])
    angle = ang2 - ang1
    return np.degrees(angle)

def get_angles(polygon):
    """
    Calculate angles for each vertex in the polygon.
    """
    angles = []
    n = len(polygon)
    for i in range(n):
        p1 = polygon[i - 1]
        p2 = polygon[i]
        p3 = polygon[(i + 1) % n]
        angle = calculate_angle(p1, p2, p3)
        angles.append(angle)
    return angles

def compare_polygons(poly1, poly2, threshold=45):
    """
    Compare two polygons and return indices of poly2 where angles differ significantly.
    CAREFUL THIS SUPPOSE THEY HAVE THE SAME NUMBER OF ANGLES AND HAVE SAME ORIENTATIONS
    """
    angles1 = get_angles(poly1)
    angles2 = get_angles(poly2)
    mismatched_indices = []

    for i, (angle1, angle2) in enumerate(zip(angles1, angles2)):
        if abs(angle1 - angle2) > threshold:
            mismatched_indices.append(i)

    return mismatched_indices

def polygon_area(coordinates):
    """
    Calculate the area of a polygon using the shoelace formula.
    :param coordinates: List of (x, y) tuples representing the vertices of the polygon.
                        The last vertex should be the same as the first one.
    :return: The area of the polygon.
    """
    n = len(coordinates)
    if n < 4:  # Minimum 4 points (including the closing point)
        return 0

    area = 0
    for i in range(n - 1):
        x1, y1 = coordinates[i]
        x2, y2 = coordinates[i + 1]
        area += (x1 * y2) - (x2 * y1)
    return abs(area) /2

def polygon_areaBETTERMAYBE(coords):
    """Calculate the area of a polygon given its coordinates."""
    poly = Polygon(coords)
    return poly.area