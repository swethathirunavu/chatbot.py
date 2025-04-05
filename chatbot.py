import streamlit as st
from streamlit_folium import st_folium
import openrouteservice
from openrouteservice import convert
from geopy.geocoders import Nominatim
import folium

st.set_page_config(page_title="Get Your Path", layout="wide")

st.title("🗺️ Get Your Path")
st.markdown("Find the best route between two places!")

# Input locations
start_loc = st.text_input("Enter Starting Place", placeholder="e.g., Bhavani")
end_loc = st.text_input("Enter Destination", placeholder="e.g., Chennai")

# Get coordinates
geolocator = Nominatim(user_agent="get-your-path")
def get_coordinates(place):
    try:
        return geolocator.geocode(place)
    except:
        return None

if start_loc and end_loc:
    start = get_coordinates(start_loc)
    end = get_coordinates(end_loc)

    if start and end:
        coords = ((start.longitude, start.latitude), (end.longitude, end.latitude))

        # Connect to OpenRouteService
        try:
            client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
            route = client.directions(coords)

            geometry = route['routes'][0]['geometry']
            decoded = convert.decode_polyline(geometry)
            distance_km = route['routes'][0]['summary']['distance'] / 1000
            duration_min = route['routes'][0]['summary']['duration'] / 60

            # Show route map
            m = folium.Map(location=[(start.latitude + end.latitude)/2, (start.longitude + end.longitude)/2], zoom_start=7)
            folium.Marker([start.latitude, start.longitude], tooltip="Start", popup=start_loc).add_to(m)
            folium.Marker([end.latitude, end.longitude], tooltip="End", popup=end_loc).add_to(m)
            folium.PolyLine(locations=[(point[1], point[0]) for point in decoded['coordinates']], color='blue').add_to(m)

            st_folium(m, width=700, height=500)

            # Show distance and duration
            st.success(f"📏 Distance: {distance_km:.2f} km")
            st.success(f"⏱️ Duration: {duration_min:.2f} minutes")

            # Step-by-step instructions
            st.subheader("🧭 Directions:")
            steps = route['routes'][0]['segments'][0]['steps']
            for i, step in enumerate(steps, start=1):
                st.markdown(f"**{i}.** {step['instruction']}")

        except Exception as e:
            st.error(f"Something went wrong: {e}")

    else:
        st.warning("Could not find one or both locations. Please check spelling.")
