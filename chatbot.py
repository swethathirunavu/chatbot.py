import streamlit as st
import openrouteservice
from openrouteservice import convert
from streamlit_folium import st_folium
import folium

# Title
st.title("🗺️ Smart Map Chatbot")
st.write("Enter your source and destination to get the route.")

# Input locations
source = st.text_input("From")
destination = st.text_input("To")

# Only run if both source and destination are entered
if source and destination:
    # Geocode to get coordinates using ORS geocoder
    try:
        client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

        src_coords = client.pelias_search(text=source)["features"][0]["geometry"]["coordinates"]
        dest_coords = client.pelias_search(text=destination)["features"][0]["geometry"]["coordinates"]

        coords = (tuple(src_coords), tuple(dest_coords))

        # Get the route
        route = client.directions(coords)
        geometry = route['routes'][0]['geometry']
        decoded = convert.decode_polyline(geometry)

        # Create the map
        m = folium.Map(location=[src_coords[1], src_coords[0]], zoom_start=10)
        folium.Marker(
            location=[src_coords[1], src_coords[0]],
            popup="Source",
            icon=folium.Icon(color="green")
        ).add_to(m)

        folium.Marker(
            location=[dest_coords[1], dest_coords[0]],
            popup="Destination",
            icon=folium.Icon(color="red")
        ).add_to(m)

        folium.PolyLine(
            locations=[(point[1], point[0]) for point in decoded['coordinates']],
            color="blue",
            weight=4,
        ).add_to(m)

        st.success("Route loaded successfully!")
        st_folium(m, width=700, height=500)

    except Exception as e:
        st.error(f"Error: {e}")
