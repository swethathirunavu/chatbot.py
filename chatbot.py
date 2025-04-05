import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium

# Get API key from Streamlit secrets
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

st.title("🗺️ Route Finder Chatbot")
st.write("Enter your starting and destination points:")

start = st.text_input("Start Location", "Bhavani Bus Stand")
end = st.text_input("Destination", "Kaveri Bridge")

if st.button("Show Route"):
    coords = client.pelias_search(text=start)['features'][0]['geometry']['coordinates'], \
             client.pelias_search(text=end)['features'][0]['geometry']['coordinates']
    route = client.directions(coords, profile='driving-car', format='geojson')

    m = folium.Map(location=[coords[0][1], coords[0][0]], zoom_start=14)
    folium.GeoJson(route, name="route").add_to(m)
    folium.Marker([coords[0][1], coords[0][0]], tooltip="Start").add_to(m)
    folium.Marker([coords[1][1], coords[1][0]], tooltip="End").add_to(m)

    st_folium(m, width=700, height=500)
