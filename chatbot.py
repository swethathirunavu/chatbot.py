import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Map Chatbot", layout="wide")
st.title("🗺️ Map Chatbot with Route Directions")

# Get OpenRouteService API key from Streamlit Secrets
ORS_API_KEY = st.secrets["ORS_API_KEY"]
client = openrouteservice.Client(key=ORS_API_KEY)

# Initialize geolocator
geolocator = Nominatim(user_agent="map_chatbot")

def geocode_location(place_name):
    location = geolocator.geocode(place_name)
    if location:
        return (location.longitude, location.latitude)
    else:
        return None

# Input from user
start_location = st.text_input("Enter Start Location", "Bhavani Bus Stand")
end_location = st.text_input("Enter Destination", "Kaveri Bridge")

if st.button("Get Route"):
    start_coords = geocode_location(start_location)
    end_coords = geocode_location(end_location)

    if not start_coords or not end_coords:
        st.error("Could not geocode one or both locations.")
    else:
        try:
            route = client.directions(
                coordinates=[start_coords, end_coords],
                profile='driving-car',
                format='geojson'
            )

            # Create the map
            m = folium.Map(location=[start_coords[1], start_coords[0]], zoom_start=13)
            folium.GeoJson(route, name="route").add_to(m)
            folium.Marker(
                location=[start_coords[1], start_coords[0]],
                popup="Start: " + start_location,
                icon=folium.Icon(color='green')
            ).add_to(m)
            folium.Marker(
                location=[end_coords[1], end_coords[0]],
                popup="End: " + end_location,
                icon=folium.Icon(color='red')
            ).add_to(m)

            st_folium(m, width=700, height=500)

            # Display instructions
            instructions = route['features'][0]['properties']['segments'][0]['steps']
            st.subheader("📝 Route Instructions:")
            for step in instructions:
                st.markdown(f"- {step['instruction']}")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
