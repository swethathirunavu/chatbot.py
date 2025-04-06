import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Get Your Path", layout="wide")
st.title("🗌️ Get Your Path - AI Travel Assistant")

st.markdown("""
Speak or type your starting and destination places. This app will:
- Show the best route on a map
- Display distance and duration
- Provide step-by-step directions
- Offer route alternatives (Fastest/Recommended)
- Answer your travel queries like a smart assistant 🧠
- Detect traffic along the route 🚦
""")

if "route_info" not in st.session_state:
    st.session_state.route_info = None

if "client" not in st.session_state:
    try:
        st.session_state.client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
    except Exception as e:
        st.error(f"OpenRouteService API key issue: {e}")

# Text input
start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")
end_place = st.text_input("Enter Destination", placeholder="e.g. Kaveri Bridge, Bhavani")

# Route preference
route_preference = st.selectbox(
    "Select Route Preference",
    ("Fastest", "Recommended", "Shortest")
)

def geocode_place(place_name):
    if "," in place_name:
        try:
            lat, lon = map(float, place_name.split(","))
            return (lat, lon)
        except:
            return None
    geolocator = Nominatim(user_agent="get-your-path-app")
    location = geolocator.geocode(place_name)
    return (location.latitude, location.longitude) if location else None

if st.button("Find Route"):
    start_coords = geocode_place(start_place)
    end_coords = geocode_place(end_place)

    if not start_coords or not end_coords:
        st.error("❌ Could not find one or both locations. Please check spelling.")
    else:
        try:
            profile = 'driving-car'
            headers = {
                'Authorization': st.secrets["ORS_API_KEY"],
                'Content-Type': 'application/json'
            }

            data = {
                "coordinates": [list(start_coords[::-1]), list(end_coords[::-1])],
                "instructions": True,
                "format": "geojson",
                "alternative_routes": {"share_factor": 0.5, "target_count": 2},
                "options": {"traffic": True}
            }

            if route_preference == "Shortest":
                data["options"].update({"weighting": "shortest"})
            elif route_preference == "Fastest":
                data["options"].update({"weighting": "fastest"})

            response = requests.post("https://api.openrouteservice.org/v2/directions/driving-car",
                                     json=data, headers=headers)
            route = response.json()

            st.session_state.route_info = {
                "route": route,
                "start_coords": start_coords,
                "end_coords": end_coords
            }

        except Exception as e:
            st.error(f"Something went wrong while fetching route: {e}")

if st.session_state.route_info:
    route = st.session_state.route_info["route"]
    start_coords = st.session_state.route_info["start_coords"]
    end_coords = st.session_state.route_info["end_coords"]

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
            elif "roundabout" in instruction.lower(): icon = "🔄"
            else: icon = "🧽"
            st.markdown(f"{i+1}. {icon} {instruction}")

        m = folium.Map(location=start_coords, zoom_start=13)
        folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color='red')).add_to(m)
        folium.PolyLine(
            locations=[(c[1], c[0]) for c in route['features'][0]['geometry']['coordinates']],
            color='blue'
        ).add_to(m)

        for alt in route['features'][1:]:
            folium.PolyLine(
                locations=[(c[1], c[0]) for c in alt['geometry']['coordinates']],
                color='orange', weight=3, opacity=0.7
            ).add_to(m)

        st_folium(m, width=700, height=500)

        st.subheader("🤖 Smart Travel Assistant")
        user_query = st.text_input("Ask something (e.g., 'suggest nearby attractions', 'traffic condition on this route')")
        if user_query:
            st.info("🧠 This feature will be powered by a travel-specific LLM or chatbot soon!")

    except Exception as e:
        st.error(f"Error displaying route: {e}")
