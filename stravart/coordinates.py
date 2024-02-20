from dataclasses import dataclass, field
from typing import List
import numpy as np
import requests
from config import MAPBOX_ACCESS_TOKEN
from geopy.distance import great_circle

@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __eq__(self, other):
        if not isinstance(other, Coordinates):
            return NotImplemented
        return (self.latitude, self.longitude) == (other.latitude, other.longitude)

    def __hash__(self):
        return hash((self.latitude, self.longitude))
        
    def __iter__(self):
        yield self.latitude
        yield self.longitude
    
    def to_tuple(self):
        return (self.latitude, self.longitude)

    @staticmethod
    def from_tuple(coords_tuple):
        if coords_tuple:
            return Coordinates(latitude=coords_tuple[0], longitude=coords_tuple[1])
        else:
            return None

    def to_numpy_array(self):
        return np.array([self.latitude, self.longitude])
        
    def __repr__(self):
        return f"({self.latitude}, {self.longitude})"
        
    def __add__(self, other):
        if not isinstance(other, Coordinates):
            return NotImplemented
        return Coordinates(self.latitude + other.latitude, self.longitude + other.longitude)
    
    def __sub__(self, other):
        if not isinstance(other, Coordinates):
            return NotImplemented
        return Coordinates(self.latitude - other.latitude, self.longitude - other.longitude)
    
    def __neg__(self):
        return Coordinates(-self.latitude, -self.longitude)
    
    def __mul__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Coordinates(self.latitude * other, self.longitude * other)

    @classmethod
    def from_list(cls, coordinates: List[float]) -> 'Coordinates':
        if len(coordinates) != 2:
            raise ValueError("Coordinates must have only two values.")
        return cls(latitude=coordinates[0], longitude=coordinates[1])

    def get_nearest_bicycle_road_point(self, dist=1000):
        '''
        try:
            mode = "cycling"
            access_token = MAPBOX_ACCESS_TOKEN
            coordinates = f"{self.longitude},{self.latitude};{self.longitude},{self.latitude}"
            url = f"https://api.mapbox.com/directions/v5/mapbox/{mode}/{coordinates}"

            params = {
                'access_token': access_token,
                'geometries': 'geojson',
                'radiuses': f"{dist};{dist}"
            }

            response = requests.get(url, params=params)
            data = response.json()

            if data['code'] != 'Ok':
                raise Exception("Mapbox API error: " + data['code'])
            print(data['routes'])
            nearest_point = None
            min_distance = float('inf')
            for route in data['routes']:
                for leg in route['legs']:
                    for step in leg['steps']:
                        step_point = (step['maneuver']['location'][1], step['maneuver']['location'][0])
                        distance = great_circle((self.latitude, self.longitude), step_point).meters
                        if distance < min_distance:
                            nearest_point = step_point
                            min_distance = distance

            return nearest_point if nearest_point else None

        except Exception as e:
            print(f"Error getting closest bicycle coordinate for {(self.latitude, self.longitude)}: {e}")
            return None
'''
        try:
            overpass_url = "http://overpass-api.de/api/interpreter"
            lat, lon  = self.latitude, self.longitude
            overpass_query = f"""
            [out:json];
                          (
            way(around:{dist},{lat},{lon})["highway"="cycleway"];
            way(around:{dist},{lat},{lon})["bicycle"="designated"];
            way(around:{dist},{lat},{lon})["bicycle"="yes"];
            way(around:{dist},{lat},{lon})["highway"="path"]["bicycle"!="no"];
            way(around:{dist},{lat},{lon})["highway"="footway"]["bicycle"="yes"];
            way(around:{dist},{lat},{lon})["highway"="service"]["bicycle"!="no"];
            way(around:{dist},{lat},{lon})["highway"="residential"]["bicycle"!="no"];
            );
        
            (._;>;);
            out center;
            """
            response = requests.get(overpass_url, params={'data': overpass_query})
            data = response.json()
            
            nearest_point = None
            min_distance = float('inf')
        
            for element in data['elements']:
                if 'center' in element:
                    center = element['center']
                    road_point = (center['lat'], center['lon'])
                    distance = great_circle((lat, lon), road_point).meters
                    if distance < min_distance:
                        nearest_point = road_point
                        min_distance = distance
            
            return Coordinates.from_tuple(nearest_point)
        except Exception as e:
            print(f"Error getting closest bicycle coordinate for {(lat, lon)}: {e}")
            return None
