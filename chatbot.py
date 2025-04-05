import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium
from gtts import gTTS
import os
import uuid

# Title
st.set_page_config(page_title="Map Chatbot", layout="centered")
st.title("🗺️ Map Chatbot with Directions")

# Input fields
source = st.text_input("Enter Source Location", "Bhavani Bus Stand")
destination = st.text_input("Enter Destination Location", "Kaveri Bridge")

# Initialize client
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

# Function to get route and instructions
def get_directions(src, dest):
    geocode_src = client.pelias_search(text=src)
    geocode_dest = client.pelias_search(text=dest)

    coord_src = geocode_src['features'][0]['geometry']['coordinates']
    coord_dest = geocode_dest['features'][0]['geometry']['coordinates']

    coords = (coord_src, coord_dest)

    route = client.directions(coords)
    steps = route['routes'][0]['segments'][0]['steps']

    # Extract polyline
    geometry = route['routes'][0]['geometry']
    decoded = openrouteservice.convert.decode_polyline(geometry)

    return decoded['coordinates'], steps

# Function to speak directions
def speak_directions(steps):
    instructions = " ".join([step['instruction'] for step in steps])
    tts = gTTS(text=instructions, lang='en')
    filename = f"route_audio_{uuid.uuid4()}.mp3"
    tts.save(filename)
    st.audio(filename, format="audio/mp3")

# Button to get route
if st.button("Get Route"):
    try:
        coords, steps = get_directions(source, destination)

        # Display instructions
        st.subheader("Directions 🧭")
        for i, step in enumerate(steps):
            st.markdown(f"**{i+1}.** {step['instruction']}")

        # Display map
        m = folium.Map(location=coords[0][::-1], zoom_start=14)
        folium.PolyLine(coords, color="blue", weight=5).add_to(m)
        folium.Marker(coords[0][::-1], tooltip="Start").add_to(m)
        folium.Marker(coords[-1][::-1], tooltip="End").add_to(m)

        st_folium(m, width=700)

        # Play directions
        st.subheader("🔊 Voice Directions")
        speak_directions(steps)

    except Exception as e:
        st.error(f"Something went wrong: {e}")

