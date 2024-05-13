import gpxpy
import gpxpy.gpx
import os
import matplotlib.pyplot as plt
from math import radians, sin, cos, asin, sqrt

def are_collinear(p1, p2, p3):
    """
    Check if three points are collinear.
    Each point is a tuple (x, y).
    """
    matrix = [
        [p1[0], p1[1], 1],
        [p2[0], p2[1], 1],
        [p3[0], p3[1], 1]
    ]
    # Calculate the determinant of the matrix
    det = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) - \
          matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) + \
          matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    return det == 0

def simplify_coordinates(coordinates):
    """
    Simplify a list of coordinates by removing collinear points.
    """
    simplified = [coordinates[0]]
    for i in range(1, len(coordinates) - 1):
        if not are_collinear(coordinates[i - 1], coordinates[i], coordinates[i + 1]):
            simplified.append(coordinates[i])
    simplified.append(coordinates[-1])
    return simplified

def order_coordinates_by_nearest_neighbors(coordinates):
    """
    Order a list of coordinates by nearest neighbors.

    Args:
    coordinates (list): List of tuples (longitude, latitude).

    Returns:
    list: Ordered list of coordinates.
    """
    if not coordinates:
        return []

    ordered_coords = [coordinates.pop(0)]  # Start with the first point and remove it from the list

    while coordinates:
        last_coord = ordered_coords[-1]
        # Find the nearest neighbor
        nearest_neighbor, nn_index = min(
            ((coord, idx) for idx, coord in enumerate(coordinates)),
            key=lambda item: haversine(last_coord[0], last_coord[1], item[0][0], item[0][1])
        )
        ordered_coords.append(nearest_neighbor)
        del coordinates[nn_index]  # Remove the nearest neighbor from the list

    return ordered_coords

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

def create_gpx_file(coordinates_list, filename, output_dir="../routes/"):
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    for coord in coordinates_list:
        segment.points.append(gpxpy.gpx.GPXTrackPoint(coord[0], coord[1]))
    
    full_path = os.path.abspath(os.path.join(output_dir, filename))
    with open(full_path, 'w') as f:
        f.write(gpx.to_xml())