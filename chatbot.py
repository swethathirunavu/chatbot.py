import streamlit as st
import openrouteservice
from streamlit_folium import st_folium
import folium
import requests
import cohere
import time
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Get Your Path", layout="wide")
st.title(" Get Your Path - AI Travel Assistant")

st.markdown("""
Type your starting and destination places. This app will:
- Show the best route on a map
- Display distance and duration
- Provide step-by-step directions
- Offer route alternatives (Fastest/Recommended/Shortest)
- Answer your travel queries like a smart assistant 🧠
""")

if "route_info" not in st.session_state:
    st.session_state.route_info = None

if "client" not in st.session_state:
    try:
        st.session_state.client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
    except Exception as e:
        st.error(f"OpenRouteService API key issue: {e}")

col1, col2 = st.columns(2)
with col1:
    start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")
with col2:
    end_place = st.text_input("Enter Destination Place", placeholder="e.g. Coimbatore Station")

route_preference = st.selectbox(
    "Select Route Preference",
    ("Fastest", "Recommended", "Shortest")
)

def geocode(place):
    geolocator = Nominatim(user_agent="get-your-path-app")
    try:
        location = geolocator.geocode(place)
        if location:
            return (location.latitude, location.longitude)
        return None
    except:
        return None

if st.button("Find Route"):
    start = geocode(start_place)
    end = geocode(end_place)

    if not start or not end:
        st.error("❌ Could not find one or both locations. Please check spelling.")
    else:
        with st.spinner("Fetching best routes for you..."):
            time.sleep(1)
            try:
                headers = {
                    'Authorization': st.secrets["ORS_API_KEY"],
                    'Content-Type': 'application/json'
                }

                data = {
                    "coordinates": [[start[1], start[0]], [end[1], end[0]]],
                    "instructions": True,
                    "format": "geojson"
                }

                if route_preference == "Shortest":
                    data["options"] = {"weighting": "shortest"}
                elif route_preference == "Fastest":
                    data["options"] = {"weighting": "fastest"}

                response = requests.post("https://api.openrouteservice.org/v2/directions/driving-car",
                                         json=data, headers=headers)
                route = response.json()

                if "features" not in route or not route["features"]:
                    st.error("No route found. Please try with different locations.")
                else:
                    st.session_state.route_info = {
                        "route": route,
                        "start_coords": start,
                        "end_coords": end
                    }

            except Exception as e:
                st.error(f"Error while fetching route:\n\n{e}\n\nResponse content:\n\n{response.text}")

if st.session_state.route_info:
    route = st.session_state.route_info["route"]
    start = st.session_state.route_info["start_coords"]
    end = st.session_state.route_info["end_coords"]

    try:
        distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000
        duration = route['features'][0]['properties']['segments'][0]['duration'] / 60

        st.success(f"**Distance:** {distance:.2f} km | **Estimated Time:** {duration:.1f} mins")

        st.subheader("📍 Step-by-step Directions:")
        steps = route['features'][0]['properties']['segments'][0]['steps']
        for i, step in enumerate(steps):
            instruction = step['instruction']
            if "left" in instruction.lower(): icon = "⬅️"
            elif "right" in instruction.lower(): icon = "➡️"
            elif "roundabout" in instruction.lower(): icon = "🔀"
            else: icon = "🛋"
            st.markdown(f"{i+1}. {icon} {instruction}")

        m = folium.Map(location=start, zoom_start=13)
        folium.Marker(start, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(end, tooltip="End", icon=folium.Icon(color='red')).add_to(m)
        folium.PolyLine(
            locations=[(c[1], c[0]) for c in route['features'][0]['geometry']['coordinates']],
            color='blue'
        ).add_to(m)

        st_folium(m, width=700, height=500)

    except Exception as e:
        st.error(f"Error displaying route: {e}")

st.divider()
st.subheader("🧠 Smart Travel Assistant")
user_query = st.text_input("Ask a travel-related question (e.g., 'suggest tourist places near Kodaikanal')")
if user_query:
    with st.spinner("Thinking..."):
        try:
            co = cohere.Client(st.secrets["COHERE_API_KEY"])
            response = co.chat(message=user_query, model="command-r", temperature=0.7)
            assistant_reply = response.text
            st.markdown(f"💬 **Assistant:** {assistant_reply}")

        except Exception as e:
            st.error(f"Error fetching assistant reply: {e}")
