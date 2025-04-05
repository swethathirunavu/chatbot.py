# get_your_path.py

import streamlit as st
from streamlit_folium import st_folium
import openrouteservice
from openrouteservice import convert
from geopy.geocoders import Nominatim
import folium

# Title
st.title("🚀 Get Your Path")
st.markdown("Find the best route between two places with map, directions, distance, and time.")

# Input fields
start = st.text_input("Enter Starting Place")
end = st.text_input("Enter Destination")

if st.button("Show Route"):
    try:
        # Geocoding using geopy
        geolocator = Nominatim(user_agent="get-your-path")
        loc1 = geolocator.geocode(start)
        loc2 = geolocator.geocode(end)

        if not loc1 or not loc2:
            st.error("Could not find one or both locations. Please check spelling.")
        else:
            coords = ((loc1.longitude, loc1.latitude), (loc2.longitude, loc2.latitude))

            # OpenRouteService Client
            client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
            res = client.directions(coords)

            geometry = res['routes'][0]['geometry']
            decoded = convert.decode_polyline(geometry)
            distance = round(res['routes'][0]['summary']['distance'] / 1000, 2)  # in km
            duration = round(res['routes'][0]['summary']['duration'] / 60, 2)  # in mins

            # Create map
            m = folium.Map(location=[loc1.latitude, loc1.longitude], zoom_start=13)
            folium.Marker([loc1.latitude, loc1.longitude], tooltip="Start", popup=start).add_to(m)
            folium.Marker([loc2.latitude, loc2.longitude], tooltip="End", popup=end).add_to(m)
            folium.PolyLine(locations=[[coord[1], coord[0]] for coord in decoded['coordinates']], color="blue").add_to(m)

            # Display map and results
            st_folium(m, width=700, height=500)
            st.success(f"Distance: {distance} km | Duration: {duration} mins")
            st.markdown("### Step-by-step Directions:")
            steps = res['routes'][0]['segments'][0]['steps']
            for step in steps:
                st.write(f"➡️ {step['instruction']}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")


