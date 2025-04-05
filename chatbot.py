import streamlit as st
import openrouteservice
from openrouteservice import convert
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

# App Title
st.set_page_config(page_title="Get Your Path", layout="centered")
st.title("🗺️ Get Your Path")
st.markdown("Find the best route between two places!")

# Initialize API client
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
geolocator = Nominatim(user_agent="get-your-path")

# Input fields
start_location = st.text_input("Enter Starting Place", placeholder="e.g. Ramapuram, Chennai")
end_location = st.text_input("Enter Destination", placeholder="e.g. Marina Beach, Chennai")

if st.button("Get Route"):
    try:
        # Geocode start and end
        start = geolocator.geocode(start_location)
        end = geolocator.geocode(end_location)

        if not start or not end:
            st.error("❌ Could not find one or both locations. Please check spelling.")
        else:
            coords = [(start.longitude, start.latitude), (end.longitude, end.latitude)]

            # Get directions
            route = client.directions(coords)
            geometry = route["routes"][0]["geometry"]
            decoded = convert.decode_polyline(geometry)

            distance = route["routes"][0]["summary"]["distance"] / 1000  # in km
            duration = route["routes"][0]["summary"]["duration"] / 60  # in mins

            st.success(f"🛣️ Distance: {distance:.2f} km | 🕒 Duration: {duration:.2f} mins")

            # Step-by-step directions
            st.subheader("📍 Step-by-Step Directions")
            for step in route["routes"][0]["segments"][0]["steps"]:
                st.markdown(f"- {step['instruction']}")

            # Show map
            m = folium.Map(location=[start.latitude, start.longitude], zoom_start=13)
            folium.Marker([start.latitude, start.longitude], tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
            folium.Marker([end.latitude, end.longitude], tooltip="End", icon=folium.Icon(color='red')).add_to(m)

            folium.PolyLine(
                locations=[(coord[1], coord[0]) for coord in decoded["coordinates"]],
                color="blue",
                weight=5
            ).add_to(m)

            st_folium(m, width=700, height=500)

    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")
