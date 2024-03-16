from stravart.search.operations import Projection, Rotation
from stravart.search.metrics import diff_area


def generate_route(gps_poly):
    final_contour, path_mapping = gps_poly.fill_paths_between_points()
    return final_contour, path_mapping
    
def test_operation(operation, map_center, radius, poly):
    new_poly = operation.apply(poly)
    projection = Projection(center=map_center, radius=radius, map_type="GPS")
    gps_poly = projection.apply(new_poly)

    # Get Route + Metric
    final_contour, path_mapping = generate_route(gps_poly)
    return diff_area(final_contour, path_mapping)
    
def generate_grid(lat_start, lat_end, lon_start, lon_end, lat_points, lon_points):
    lat_step = (lat_end - lat_start) / (lat_points - 1)
    lon_step = (lon_end - lon_start) / (lon_points - 1)

    grid = []
    for i in range(lat_points):
        for j in range(lon_points):
            lat = lat_start + i * lat_step
            lon = lon_start + j * lon_step
            grid.append((lat, lon))
    
    return grid

def define_search_space(trial, city_grid):
    angle = trial.suggest_float('rot_angle', -10, 10, step=5)

    # Randomly select a map center from city_grid
    map_center_idx = trial.suggest_int('map_center_idx', 0, len(city_grid) - 1)
    map_center = city_grid[map_center_idx]

    # Use discrete increments for radius
    radius = trial.suggest_float('radius', 0.01, 0.1, step= 0.005)

    return angle, map_center, radius

def objective(trial, poly, city_grid):
    angle, map_center, radius = define_search_space(trial,city_grid=city_grid)

    # Apply the operation and projection
    new_poly = Rotation(angle).apply(poly)
    projection = Projection(center=map_center, radius=radius, map_type="GPS")
    gps_poly = projection.apply(new_poly)

    # Generate route and calculate loss
    final_contour, path_mapping = generate_route(gps_poly)
    loss = diff_area(final_contour, path_mapping)

    trial.set_user_attr('final_contour', final_contour)
    trial.set_user_attr('path_mapping', path_mapping)

    return loss