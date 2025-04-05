import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Get Your Path", layout="wide")

st.title("🗺️ Get Your Path")
st.markdown("""
Enter starting and destination places by name. This app will:
- Show the best route on a map
- Display distance and duration
- Provide step-by-step directions
""")

start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")
end_place = st.text_input("Enter Destination", placeholder="e.g. Kaveri Bridge, Bhavani")

def geocode_place(place_name):
    geolocator = Nominatim(user_agent="get-your-path-app")
    location = geolocator.geocode(place_name)
    return (location.latitude, location.longitude) if location else None

if st.button("Find Route"):
    try:
        start_coords = geocode_place(start_place)
        end_coords = geocode_place(end_place)

        if not start_coords or not end_coords:
            st.error("❌ Could not find one or both locations. Please check spelling.")
        else:
            client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
            route = client.directions(
                coordinates=[start_coords[::-1], end_coords[::-1]],
                profile='driving-car',
                format='geojson'
            )

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

    except Exception as e:
        st.error(f"Something went wrong: {e}")




