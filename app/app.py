import streamlit as st
import folium
from streamlit_folium import folium_static

import optuna

from stravart.utils import simplify_coordinates
from stravart.polygone import Polygon
from stravart.search.optimization import generate_route, diff_area, Rotation, Projection

if 'study_running' not in st.session_state:
    st.session_state.study_running = False
if 'show_start_button' not in st.session_state:
    st.session_state['show_start_button'] = True
if 'study' not in st.session_state:
    st.session_state.study = optuna.create_study(direction='minimize')
if 'current_map_data' not in st.session_state:
    st.session_state.current_map_data = None
if 'current_trial_number' not in st.session_state:
    st.session_state.current_trial_number = 0
if 'best_loss' not in st.session_state:
    st.session_state.best_loss = float('inf')
if 'map_data' not in st.session_state:
    st.session_state.map_data = None
if 'best_map_data' not in st.session_state:
    st.session_state.best_map_data = None


def generate_fg(final_contour):
    fg = folium.FeatureGroup(name="kook")
    for index, coord in enumerate(final_contour):
        fg.add_child(
            folium.Marker(
            location=[coord.latitude, coord.longitude],
            popup=str(index),
            icon=folium.Icon(color="blue")
        ))
    polyline_coords = [[coord.latitude, coord.longitude] for coord in final_contour]
    fg.add_child(folium.PolyLine(polyline_coords, color="blue", weight=2.5, opacity=1))
    return fg

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

st.title("StravArt")
n_trials = st.sidebar.number_input('Number of Trials', min_value=3, max_value=50, value=3)
grid_size = st.sidebar.slider('City Grid Size', min_value=3, max_value=10, value=5)
placeholder = st.empty()

def reset_app():
    """Reset application state."""
    st.session_state['study_running'] = False
    st.session_state['show_start_button'] = True
    st.markdown("""<style>.css-18rr39v{visibility:hidden}</style><div class="block-container css-18rr39v"></div>""", unsafe_allow_html=True)

lat_start, lat_end = 48.8156, 48.9022
lon_start, lon_end = 2.2241, 2.4699
city_grid = generate_grid(lat_start, lat_end, lon_start, lon_end, grid_size, grid_size)

coordinates = [
    (-4, 7), (-3.5, 8), (-3, 9), (-2.5, 10), (-2, 10.5), (-1.5, 11), (-1, 11.5), (-0.5, 11.75), (0, 12),
    (0.5, 11.75), (1, 11.5), (1.5, 11), (2, 10.5), (2.5, 10), (3, 9), (3.5, 8), (4, 7),
    (3.5, 6), (3, 5), (2.5, 4), (2, 3), (1.5, 2), (1, 1), (0.5, 0), (0, -1),
    (-0.5, 0), (-1, 1), (-1.5, 2), (-2, 3), (-2.5, 4), (-3, 5), (-3.5, 6), (-4, 7),
    (-4.5, 6.5), (-5, 6), (-5.5, 5.5), (-6, 5), (-5.5, 4.5), (-5, 4), (-4.5, 3.5), (-4, 3),
    (-3.5, 3.5), (-3, 4), (-2.5, 4.5), (-2, 5), (-1.5, 5.5), (-1, 6), (-0.5, 6.5), (0, 7),
    (0.5, 6.5), (1, 6), (1.5, 5.5), (2, 5), (2.5, 4.5), (3, 4), (3.5, 3.5), (4, 3),
    (4.5, 3.5), (5, 4), (5.5, 4.5), (6, 5), (5.5, 5.5), (5, 6), (4.5, 6.5), (4, 7),
    (3.5, 7.5), (3, 8), (2.5, 8.5), (2, 9), (1.5, 9.5), (1, 10), (0.5, 10.5), (0, 11),
    (-0.5, 10.5), (-1, 10), (-1.5, 9.5), (-2, 9), (-2.5, 8.5), (-3, 8), (-3.5, 7.5), (-4, 7)
]

origin = simplify_coordinates(coordinates)
poly =  Polygon.from_list(coordinates_list=origin, system="cartesian")

def define_search_space(trial, city_grid):
    angle = trial.suggest_float('rot_angle', -20, 20, step=5)

    map_center_idx = trial.suggest_int('map_center_idx', 0, len(city_grid) - 1)
    map_center = city_grid[map_center_idx]
    radius = trial.suggest_float('radius', 0.01, 0.1, step= 0.005)

    return angle, map_center, radius

def objective(trial, poly=poly, city_grid=city_grid):
    angle, map_center, radius = define_search_space(trial,city_grid=city_grid)

    new_poly = Rotation(angle).apply(poly)
    projection = Projection(center=map_center, radius=radius, map_type="GPS")
    gps_poly = projection.apply(new_poly)
    final_contour, path_mapping = generate_route(gps_poly)
    loss = diff_area(final_contour, path_mapping)

    trial.set_user_attr('final_contour', final_contour)
    trial.set_user_attr('path_mapping', path_mapping)

    st.session_state.current_map_data = (map_center, final_contour)
    st.session_state.current_trial_number = trial.number

    return loss

with st.sidebar:
    if st.session_state.show_start_button:
        if st.button('Start Optuna Study', key='start_study_btn'):
            st.session_state.study_running = True
            st.session_state.show_start_button = False
            if st.button('Abort Study', key='abort_study_btn', disabled=False, on_click=reset_app):
                st.warning('Optuna Study Aborted')

    elif st.session_state.study_running:
        if st.button('Abort Study', key='abort_study_btn', disabled=False, on_click=reset_app):
            st.warning('Optuna Study Aborted')

if st.session_state.study_running:
    trial_status_placeholder = st.empty()
    best_loss_placeholder = st.empty()
    with st.spinner('Running Optuna Study...'):
        for i in range(n_trials):
            print(f'Doing {i} trials')
            trial_status_placeholder.write(f"Currently testing trial number: {i + 1}")
            trial = st.session_state.study.ask()
            loss = objective(trial, poly=poly, city_grid=city_grid)
            st.session_state.study.tell(trial, loss)

            if loss < st.session_state.best_loss:
                st.session_state.best_loss = loss
                best_loss_placeholder.write(f"Best loss so far: {round(loss, 3)}")
                map_center, final_contour = st.session_state.current_map_data
                m = folium.Map(location=map_center, zoom_start=14)
                fg = generate_fg(final_contour)
                fg.add_to(m)
                st.session_state.best_map_data = m 

                with placeholder.container():
                    import time
                    map_display_width = 700
                    map_display_height = 500
                    folium_static(st.session_state.best_map_data, width=map_display_width, height=map_display_height)
                    best_trial = st.session_state.study.best_trial
                    st.write("Best trial loss:", round(best_trial.value, 4))
                    st.write("Best trial params:", best_trial.params)
                    time.sleep(1)

        trial_status_placeholder.empty()
    st.session_state.study_running = False

else:
    st.sidebar.info("The study is currently stopped.")