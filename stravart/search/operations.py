from dataclasses import dataclass, field
from typing import List
import math
from math import radians, cos, sin, asin, sqrt
import numpy as np

from stravart.coordinates import Coordinates
from stravart.polygone import Polygon

@dataclass
class Translation:
    vector: Coordinates
    
    def apply(self, polygon: Polygon):
        if polygon.system == "GPS":
            raise NotImplementedError
        else:
            return Polygon(coordinates=[point - self.vector for point in polygon.coordinates], system=polygon.system)
@dataclass
class Scaling:
    scale_factor: float    
    
    def apply(self, polygon: Polygon):
        if polygon.system == "GPS":
            raise NotImplementedError
        else:
            return Polygon(coordinates=[point * self.scale_factor for point in polygon.coordinates], system=polygon.system)

@dataclass
class RadialDistortion:
    distortion_factor: float

    def apply(self, polygon: Polygon):
        if polygon.system == "GPS":
            raise NotImplementedError
        else:
            centroid = polygon.centroid
            distorted_polygon = []

            for point in polygon.coordinates:
                vector = point.to_numpy_array() - centroid.to_numpy_array()
                distorted_point = centroid.to_numpy_array() + vector * (1 + self.distortion_factor)
                distorted_polygon.append(Coordinates.from_tuple(distorted_point))

            return Polygon(coordinates=distorted_polygon, system=polygon.system)

@dataclass
class Rotation:
    angle: float
    
    def apply(self, polygon: Polygon):
        
        centroid = polygon.centroid
        angle_radians = math.radians(self.angle)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        ox, oy = centroid.to_numpy_array()
    
        rotated_coords = []
        for coord in polygon.coordinates:
            x, y = coord.to_tuple()
  
            # Translate point to center
            tx = x - ox
            ty = y - oy

            # Rotate point
            rx = tx * cos_angle - ty * sin_angle
            ry = tx * sin_angle + ty * cos_angle

            # Translate point back
            final_x = rx + ox
            final_y = ry + oy

            rotated_coords.append(Coordinates(final_x, final_y))
    
        return Polygon(coordinates=rotated_coords, system=polygon.system)
    

@dataclass
class Projection:
    center: Coordinates
    radius: float
    map_type : str = "GPS"
    
    def apply(self, polygon: Polygon):
        # Calculate the centroid of the contour
        centroid = polygon.centroid
    
        # Translate the contour to the origin
        translated_poly = Translation(vector=centroid).apply(polygon) 
    
        # Scale the contour to fit within the map radius
        max_distance = max(np.linalg.norm(point.to_numpy_array()) for point in polygon.coordinates)
        if max_distance == 0:
            raise ValueError("Degenerate Polygone, it's just zero!")
        else:
            scale_factor = self.radius / max_distance
            scaled_poly = Scaling(scale_factor).apply(translated_poly)
    
        # Invert coordinates before projecting to GPS. It's because Cartesian coordinates (x,y) corresponds to longitude, latitude.
        inverted_coordinates = [Coordinates(coord.longitude, coord.latitude) for coord in scaled_poly.coordinates]
        scaled_poly = Polygon(coordinates=inverted_coordinates)
        
        # Translate the contour to the map center
        center = Coordinates.from_tuple(self.center)
        final_contour = Translation(vector=-center).apply(scaled_poly)
        final_contour.system = self.map_type
    
        return final_contour

#### OLD
def rotate_coordinates(coords, angle_degrees, origin=(0, 0)):
    """
    Rotate a list of coordinates by a given angle around an origin.

    :param coords: List of tuples representing the coordinates (x, y).
    :param angle_degrees: Rotation angle in degrees.
    :param origin: A tuple representing the origin (x, y) for rotation.
    :return: List of rotated coordinates.
    """
    angle_radians = math.radians(angle_degrees)
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)
    ox, oy = origin

    rotated_coords = []
    for x, y in coords:
        # Translate point to origin
        tx = x - ox
        ty = y - oy

        # Rotate point
        rx = tx * cos_angle - ty * sin_angle
        ry = tx * sin_angle + ty * cos_angle

        # Translate point back
        final_x = rx + ox
        final_y = ry + oy

        rotated_coords.append((final_x, final_y))

    return rotated_coords

def sinusoidal_perturbation(polygon, amplitude=0.05, frequency=1):
    """
    Apply a sinusoidal perturbation to the vertices and midpoints of a polygon.

    :param polygon: List of tuples [(x1, y1), (x2, y2), ..., (xn, yn)]
    :param amplitude: Amplitude of the sinusoidal wave
    :param frequency: Frequency of the sinusoidal wave
    :return: Perturbed polygon as a list of tuples
    """
    perturbed_polygon = []
    num_points = len(polygon)

    for i in range(num_points):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % num_points]

        # Apply perturbation to the vertex
        wave_vertex = amplitude * np.sin(frequency * i * 2 * np.pi / num_points)
        perturbed_vertex = (x1 + wave_vertex, y1 + wave_vertex)
        perturbed_polygon.append(perturbed_vertex)

        # Midpoint of the edge
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2

        # Direction perpendicular to the edge
        perp_dir = np.array([-y2 + y1, x2 - x1])
        if np.linalg.norm(perp_dir) != 0:
            perp_dir = perp_dir / np.linalg.norm(perp_dir)

        # Sinusoidal perturbation for midpoint
        wave_mid = amplitude * np.sin(frequency * (i + 0.5) * 2 * np.pi / num_points)
        mid_x_perturbed = mid_x + wave_mid * perp_dir[0]
        mid_y_perturbed = mid_y + wave_mid * perp_dir[1]

        perturbed_polygon.append((mid_x_perturbed, mid_y_perturbed))

    return perturbed_polygon
