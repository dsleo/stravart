import streamlit as st
import requests
import folium
from streamlit_folium import folium_static


def geocode(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=AIzaSyAlFJy2mE0LKbLHJS7z4Kz9WgB2B76LtrA"
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "OK":
        result = data["results"][0]
        location = result["geometry"]["location"]
        return (location["lat"], location["lng"])
    else:
        return None

st.title("Geocoder")

user_input = st.text_input("Enter an address to geocode:")
if user_input:
    coords = geocode(user_input)
    if coords:
        lat, lng = coords
        m = folium.Map(location=[lat, lng], zoom_start=15)
        folium_static(m)
    else:
        st.warning("No locations seem to match the provided address. Please try again.")
else:
    st.info("Please enter an address to start.")
