import streamlit as st
from streamlit_folium import st_folium
import openrouteservice
from folium import Map, Marker, PolyLine

# Set page config
st.set_page_config(page_title="Map Chatbot", layout="wide")
st.title("🗺️ Map Route Chatbot")

# Initialize OpenRouteService client
try:
    client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
except Exception as e:
    st.error("❌ Could not load OpenRouteService API Key. Please set it in Streamlit secrets.")
    st.stop()

# Input fields
start_location = st.text_input("Enter Starting Location:", "Bhavani Bus Stand")
end_location = st.text_input("Enter Destination:", "Kaveri Bridge")

# Button to get directions
if st.button("Get Route"):
    try:
        # Geocoding locations to coordinates
        coords_start = client.pelias_search(text=start_location)['features'][0]['geometry']['coordinates']
        coords_end = client.pelias_search(text=end_location)['features'][0]['geometry']['coordinates']

        # Check distance manually
        import geopy.distance
        dist_km = geopy.distance.geodesic(coords_start[::-1], coords_end[::-1]).km

        if dist_km > 6000:
            st.error("❌ Route too long! Please choose locations within 6000 km range.")
            st.stop()

        # Get directions
        route = client.directions(
            coordinates=[coords_start, coords_end],
            profile='driving-car',
            format='geojson'
        )

        # Show map with route
        m = Map(location=coords_start[::-1], zoom_start=13)
        Marker(coords_start[::-1], tooltip="Start").add_to(m)
        Marker(coords_end[::-1], tooltip="End").add_to(m)
        PolyLine(locations=[(coord[1], coord[0]) for coord in route['features'][0]['geometry']['coordinates']],
                 color="blue", weight=5).add_to(m)
        st_folium(m, width=700, height=500)

        # Show step-by-step directions
        steps = route['features'][0]['properties']['segments'][0]['steps']
        st.subheader("📍 Directions:")
        for i, step in enumerate(steps):
            st.markdown(f"{i+1}. {step['instruction']}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
