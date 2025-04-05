import streamlit as st
import openrouteservice
from openrouteservice import convert
from streamlit_folium import st_folium
import folium

# Title
st.title("🗺️ Smart Map Chatbot")
st.write("Enter your source and destination to get the route.")

# Input
source = st.text_input("From")
destination = st.text_input("To")

if source and destination:
    try:
        # ORS client
        client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

        # Geocode to get coordinates
        src_coords = client.pelias_search(text=source)["features"][0]["geometry"]["coordinates"]
        dest_coords = client.pelias_search(text=destination)["features"][0]["geometry"]["coordinates"]
        coords = (tuple(src_coords), tuple(dest_coords))

        # Get route
        route = client.directions(coords, instructions=True)
        geometry = route['routes'][0]['geometry']
        decoded = convert.decode_polyline(geometry)

        # Draw Map
        m = folium.Map(location=[src_coords[1], src_coords[0]], zoom_start=12)
        folium.Marker([src_coords[1], src_coords[0]], popup="Source", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker([dest_coords[1], dest_coords[0]], popup="Destination", icon=folium.Icon(color="red")).add_to(m)
        folium.PolyLine([(point[1], point[0]) for point in decoded['coordinates']],
                        color="blue", weight=4).add_to(m)

        st_folium(m, width=700, height=500)

        # Show step-by-step directions
        st.subheader("🧭 Directions:")
        steps = route['routes'][0]['segments'][0]['steps']
        for i, step in enumerate(steps):
            st.markdown(f"**{i+1}.** {step['instruction']}")

    except Exception as e:
        st.error(f"Error: {e}")
