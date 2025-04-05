import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium
import pyttsx3
import speech_recognition as sr

st.set_page_config(page_title="Map Route Chatbot", layout="centered")
st.title("🗺️ Map Route Chatbot with Voice")

# Initialize ORS client with secret key
client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])

# Function to convert text to speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to listen from mic (optional for future use)
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        return query
    except sr.UnknownValueError:
        return "Sorry, could not understand."

# Get user input
start = st.text_input("Enter Starting Location", "Bhavani Bus Stand")
end = st.text_input("Enter Destination", "Kaveri Bridge")

if st.button("Get Route"):
    try:
        # Geocode start and end locations
        coords = [
            client.pelias_search(text=start)['features'][0]['geometry']['coordinates'],
            client.pelias_search(text=end)['features'][0]['geometry']['coordinates']
        ]

        # Get route
        route = client.directions(coords, profile='driving-car', format='geojson')

        # Create map centered at the start location
        m = folium.Map(location=coords[0][::-1], zoom_start=14)
        folium.Marker(location=coords[0][::-1], tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(location=coords[1][::-1], tooltip="End", icon=folium.Icon(color='red')).add_to(m)
        folium.GeoJson(route, name="Route").add_to(m)

        # Display map
        st_folium(m, width=700, height=500)

        # Get turn-by-turn directions
        directions = client.directions(coords, profile='driving-car')
        steps = directions['routes'][0]['segments'][0]['steps']

        route_text = ""
        for step in steps:
            route_text += f"{step['instruction']} ({step['distance']:.0f} meters)\n"

        st.subheader("Route Instructions:")
        st.text(route_text)

        # Speak the instructions
        speak(route_text)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
