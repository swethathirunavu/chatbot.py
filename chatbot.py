import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

st.title("🗺️ Get Your Path")

start_place = st.text_input("Enter Starting Place")
end_place = st.text_input("Enter Destination")

geolocator = Nominatim(user_agent="get_your_path_app")

def get_coordinates(place):
    try:
        location = geolocator.geocode(place)
        return (location.latitude, location.longitude)
    except:
        return None

if start_place and end_place:
    start_coords = get_coordinates(start_place)
    end_coords = get_coordinates(end_place)

    if start_coords and end_coords:
        try:
            client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
            coords = (start_coords, end_coords)

            route = client.directions(coords, optimize_waypoints=True)  # 🚨 Added optimize_waypoints

            geometry = route['routes'][0]['geometry']
            decoded = openrouteservice.convert.decode_polyline(geometry)

            m = folium.Map(location=start_coords, zoom_start=13)
            folium.Marker(start_coords, tooltip="Start").add_to(m)
            folium.Marker(end_coords, tooltip="End").add_to(m)
            folium.PolyLine(locations=decoded['coordinates'], color="blue", weight=5).add_to(m)

            st_folium(m, width=700, height=500)

            distance_km = route['routes'][0]['summary']['distance'] / 1000
            duration_min = route['routes'][0]['summary']['duration'] / 60
            st.success(f"🛣️ Distance: {distance_km:.2f} km")
            st.info(f"⏱️ Duration: {duration_min:.2f} minutes")

            st.subheader("📍 Directions:")
            for step in route['routes'][0]['segments'][0]['steps']:
                st.write(f"➡️ {step['instruction']}")

        except Exception as e:
            st.error("Could not generate a route. Try nearby city names or major roads.")
            st.exception(e)
    else:
        st.warning("Could not find one or both locations. Please check spelling.")

