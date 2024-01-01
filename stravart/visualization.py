import folium
import matplotlib.pyplot as plt 
from sklearn.preprocessing import MinMaxScaler

from .directions import *

def plot_route(map_center, route: Route, contour = True, points = True):
    
    m = folium.Map(location=map_center, zoom_start=15)
    
    if points:
        for index, coord in enumerate(route):
            folium.Marker(location=coord.to_tuple(),popup=str(index), icon=folium.Icon(color="blue")).add_to(m)
    
    if contour:
        folium.PolyLine(route.to_folium_tuples(), color="blue", weight=2.5, opacity=1).add_to(m)
    
    return m

def plot_contours(contour1, contour2):

    x_coords, y_coords = zip(*contour1)
    x2_coords, y2_coords = zip(*contour2)
    
    # Plotting
    plt.figure(figsize=(5, 5))
    plt.plot(y_coords, x_coords, marker='x', label=str("first"))
    plt.plot(y2_coords, x2_coords, marker='o', label=str("second"))
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.axis('equal')
    plt.legend()
    plt.show()

def plot_compare_polygons(poly1, poly2):

    scaler = MinMaxScaler()
    norm1 = scaler.fit_transform(poly1.to_folium_tuples())
    norm2 = scaler.transform(poly2.to_folium_tuples())

    return plot_contours(norm1, norm2)
