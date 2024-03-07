# Strava Art

Ultimate goal is to design routes as the contour of an image.

## How to convert an image to a Route
Here is the recipe:

1. Extract the largest contour (list of coordinates) from an image
2. Project that contour on a map.
3. Get direction between successives points.

Have a look at the [Starter Notebook](https://github.com/dsleo/stravart/blob/main/notebooks/Starter%20Notebook.ipynb) for a first overview.

```python
from stravart.polygone import Polygon
from stravart.search.operations import Projection
from stravart.contours.extraction import ContourExtractor

contour_extractor = ContourExtractor("path/to/img")
contour = contour_extractor.get_best_contour()
contour.close()

map_center =  (48.8675, 2.3638)  
radius = 0.03

poly =  Polygon.from_list(coordinates_list=contour, system="cartesian")
projection = Projection(center=map_center, radius=radius, map_type="GPS")
gps_poly = projection.apply(poly)

final_contour, path_mapping = gps_poly.fill_paths_between_points()
plot_route(map_center=map_center, route=final_contour)
```

For natural image, check out the [Contour Extraction.ipynb](https://github.com/dsleo/stravart/blob/main/notebooks/Contour%20Extraction.ipynb) notebook.

## Find a better route

We can try to look for the best possible route by:
1. Applying multiple operations to the polygon (dilatation, rotation)
2. Measure each feasible route quality - as the total difference area between the image contour and the suggested polygon.
3. Select the best one according to the previous criterion.

Check out the [Optimization notebook](https://github.com/dsleo/stravart/blob/main/notebooks/Optuna%20Optimization.ipynb)

```python
import optuna
from stravart.search.optimization import generate_grid, objective

# Grid over Paris
lat_start, lat_end = 48.8156, 48.9022
lon_start, lon_end = 2.2241, 2.4699
city_grid = generate_grid(lat_start, lat_end, lon_start, lon_end, 5, 5)

study = optuna.create_study(direction='minimize')
study.optimize(lambda trial: objective(trial, poly=poly, city_grid=city_grid), n_trials=10)

best_trial = study.best_trial
best_final_contour = best_trial.user_attrs['final_contour']
map_center = city_grid[study.best_params['map_center_idx']]
```

## Installation

To install StravArt, follow these steps:

1. Clone the repository to your local machine

```bash
git clone https://github.com/yourusername/StravArt.git
cd StravArt
```

2. Create a virtual env

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies 
```bash
pip install -r requirements.txt
```

## TODO

- [ ] Write the route to gpx file.




