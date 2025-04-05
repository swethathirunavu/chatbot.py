import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium
from gtts import gTTS
import os
import tempfile

# Set page config
st.set_page_config(page_title="Map Chatbot", layout="centered")
st.title("🗺️ Map Chatbot")

# Initialize client with API key
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

# Input form
with st.form("route_form"):
    start = st.text_input("Enter starting location:", "Bhavani Bus Stand")
    end = st.text_input("Enter destination:", "Kaveri Bridge")
    submitted = st.form_submit_button("Get Route")

if submitted:
    try:
        # Geocode locations
        start_coords = client.pelias_search(text=start)['features'][0]['geometry']['coordinates']
        end_coords = client.pelias_search(text=end)['features'][0]['geometry']['coordinates']

        # Get route
        route = client.directions(
            coordinates=[start_coords, end_coords],
            profile='foot-walking',
            format='geojson'
        )

        # Create map
        m = folium.Map(location=[(start_coords[1]+end_coords[1])/2, (start_coords[0]+end_coords[0])/2], zoom_start=14)
        folium.GeoJson(route, name="Route").add_to(m)
        folium.Marker(location=[start_coords[1], start_coords[0]], popup="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(location=[end_coords[1], end_coords[0]], popup="End", icon=folium.Icon(color='red')).add_to(m)

        # Display map
        st_folium(m, width=700, height=500)

        # Extract and display directions
        steps = route['features'][0]['properties']['segments'][0]['steps']
        instructions = "\n".join([step['instruction'] for step in steps])
        st.markdown("### 🧭 Route Instructions")
        st.text(instructions)

        # Convert instructions to speech
        tts = gTTS(text=instructions, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            audio_file = tmp.name
        st.audio(audio_file, format='audio/mp3')

    except Exception as e:
        st.error(f"Something went wrong: {e}")
