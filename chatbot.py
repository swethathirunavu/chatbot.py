import streamlit as st
import openrouteservice
from openrouteservice import convert
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Smart Route Finder", layout="centered")
st.title("🗺️ Smart Route Finder with Suggestions")

# Initialize ORS client
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

# Location input from user
col1, col2 = st.columns(2)
with col1:
    start = st.text_input("Enter Starting Location", placeholder="Eg: Bhavani")
with col2:
    end = st.text_input("Enter Destination", placeholder="Eg: Chennai")

# Submit button
if st.button("Get Route") and start and end:
    try:
        # Geocode input locations
        geocode_start = client.pelias_search(text=start)["features"][0]["geometry"]["coordinates"]
        geocode_end = client.pelias_search(text=end)["features"][0]["geometry"]["coordinates"]

        coords = (geocode_start, geocode_end)

        # Request route with alternate routes enabled
        route = client.directions(
            coordinates=coords,
            profile='driving-car',
            format='geojson',
            optimize_waypoints=True,
            instructions=True,
            alternative_routes={'share_factor': 0.6, 'target_count': 3}
        )

        # Display map with route
        m = folium.Map(location=[(geocode_start[1] + geocode_end[1]) / 2,
                                 (geocode_start[0] + geocode_end[0]) / 2], zoom_start=7)

        folium.Marker(location=[geocode_start[1], geocode_start[0]], tooltip="Start").add_to(m)
        folium.Marker(location=[geocode_end[1], geocode_end[0]], tooltip="End").add_to(m)

        folium.GeoJson(route, name="Route").add_to(m)

        st_folium(m, width=700, height=500)

        # Show route instructions, distance & time
        st.subheader("🧾 Directions")
        steps = route['features'][0]['properties']['segments'][0]['steps']
        total_distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # in km
        total_duration = route['features'][0]['properties']['segments'][0]['duration'] / 60  # in min

        st.markdown(f"**Total Distance:** {total_distance:.2f} km")
        st.markdown(f"**Estimated Time:** {total_duration:.2f} minutes")

        for i, step in enumerate(steps):
            st.markdown(f"{i+1}. {step['instruction']}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")

# Footer
st.markdown("---")
st.caption("🚀 Built with ❤️ by Swetha and Margaux")
