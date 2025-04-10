import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import cohere

# Set page configuration once at the start
st.set_page_config(page_title="Get Your Path", layout="wide")

# Define your app's logic for the "Get Your Path" section
def get_your_path():
    st.title("🗺️ Get Your Path")
    st.markdown("""
    Enter starting and destination places by name. This app will:
    - Show the best route on a map
    - Display distance and duration
    - Provide step-by-step directions
    - Allow route alternatives (shortest, fastest, recommended)
    """)

    if "route_info" not in st.session_state:
        st.session_state.route_info = None

    if "client" not in st.session_state:
        try:
            st.session_state.client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
        except Exception as e:
            st.error(f"OpenRouteService API key issue: {e}")

    start_place = st.text_input("Enter Starting Place", placeholder="e.g. Bhavani Bus Stand")
    end_place = st.text_input("Enter Destination", placeholder="e.g. Kaveri Bridge, Bhavani")

    route_preference = st.selectbox(
        "Select Route Preference",
        ("Fastest", "Shortest", "Recommended")
    )

    def geocode_place(place_name):
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

                route = st.session_state.client.directions(
                    coordinates=[start_coords[::-1], end_coords[::-1]],
                    profile=profile,
                    format='geojson'
                )

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
                st.markdown(f"{i+1}. {step['instruction']}")

            m = folium.Map(location=start_coords, zoom_start=13)
            folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
            folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color='red')).add_to(m)
            folium.PolyLine(
                locations=[(c[1], c[0]) for c in route['features'][0]['geometry']['coordinates']],
                color='blue'
            ).add_to(m)

            # Optional alternative routes
            if route_preference != "Shortest":
                try:
                    alt_route = st.session_state.client.directions(
                        coordinates=[start_coords[::-1], end_coords[::-1]],
                        profile='driving-car',
                        format='geojson'
                    )

                    for alt in alt_route['features'][1:]:
                        folium.PolyLine(
                            locations=[(c[1], c[0]) for c in alt['geometry']['coordinates']],
                            color='orange',
                            weight=3,
                            opacity=0.7
                        ).add_to(m)
                except Exception as e:
                    st.warning(f"Could not load alternate routes: {e}")

            st_folium(m, width=700, height=500)

        except Exception as e:
            st.error(f"Error displaying route: {e}")

# Define your app's logic for the "Smart Assistant" section
def smart_assistant():
    st.title("🧠 Smart Travel Assistant")

    st.markdown("""
    Ask anything travel-related and get instant help! Examples:
    - Suggest tourist spots in Kodaikanal
    - Best time to visit Manali
    - Foods to try in Hyderabad
    """)

    user_query = st.text_input("Ask your travel question:")

    if user_query:
        with st.spinner("Thinking..."):
            try:
                co = cohere.Client(st.secrets["COHERE_API_KEY"])
                response = co.chat(message=user_query, model="command-r", temperature=0.7)
                assistant_reply = response.text
                st.markdown(f"💬 **Assistant:** {assistant_reply}")
            except Exception as e:
                st.error(f"Error fetching assistant reply: {e}")

# Streamlit's page switching feature could be used to decide which section to show
page = st.selectbox("Select a page", ("Get Your Path", "Smart Assistant"))

if page == "Get Your Path":
    get_your_path()
else:
    smart_assistant()

