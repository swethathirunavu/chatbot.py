import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import requests
import cohere

st.set_page_config(page_title="Get Your Path", layout="wide")
st.title("🧭 Get Your Path - AI Travel Assistant")

st.markdown("""
Type your starting and destination places. This app will:
- Show the best route on a map
- Display distance and duration
- Provide step-by-step directions
- Offer route alternatives (Fastest/Recommended/Shortest)
- Answer your travel queries like a smart assistant 🧠
""")

# Initialize session state
if "route_info" not in st.session_state:
    st.session_state["route_info"] = None

# OpenRouteService Client
try:
    ors_client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
except Exception as e:
    st.error("🔐 ORS API key not found. Add it in `.streamlit/secrets.toml`.")
    st.stop()

# Input Fields
start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")
end_place = st.text_input("Enter Destination", placeholder="e.g. Kaveri Bridge, Bhavani")
route_preference = st.selectbox("Select Route Preference", ("Recommended", "Fastest", "Shortest"))

# Geocoding Helper
def geocode_place(place_name):
    try:
        geolocator = Nominatim(user_agent="get-your-path")
        location = geolocator.geocode(place_name)
        return (location.latitude, location.longitude) if location else None
    except:
        return None

# Button: Find Route
if st.button("Find Route"):
    start_coords = geocode_place(start_place)
    end_coords = geocode_place(end_place)

    if not start_coords or not end_coords:
        st.error("❌ Could not find one or both locations. Please check spelling.")
    else:
        try:
            headers = {
                'Authorization': st.secrets["ORS_API_KEY"],
                'Content-Type': 'application/json'
            }
            data = {
                "coordinates": [list(start_coords[::-1]), list(end_coords[::-1])],
                "instructions": True,
                "format": "geojson",
                "alternative_routes": {"share_factor": 0.5, "target_count": 2},
            }

            if route_preference == "Shortest":
                data["options"] = {"weighting": "shortest"}
            elif route_preference == "Fastest":
                data["options"] = {"weighting": "fastest"}

            response = requests.post("https://api.openrouteservice.org/v2/directions/driving-car",
                                     json=data, headers=headers)
            route = response.json()

            if "features" not in route or not route["features"]:
                st.error("❌ No route found. Please try different locations.")
            else:
                st.session_state["route_info"] = {
                    "route": route,
                    "start_coords": start_coords,
                    "end_coords": end_coords
                }

        except Exception as e:
            st.error(f"Error fetching route: {e}")

# Display Route if Available
if st.session_state["route_info"]:
    try:
        route = st.session_state["route_info"]["route"]
        start_coords = st.session_state["route_info"]["start_coords"]
        end_coords = st.session_state["route_info"]["end_coords"]

        segment = route['features'][0]['properties']['segments'][0]
        distance = segment['distance'] / 1000
        duration = segment['duration'] / 60
        st.success(f"**Distance:** {distance:.2f} km | **Estimated Time:** {duration:.1f} mins")

        st.subheader("📍 Step-by-step Directions:")
        for i, step in enumerate(segment['steps']):
            icon = "🧭"
            if "left" in step['instruction'].lower(): icon = "⬅️"
            elif "right" in step['instruction'].lower(): icon = "➡️"
            elif "roundabout" in step['instruction'].lower(): icon = "🔄"
            st.markdown(f"{i+1}. {icon} {step['instruction']}")

        # Draw Map
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
                color='orange', weight=3, opacity=0.6
            ).add_to(m)

        st_folium(m, width=700, height=500)
    except Exception as e:
        st.error(f"Error displaying route: {e}")

# Smart Assistant
st.divider()
st.subheader("🤖 Smart Travel Assistant")

user_query = st.text_input("Ask a travel-related question (e.g., 'suggest places near Kodaikanal')")
if user_query:
    try:
        co = cohere.Client(st.secrets["COHERE_API_KEY"])
        response = co.chat(message=user_query, model="command-r", temperature=0.7)
        st.markdown(f"💬 **Assistant:** {response.text}")
    except Exception as e:
        st.error("❌ Error with assistant. Check Cohere API key in `.streamlit/secrets.toml`.")


