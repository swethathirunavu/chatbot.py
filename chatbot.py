import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Map Chatbot", layout="wide")

st.title("🗺️ Map Chatbot - Route Finder")
st.markdown("Get directions between two places using OpenRouteService!")

# Input fields for the user
start = st.text_input("Enter **starting location**", "Bhavani Bus Stand")
end = st.text_input("Enter **destination**", "Kaveri Bridge")

# If user clicks the button
if st.button("Get Route"):
    with st.spinner("Finding the route..."):
        try:
            # 🔐 Use your ORS API key securely from Streamlit Secrets
            client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

            # Geocode the input locations
            geocode_start = client.pelias_search(text=start)
            geocode_end = client.pelias_search(text=end)

            # Check if locations are found
            if not geocode_start['features'] or not geocode_end['features']:
                st.error("Could not find one of the locations. Please check the names.")
            else:
                coords = [
                    geocode_start['features'][0]['geometry']['coordinates'],
                    geocode_end['features'][0]['geometry']['coordinates']
                ]

                # Get route directions
                route = client.directions(coords)

                # Display map
                m = folium.Map(location=[coords[0][1], coords[0][0]], zoom_start=14)
                folium.Marker(
                    location=[coords[0][1], coords[0][0]],
                    tooltip="Start",
                    icon=folium.Icon(color="green")
                ).add_to(m)
                folium.Marker(
                    location=[coords[1][1], coords[1][0]],
                    tooltip="End",
                    icon=folium.Icon(color="red")
                ).add_to(m)

                folium.PolyLine(
                    locations=[(pt[1], pt[0]) for pt in route['routes'][0]['geometry']['coordinates']],
                    color="blue",
                    weight=5
                ).add_to(m)

                st_folium(m, width=700, height=500)

        except Exception as e:
            st.error(f"Something went wrong: {e}")



