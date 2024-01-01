from dataclasses import dataclass, field
from typing import List
import math
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from .utils import haversine
from .coordinates import Coordinates
from .directions import Route

@dataclass
class Polygon(Route):
    coordinates: List[Coordinates]
    system: str = "unknown"
    
    def __post_init__(self):
        if self.coordinates[0] != self.coordinates[-1]:
            raise ValueError("Start {self.coordinates[0]} and end {self.coordinates[-1]} points should be the same")
    
    @classmethod
    def from_list(cls, coordinates_list: List[List[float]], system: str) -> 'Polygon':
        coordinates = [Coordinates.from_list(coord) for coord in coordinates_list]
        return cls(coordinates, system)
        
    @classmethod
    def from_route(cls, route: Route, system: str) -> 'Polygon':
        return cls(coordinates=route.coordinates, system=system)
    
    def scale_coordinates(self):
        coordinates_array = np.array([coord.to_tuple() for coord in self.coordinates])
        scaler = MinMaxScaler()
        scaled_coordinates = scaler.fit_transform(coordinates_array)

        scaled_polygon = Polygon(coordinates=[Coordinates.from_tuple(tuple(coord)) for coord in scaled_coordinates], system="cartesian")
        return scaled_polygon
    
    def centroid(self) -> Coordinates:
        if self.system == "GPS":
            raise NotImplementedError
        else:    
            x_coords = [p.latitude for p in self.coordinates]
            y_coords = [p.longitude for p in self.coordinates]
            self.centroid = Coordinates(sum(x_coords) / len(self.coordinates), sum(y_coords) / len(self.coordinates))
            return self.centroid
    
    def area(self) -> float:
        if self.system == "GPS":
            raise NotImplementedError
        else:
            n = len(self.coordinates)
            if n < 4: 
                return 0
        
            area = 0
            for i in range(n - 1):
                x1, y1 = self.coordinates[i].latitude, self.coordinates[i].longitude
                x2, y2 = self.coordinates[i + 1].latitude, self.coordinates[i + 1].longitude
                area += (x1 * y2) - (x2 * y1)
            self.area = abs(area) /2
            return self.area

    @property
    def perimeter(self) -> float:
        if system == "GPS":
            perimeter = 0
            for i in range(len(self.coordinates)):
                lat1, lon1 = self.coordinates[i]
                lat2, lon2 = self.coordinates[(i + 1) % len(self.coordinates)]
                perimeter += haversine(lon1, lat1, lon2, lat2)
            self.perimeter = perimeter
            return self.perimeter
            
        else:
            perimeter = 0
            for i in range(len(coordinates)):
                x1, y1 = coordinates[i]
                x2, y2 = coordinates[(i + 1) % len(coordinates)]
                perimeter += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            self.perimeter = perimeter
            return self.perimeter
            
    @property
    def perimeter(self) -> float:
        if self.system == "GPS":
            perimeter = 0
            for i in range(len(self.coordinates)):
                lat1, lon1 = self.coordinates[i].latitude, self.coordinates[i].longitude
                lat2, lon2 = self.coordinates[(i + 1) % len(self.coordinates)].latitude, self.coordinates[(i + 1) % len(self.coordinates)].longitude
                perimeter += haversine(lon1, lat1, lon2, lat2)
            self.perimeter = perimeter
            return self.perimeter
        else:
            perimeter = 0
            for i in range(len(self.coordinates)):
                x1, y1 = self.coordinates[i].latitude, self.coordinates[i].longitude
                x2, y2 = self.coordinates[(i + 1) % len(self.coordinates)].latitude, self.coordinates[(i + 1) % len(self.coordinates)].longitude
                perimeter += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            self.perimeter = perimeter
            return self.perimeter