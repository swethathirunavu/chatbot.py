import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium

st.title("🗺️ Smart Route Finder")

# Set default coordinates
origin = (11.4435, 77.6834)  # Bhavani
destination = (13.0827, 80.2707)  # Chennai

# Initialize ORS client
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

# Get route
try:
    coords = (origin, destination)
    route = client.directions(coords)
    geometry = route['routes'][0]['geometry']
    decoded = openrouteservice.convert.decode_polyline(geometry)
    distance = round(route['routes'][0]['summary']['distance'] / 1000, 2)
    duration = round(route['routes'][0]['summary']['duration'] / 60, 2)

    st.success(f"📏 Distance: {distance} km | ⏱️ Duration: {duration} mins")

    # Directions text
    steps = route['routes'][0]['segments'][0]['steps']
    st.subheader("🧭 Directions:")
    for i, step in enumerate(steps):
        st.write(f"{i+1}. {step['instruction']}")

    # Show on map
    m = folium.Map(location=origin, zoom_start=7)
    folium.Marker(location=origin, tooltip="Start").add_to(m)
    folium.Marker(location=destination, tooltip="End").add_to(m)
    folium.PolyLine(locations=[(point[1], point[0]) for point in decoded['coordinates']], color="blue").add_to(m)
    st_folium(m, width=700, height=500)

except Exception as e:
    st.error(f"Something went wrong: {e}")

