import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
from streamlit_javascript import st_javascript

st.set_page_config(page_title="Get Your Path", layout="wide")
st.title("🗘️ Get Your Path")

st.markdown("""
Enter starting and destination places by name. This app will:
- Show the best route on a map
- Display distance and duration
- Provide step-by-step directions
""")

if "route_info" not in st.session_state:
    st.session_state.route_info = None

# Get user location if requested
def get_user_location():
    loc = st_javascript("navigator.geolocation.getCurrentPosition((loc) => {window.parent.postMessage({latitude: loc.coords.latitude, longitude: loc.coords.longitude}, '*');})")
    return loc

# Reverse geocode coordinates to address
def reverse_geocode(coords):
    geolocator = Nominatim(user_agent="get-your-path-app")
    location = geolocator.reverse(coords, exactly_one=True)
    return location.address if location else "Unknown location"

# Geocode place name to coordinates
def geocode_place(place_name):
    geolocator = Nominatim(user_agent="get-your-path-app")
    location = geolocator.geocode(place_name)
    return (location.latitude, location.longitude) if location else None

use_current = st.checkbox("Use my current location as starting point")

if use_current:
    st.info("Detecting your location...")
    user_loc = get_user_location()
    if user_loc and "latitude" in user_loc:
        start_coords = (user_loc["latitude"], user_loc["longitude"])
        reverse_start = reverse_geocode(start_coords)
        st.success(f"Detected: {reverse_start}")
        start_place = reverse_start
    else:
        st.warning("Could not detect location.")
        start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")
else:
    start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")

end_place = st.text_input("Enter Destination", placeholder="e.g. Kaveri Bridge, Bhavani")

if st.button("Find Route"):
    start_coords = geocode_place(start_place)
    end_coords = geocode_place(end_place)

    if not start_coords or not end_coords:
        st.error("❌ Could not find one or both locations. Please check spelling.")
    else:
        try:
            client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
            route = client.directions(
                coordinates=[start_coords[::-1], end_coords[::-1]],
                profile='driving-car',
                format='geojson'
            )

            st.session_state.route_info = {
                "route": route,
                "start_coords": start_coords,
                "end_coords": end_coords
            }

        except Exception as e:
            st.error(f"Something went wrong: {e}")

# Display route info if available
if st.session_state.route_info:
    route = st.session_state.route_info["route"]
    start_coords = st.session_state.route_info["start_coords"]
    end_coords = st.session_state.route_info["end_coords"]

    distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000
    duration = route['features'][0]['properties']['segments'][0]['duration'] / 60

    st.success(f"**Distance:** {distance:.2f} km | **Estimated Time:** {duration:.1f} mins")

    st.subheader("📍 Step-by-step Directions:")
    steps = route['features'][0]['properties']['segments'][0]['steps']
    for i, step in enumerate(steps):
        st.markdown(f"{i+1}. {step['instruction']}")

    m = folium.Map(location=start_coords, zoom_start=13)
    folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine(
        locations=[(c[1], c[0]) for c in route['features'][0]['geometry']['coordinates']],
        color='blue'
    ).add_to(m)

    st_folium(m, width=700, height=500)






