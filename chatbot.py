import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import streamlit.components.v1 as components

st.set_page_config(page_title="Get Your Path", layout="wide")
st.title("🗺️ Get Your Path")

st.markdown("""
Enter starting and destination places by name. This app will:
- Show the best route on a map
- Display distance and duration
- Provide step-by-step directions
""")

if "route_info" not in st.session_state:
    st.session_state.route_info = None

start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")
end_place = st.text_input("Enter Destination", placeholder="e.g. Kaveri Bridge, Bhavani")

# JavaScript code to get the user's location
geolocation_script = """
<script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const coords = {lat: latitude, lon: longitude};
            window.parent.postMessage({coords: coords}, "*");
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
</script>
"""

# Display the JavaScript
components.html(geolocation_script, height=0)

def geocode_place(place_name):
    geolocator = Nominatim(user_agent="get-your-path-app")
    location = geolocator.geocode(place_name)
    return (location.latitude, location.longitude) if location else None

# Check if user location is received from JavaScript
def get_user_location():
    if "coords" in st.session_state:
        return st.session_state["coords"]
    return None, None

if st.button("Find Route"):
    # Check if user location is available
    user_lat, user_lon = get_user_location()
    
    if user_lat and user_lon:
        start_coords = (user_lat, user_lon)  # Use user location
        st.write(f"Your current location: Latitude = {user_lat}, Longitude = {user_lon}")
    else:
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


