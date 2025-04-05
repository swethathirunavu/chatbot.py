import streamlit as st
from streamlit_folium import st_folium
import openrouteservice
from openrouteservice import convert
from folium import Map, Marker, PolyLine
from geopy.geocoders import Nominatim

# Set page config
st.set_page_config(page_title="Get Your Path", layout="centered")
st.title("🗺️ Get Your Path")
st.markdown("Find the best route between two places!")

# Get input from user
start_place = st.text_input("Enter Starting Place")
end_place = st.text_input("Enter Destination")

# Initialize geolocator
geolocator = Nominatim(user_agent="get_your_path")

# When user clicks the button
if st.button("Find Route"):
    if not start_place or not end_place:
        st.error("Please enter both starting and destination locations.")
    else:
        try:
            # Geocode addresses
            start_location = geolocator.geocode(start_place)
            end_location = geolocator.geocode(end_place)

            if start_location and end_location:
                start_coords = [start_location.longitude, start_location.latitude]
                end_coords = [end_location.longitude, end_location.latitude]

                # Get route
                client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
                route = client.directions(
                    coordinates=[start_coords, end_coords],
                    profile='driving-car',
                    format='geojson',
                    optimize_waypoints=True
                )

                # Extract distance and duration
                distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # in km
                duration = route['features'][0]['properties']['segments'][0]['duration'] / 60  # in mins

                st.success(f"Distance: {distance:.2f} km")
                st.success(f"Estimated Duration: {duration:.2f} minutes")

                # Get turn-by-turn steps
                steps = route['features'][0]['properties']['segments'][0]['steps']
                st.markdown("### 🧭 Directions:")
                for i, step in enumerate(steps):
                    st.write(f"{i+1}. {step['instruction']}")

                # Draw map
                midpoint = [(start_coords[1] + end_coords[1]) / 2, (start_coords[0] + end_coords[0]) / 2]
                m = Map(location=midpoint, zoom_start=12)
                Marker(location=[start_coords[1], start_coords[0]], tooltip="Start").add_to(m)
                Marker(location=[end_coords[1], end_coords[0]], tooltip="End").add_to(m)

                geometry = route['features'][0]['geometry']
                decoded = convert.decode_polyline(geometry)
                coords = [(point[1], point[0]) for point in decoded['coordinates']]
                PolyLine(coords, color="blue", weight=5, opacity=0.7).add_to(m)

                st_folium(m, width=700, height=500)

            else:
                st.error("Could not find one or both locations. Please check spelling.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

