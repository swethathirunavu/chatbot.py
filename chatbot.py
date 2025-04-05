# get_your_path.py
import streamlit as st
import openrouteservice
from openrouteservice import convert
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

# App title
st.title("🗺️ Get Your Path")
st.markdown("""
Enter **starting** and **destination** places by name. This app will:
- Show the **best route** on a map
- Display **distance** and **duration**
- Provide **step-by-step directions**
""")

# Inputs
start_location = st.text_input("Enter Starting Place", placeholder="e.g., Chennai Central")
end_location = st.text_input("Enter Destination", placeholder="e.g., Ramapuram, Chennai")

if st.button("Find Route"):
    try:
        # Geocode location names
        geolocator = Nominatim(user_agent="get-your-path")
        start_coords = geolocator.geocode(start_location)
        end_coords = geolocator.geocode(end_location)

        if not start_coords or not end_coords:
            st.error("Could not find one or both locations. Please check spelling.")
        else:
            coords = ((start_coords.longitude, start_coords.latitude),
                      (end_coords.longitude, end_coords.latitude))

            # Call OpenRouteService API
            client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
            route = client.directions(coords)

            # Distance and Duration
            distance = round(route['routes'][0]['summary']['distance'] / 1000, 2)
            duration = round(route['routes'][0]['summary']['duration'] / 60, 2)
            st.success(f"Distance: {distance} km | Duration: {duration} minutes")

            # Route instructions
            steps = route['routes'][0]['segments'][0]['steps']
            st.subheader("Step-by-step Directions:")
            for step in steps:
                st.markdown(f"➡️ {step['instruction']}")

            # Draw route on map
            geometry = route['routes'][0]['geometry']
            decoded = convert.decode_polyline(geometry)

            m = folium.Map(location=[start_coords.latitude, start_coords.longitude], zoom_start=13)
            folium.Marker(
                [start_coords.latitude, start_coords.longitude], popup="Start", tooltip="Start", icon=folium.Icon(color='green')
            ).add_to(m)
            folium.Marker(
                [end_coords.latitude, end_coords.longitude], popup="End", tooltip="End", icon=folium.Icon(color='red')
            ).add_to(m)

            folium.PolyLine(locations=[(point[1], point[0]) for point in decoded['coordinates']], color="blue").add_to(m)
            st_folium(m, width=700, height=500)

    except Exception as e:
        st.error(f"Something went wrong: {e}")



