import folium
import matplotlib.pyplot as plt 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from adjustText import adjust_text

from stravart.directions import Route
from stravart.contours.contours import Contour

def plot_route(map_center, route: Route, contour = True, points = True):
    
    m = folium.Map(location=map_center, zoom_start=15)
    
    if points:
        for index, coord in enumerate(route):
            folium.Marker(location=coord.to_tuple(),popup=str(index), icon=folium.Icon(color="blue")).add_to(m)
    
    if contour:
        folium.PolyLine(route.to_folium_tuples(), color="blue", weight=2.5, opacity=1).add_to(m)
    
    return m

def plot_contour(contour):
    if isinstance(contour, Contour):
        x_coords, y_coords = contour.raw_contour[:, 0], contour.raw_contour[:, 1]
    elif isinstance(contour, np.ndarray):
        x_coords, y_coords = contour[:, 0], contour[:, 1]
    elif isinstance(contour, list) and all(len(point) == 2 for point in contour):
        x_coords, y_coords = zip(*contour)
    else:
        raise ValueError("Unsupported contour format. Must be an instance of Contour, a NumPy array, or a list of points.")
        
    plt.plot(x_coords, y_coords, marker='x')
    texts = []
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        texts.append(plt.text(x, y, str(i), fontsize=9, ha='right', va='bottom'))

    adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.axis('equal')
    plt.show()
    
def plot_contours(contour1, contour2):

    x_coords, y_coords = zip(*contour1)
    x2_coords, y2_coords = zip(*contour2)
    
    plt.figure(figsize=(5, 5))
    plt.plot(x_coords, y_coords, marker='x', label=str("first"))
    plt.plot(x2_coords, y2_coords, marker='o', label=str("second"))
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
