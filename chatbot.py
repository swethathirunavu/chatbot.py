import streamlit as st
import speech_recognition as sr
import pyttsx3
import openrouteservice
from streamlit_folium import st_folium
import folium

# Speak response
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Get voice input
def get_voice_input(prompt):
    st.info(prompt)
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except Exception as e:
        st.error("Sorry, could not understand.")
        return ""

# Map logic
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

def get_route(start, end):
    coords = client.pelias_autocomplete(start)["features"][0]["geometry"]["coordinates"]
    start_coords = coords[::-1]
    coords = client.pelias_autocomplete(end)["features"][0]["geometry"]["coordinates"]
    end_coords = coords[::-1]

    route = client.directions(
        coordinates=[start_coords[::-1], end_coords[::-1]],
        profile='driving-car',
        format='geojson'
    )

    m = folium.Map(location=start_coords, zoom_start=13)
    folium.Marker(start_coords, tooltip="Start").add_to(m)
    folium.Marker(end_coords, tooltip="End").add_to(m)
    folium.GeoJson(route, name="route").add_to(m)
    
    # Speak the first instruction
    steps = route['features'][0]['properties']['segments'][0]['steps']
    if steps:
        speak_text(steps[0]['instruction'])
    
    st_folium(m, width=700, height=500)

# Streamlit App UI
st.title("🗺️ Voice Map Chatbot")

if st.button("🎙️ Speak Starting Point"):
    start_location = get_voice_input("Say the starting location")
else:
    start_location = st.text_input("Enter Starting Location")

if st.button("🎙️ Speak Destination"):
    end_location = get_voice_input("Say the destination")
else:
    end_location = st.text_input("Enter Destination")

if st.button("Get Route"):
    if start_location and end_location:
        get_route(start_location, end_location)
