from dataclasses import dataclass, field
from typing import List
from joblib import Parallel, delayed
import requests
import googlemaps
from geopy.distance import great_circle

from .coordinates import Coordinates

@dataclass(frozen=True)
class Direction:
    start: Coordinates
    end: Coordinates

    def __eq__(self, other):
        if not isinstance(other, Direction):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))
        
    @classmethod
    def from_coordinates(cls, start: Coordinates, end: Coordinates):
        return cls(start=start, end=end)

    def get_shortest_path_google_maps(self, mode="walking", alternatives=True, decimals=4):
        gmaps = googlemaps.Client(key='AIzaSyAlFJy2mE0LKbLHJS7z4Kz9WgB2B76LtrA')
        start_tuple = tuple(self.start)
        end_tuple = tuple(self.end)
        print(start_tuple, end_tuple)
        # Get directions
        directions_result = gmaps.directions(start_tuple, end_tuple, mode=mode, alternatives=alternatives)

        if directions_result:
            min_area = float('inf')
            best_route = None
            for route in directions_result:
                # Extract coordinates from the route
                steps = route['legs'][0]['steps']
                path_points = [(round(self.start.latitude, decimals), round(self.start.longitude, decimals))]
                for step in steps:
                    start_location = step['start_location']
                    #end_location = step['end_location']
                    path_points.append((round(start_location['lat'], decimals), round(start_location['lng'], decimals)))
                    #path_points.append((round(end_location['lat'], decimals), round(end_location['lng'], decimals)))
            
                # Add the end point and remove duplicates
                path_points[-1] = (round(self.end.latitude, decimals), round(self.end.longitude, decimals))
                #path_points.append((round(self.end.latitude, decimals), round(self.end.longitude, decimals)))
                unique_path_points = list(dict.fromkeys(path_points))

                # Calculate area
                from .polygone import Polygon
                poly_list = unique_path_points + [unique_path_points[0]]
                polygon = Polygon.from_list(poly_list, system="GPS")
                normed_polygon = polygon.scale_coordinates()
                area = normed_polygon.area
                if area < min_area:
                    min_area = area
                    best_route = unique_path_points
            print("best",best_route)
            print("-----------")        
            return Route.from_list(best_route)
        
        '''
        steps = directions_result[0]['legs'][0]['steps']
        path_points = [(round(self.start.latitude, decimals), round(self.start.longitude, decimals))]
        for step in steps:
            start_location = step['start_location']
            end_location = step['end_location']
            path_points.append((round(start_location['lat'], decimals), round(start_location['lng'], decimals)))
            path_points.append((round(end_location['lat'], decimals), round(end_location['lng'], decimals)))
    
        # Add the end point and remove duplicates
        path_points.append((round(self.end.latitude, decimals), round(self.end.longitude, decimals)))
        unique_path_points = list(dict.fromkeys(path_points))
        return Route.from_list(unique_path_points)'''

    def get_mapbox_routes(self, mode="cycling", alternatives=True, decimals=4):
        access_token = "sk.eyJ1IjoibGVvZHMiLCJhIjoiY2xxczJpaDJ5MmdibDJrcDllejM1eWJocyJ9.IFk3eb3RMfndTJIIM_pVxQ"
        url = f"https://api.mapbox.com/directions/v5/mapbox/{mode}/{self.start.longitude},{self.start.latitude};{self.end.longitude},{self.end.latitude}"
        params = {
            'alternatives': str(alternatives).lower(),
            'geometries': 'geojson',
            'access_token': access_token
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            routes = response.json()['routes']
            min_area = float('inf')
            best_route = None
            for route in routes:
                # Swap coordinates from [lon, lat] to [lat, lon] + rounding
                route['geometry']['coordinates'] = [[round(lat,decimals), round(lon,decimals)] for lon, lat in route['geometry']['coordinates']]
                coordinates = route['geometry']['coordinates']
                
                # Calculate area
                from .polygone import Polygon
                from sklearn.preprocessing import MinMaxScaler
                polygon = Polygon.from_list(poly_list, system="GPS")
                normed_polygon = polygon.scale_coordinates()
                area = normed_polygon.area
                if area < min_area:
                    min_area = area
                    best_route = route
            return Route.from_list(best_route['geometry']['coordinates'])
        else:
            return None

    def get_shortest_path_osrm(self):
        """
        Get the shortest path between start_point and end_point using OSRM.
        :param start_point: Tuple of (latitude, longitude) for the start point.
        :param end_point: Tuple of (latitude, longitude) for the end point.
        :return: List of (latitude, longitude) tuples representing the path.
        """
        # Construct the OSRM API request URL
        osrm_route_url = f"http://router.project-osrm.org/route/v1/bicycle/{self.start.longitude},{self.start.latitude};{self.end.longitude},{self.end.latitude}?overview=full&geometries=geojson"
        # Make the request to the OSRM API
        response = requests.get(osrm_route_url)
        if response.status_code != 200:
            raise Exception("OSRM API request failed")
    
        # Parse the response JSON
        route_data = json.loads(response.text)
    
        # Extract the route geometry from the response
        geometry = route_data['routes'][0]['geometry']['coordinates']
    
        # Convert coordinates to (latitude, longitude) format
        path = [(lat, lon) for lon, lat in geometry]
    
        return Route.from_list(path)

@dataclass
class Route:
    coordinates: List[Coordinates] = field(default_factory=list)

    def __iter__(self):
        return iter(self.coordinates)
    
    def __len__(self):
        return len(self.coordinates)

    def __getitem__(self, key):
        return self.coordinates[key]
        
    def add_coordinate(self, coordinates: Coordinates):
        self.coordinates.append(coordinates)
    
    @classmethod
    def from_list(cls, coordinates_list: List[List[float]]) -> 'Route':
        coordinates = [Coordinates.from_list(coord) for coord in coordinates_list]
        return cls(coordinates)
        
    def to_folium_tuples(self):
        return [coord.to_tuple() for coord in self.coordinates]
        
    def fill_paths_between_points(self, mode="walking", provider="google"):
        """
        Fill the shortest paths between all successive points in a list.
        :param points: List of (latitude, longitude) tuples.
        :return: Concatenated list of all paths with consecutive duplicates removed and a mapping of original points to path segments.
        """
        full_path = Route()
        path_mapping = {}
    
        for i in range(len(self.coordinates) - 1):
            start = self.coordinates[i]
            end = self.coordinates[i+1]
            
            direction = Direction(start, end)
            if provider == "google":
                path_segment = direction.get_shortest_path_google_maps(mode)
            elif provider == "mapbox":
                path_segment = direction.get_mapbox_routes(mode)
    
            # Initialize path segment for mapping
            path_mapping[Direction.from_coordinates(start, end)] = []
    
            # Add the path segment to the full path, removing consecutive duplicates
            for point in path_segment:
                #if not full_path or full_path[-1] != point:
                full_path.add_coordinate(point)
                path_mapping[Direction.from_coordinates(start, end)].append(point)

        return full_path, path_mapping

    def filter_close_points(self, min_distance=15):
        filtered_segment = Route()
        for i in range(len(self.coordinates)):
            if i == 0 or great_circle(self.coordinates[i-1], self.coordinates[i]).meters >= min_distance:
                filtered_segment.add_coordinate(self.coordinates[i])
        return filtered_segment

    def get_nearest_bicycle_road_points(self, dist=1000):
        nearest_points= Parallel(n_jobs=-1)(delayed(coord.get_nearest_bicycle_road_point)(dist=dist) for coord in self.coordinates)
        print(nearest_points)
        return Route(coordinates = nearest_points)
