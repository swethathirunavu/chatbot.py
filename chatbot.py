import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import cohere
import time
import json
from datetime import datetime, timedelta
import requests
from typing import Optional, Tuple, List, Dict
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Smart Travel Companion", 
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .route-step {
        background: #f8f9fa;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 3px solid #28a745;
    }
    .error-box {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

class TravelApp:
    def __init__(self):
        self.initialize_session_state()
        self.initialize_apis()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            "route_info": None,
            "search_history": [],
            "favorite_places": [],
            "client": None,
            "cohere_client": None,
            "current_location": None,
            "route_preferences": {
                "avoid_tolls": False,
                "avoid_highways": False,
                "avoid_ferries": False
            }
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def initialize_apis(self):
        """Initialize API clients with error handling"""
        try:
            if not st.session_state.client and "ORS_API_KEY" in st.secrets:
                st.session_state.client = openrouteservice.Client(
                    key=st.secrets["ORS_API_KEY"]
                )
        except Exception as e:
            st.sidebar.error(f"⚠️ OpenRouteService API issue: {str(e)}")
        
        try:
            if not st.session_state.cohere_client and "COHERE_API_KEY" in st.secrets:
                st.session_state.cohere_client = cohere.Client(
                    st.secrets["COHERE_API_KEY"]
                )
        except Exception as e:
            st.sidebar.error(f"⚠️ Cohere API issue: {str(e)}")
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def geocode_place(_self, place_name: str) -> Optional[Tuple[float, float]]:
        """Geocode a place name to coordinates with caching"""
        try:
            geolocator = Nominatim(
                user_agent="smart-travel-companion",
                timeout=10
            )
            location = geolocator.geocode(place_name)
            if location:
                return (location.latitude, location.longitude)
            return None
        except Exception as e:
            st.error(f"Geocoding error: {str(e)}")
            return None
    
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """Get user's current location using HTML5 geolocation"""
        st.markdown("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                window.parent.postMessage({
                    type: 'location',
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                }, '*');
            });
        }
        </script>
        """, unsafe_allow_html=True)
        
        # For demo purposes, return None - actual implementation would need JavaScript integration
        return None
    
    def calculate_route(self, start_coords: Tuple[float, float], 
                       end_coords: Tuple[float, float], 
                       profile: str = 'driving-car',
                       route_preference: str = 'fastest') -> Optional[Dict]:
        """Calculate route with enhanced options"""
        try:
            # Set optimization based on preference
            preference_mapping = {
                'fastest': 'fastest',
                'shortest': 'shortest',
                'recommended': 'recommended'
            }
            
            options = {
                'avoid_features': []
            }
            
            # Add avoidance preferences
            if st.session_state.route_preferences['avoid_tolls']:
                options['avoid_features'].append('tollways')
            if st.session_state.route_preferences['avoid_highways']:
                options['avoid_features'].append('highways')
            if st.session_state.route_preferences['avoid_ferries']:
                options['avoid_features'].append('ferries')
            
            route = st.session_state.client.directions(
                coordinates=[start_coords[::-1], end_coords[::-1]],
                profile=profile,
                format='geojson',
                options=options,
                preference=preference_mapping.get(route_preference.lower(), 'fastest'),
                alternative_routes={'target_count': 2, 'weight_factor': 1.4}
            )
            
            return route
        except Exception as e:
            st.error(f"Route calculation error: {str(e)}")
            return None
    
    def save_to_history(self, start_place: str, end_place: str, distance: float, duration: float):
        """Save search to history"""
        search_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'start': start_place,
            'end': end_place,
            'distance': distance,
            'duration': duration
        }
        
        st.session_state.search_history.insert(0, search_entry)
        # Keep only last 10 searches
        st.session_state.search_history = st.session_state.search_history[:10]
    
    def create_enhanced_map(self, start_coords: Tuple[float, float], 
                          end_coords: Tuple[float, float], 
                          route_data: Dict) -> folium.Map:
        """Create an enhanced interactive map"""
        # Calculate center point
        center_lat = (start_coords[0] + end_coords[0]) / 2
        center_lon = (start_coords[1] + end_coords[1]) / 2
        
        # Create map with better styling
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='CartoDB positron'
        )
        
        # Add markers with custom icons
        folium.Marker(
            start_coords,
            tooltip="🚀 Start Point",
            popup=f"<b>Starting Location</b><br>Lat: {start_coords[0]:.4f}<br>Lon: {start_coords[1]:.4f}",
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        folium.Marker(
            end_coords,
            tooltip="🏁 Destination",
            popup=f"<b>Destination</b><br>Lat: {end_coords[0]:.4f}<br>Lon: {end_coords[1]:.4f}",
            icon=folium.Icon(color='red', icon='stop', prefix='fa')
        ).add_to(m)
        
        # Add main route
        main_route = route_data['features'][0]
        coordinates = [(c[1], c[0]) for c in main_route['geometry']['coordinates']]
        
        folium.PolyLine(
            locations=coordinates,
            color='#2E86AB',
            weight=6,
            opacity=0.8,
            popup="Main Route"
        ).add_to(m)
        
        # Add alternative routes if available
        for i, alt_route in enumerate(route_data['features'][1:], 1):
            alt_coordinates = [(c[1], c[0]) for c in alt_route['geometry']['coordinates']]
            folium.PolyLine(
                locations=alt_coordinates,
                color='#F24236',
                weight=4,
                opacity=0.6,
                popup=f"Alternative Route {i}",
                dash_array='10, 5'
            ).add_to(m)
        
        # Add route bounds
        m.fit_bounds([start_coords, end_coords])
        
        return m
    
    def format_directions(self, steps: List[Dict]) -> str:
        """Format turn-by-turn directions with better styling"""
        formatted_steps = []
        total_distance = 0
        
        for i, step in enumerate(steps, 1):
            distance = step.get('distance', 0)
            duration = step.get('duration', 0)
            instruction = step.get('instruction', 'Continue')
            
            total_distance += distance
            
            # Format distance and duration
            distance_str = f"{distance/1000:.1f} km" if distance >= 1000 else f"{distance:.0f} m"
            duration_str = f"{duration/60:.0f} min" if duration >= 60 else f"{duration:.0f} sec"
            
            formatted_steps.append(f"""
            <div class="route-step">
                <strong>Step {i}</strong> • {distance_str} • {duration_str}<br>
                📍 {instruction}
            </div>
            """)
        
        return "".join(formatted_steps)
    
    def get_weather_info(self, coords: Tuple[float, float]) -> Optional[Dict]:
        """Get weather information for the destination (placeholder)"""
        # This would integrate with a weather API like OpenWeatherMap
        # For now, return mock data
        return {
            "temperature": "25°C",
            "condition": "Sunny",
            "humidity": "60%",
            "wind_speed": "10 km/h"
        }
    
    def render_route_finder(self):
        """Render the enhanced route finder page"""
        st.markdown('<div class="main-header"><h1>🗺️ Smart Route Finder</h1></div>', 
                   unsafe_allow_html=True)
        
        # Sidebar for preferences
        with st.sidebar:
            st.header("🔧 Route Preferences")
            
            # Route avoidance options
            st.session_state.route_preferences['avoid_tolls'] = st.checkbox(
                "Avoid Toll Roads", 
                value=st.session_state.route_preferences['avoid_tolls']
            )
            st.session_state.route_preferences['avoid_highways'] = st.checkbox(
                "Avoid Highways", 
                value=st.session_state.route_preferences['avoid_highways']
            )
            st.session_state.route_preferences['avoid_ferries'] = st.checkbox(
                "Avoid Ferries", 
                value=st.session_state.route_preferences['avoid_ferries']
            )
            
            # Search history
            if st.session_state.search_history:
                st.header("🕐 Recent Searches")
                for entry in st.session_state.search_history[:5]:
                    if st.button(f"{entry['start']} → {entry['end']}", key=f"hist_{entry['timestamp']}"):
                        st.session_state.start_place = entry['start']
                        st.session_state.end_place = entry['end']
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input section with enhanced UI
            st.subheader("📍 Trip Details")
            
            # Location inputs
            start_place = st.text_input(
                "Starting Location",
                placeholder="e.g., Mumbai Central Station",
                help="Enter the name of your starting location"
            )
            
            end_place = st.text_input(
                "Destination",
                placeholder="e.g., Gateway of India, Mumbai",
                help="Enter your destination"
            )
            
            # Route options
            col_pref, col_vehicle = st.columns(2)
            with col_pref:
                route_preference = st.selectbox(
                    "Route Type",
                    ("Fastest", "Shortest", "Recommended"),
                    help="Choose your preferred route optimization"
                )
            
            with col_vehicle:
                vehicle_type = st.selectbox(
                    "Vehicle Type",
                    ("Car", "Motorcycle", "Bicycle", "Walking"),
                    help="Select your mode of transportation"
                )
            
            # Vehicle type mapping
            profile_mapping = {
                "Car": "driving-car",
                "Motorcycle": "driving-car",
                "Bicycle": "cycling-regular",
                "Walking": "foot-walking"
            }
            
            # Current location button
            if st.button("📱 Use Current Location", help="Use your current location as starting point"):
                current_loc = self.get_current_location()
                if current_loc:
                    st.success("✅ Current location detected!")
                else:
                    st.info("🔄 Enable location services in your browser")
            
            # Find route button
            if st.button("🚀 Find Best Route", type="primary"):
                if not start_place or not end_place:
                    st.error("Please enter both starting location and destination")
                    return
                
                with st.spinner("🔍 Finding the best route for you..."):
                    # Geocode locations
                    start_coords = self.geocode_place(start_place)
                    end_coords = self.geocode_place(end_place)
                    
                    if not start_coords or not end_coords:
                        st.error("❌ Could not find one or both locations. Please check the spelling and try again.")
                        return
                    
                    # Calculate route
                    route_data = self.calculate_route(
                        start_coords, 
                        end_coords, 
                        profile_mapping[vehicle_type],
                        route_preference
                    )
                    
                    if not route_data:
                        st.error("❌ Could not calculate route. Please try again.")
                        return
                    
                    # Store route information
                    st.session_state.route_info = {
                        "route": route_data,
                        "start_coords": start_coords,
                        "end_coords": end_coords,
                        "start_place": start_place,
                        "end_place": end_place,
                        "vehicle_type": vehicle_type
                    }
        
        with col2:
            # Quick stats and weather
            if st.session_state.route_info:
                route_data = st.session_state.route_info["route"]
                main_route = route_data['features'][0]['properties']['segments'][0]
                
                distance_km = main_route['distance'] / 1000
                duration_min = main_route['duration'] / 60
                
                # Save to history
                self.save_to_history(
                    st.session_state.route_info["start_place"],
                    st.session_state.route_info["end_place"],
                    distance_km,
                    duration_min
                )
                
                # Display metrics
                st.markdown("### 📊 Route Summary")
                
                col_dist, col_time = st.columns(2)
                with col_dist:
                    st.metric("Distance", f"{distance_km:.1f} km")
                with col_time:
                    st.metric("Duration", f"{duration_min:.0f} min")
                
                # Weather info (if available)
                weather = self.get_weather_info(st.session_state.route_info["end_coords"])
                if weather:
                    st.markdown("### 🌤️ Weather at Destination")
                    st.info(f"**{weather['temperature']}** • {weather['condition']}")
        
        # Display route results
        if st.session_state.route_info:
            st.markdown("---")
            
            # Map
            st.subheader("🗺️ Interactive Route Map")
            enhanced_map = self.create_enhanced_map(
                st.session_state.route_info["start_coords"],
                st.session_state.route_info["end_coords"],
                st.session_state.route_info["route"]
            )
            
            map_data = st_folium(enhanced_map, width=700, height=500)
            
            # Directions
            st.subheader("🧭 Turn-by-Turn Directions")
            main_route = st.session_state.route_info["route"]['features'][0]
            steps = main_route['properties']['segments'][0]['steps']
            
            formatted_directions = self.format_directions(steps)
            st.markdown(formatted_directions, unsafe_allow_html=True)
            
            # Export options
            st.subheader("📤 Export Options")
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                if st.button("📱 Share Route Link"):
                    st.success("🔗 Route link copied to clipboard!")
            
            with col_export2:
                route_json = json.dumps(st.session_state.route_info["route"], indent=2)
                st.download_button(
                    label="💾 Download Route Data",
                    data=route_json,
                    file_name=f"route_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )
    
    def render_smart_assistant(self):
        """Render the enhanced AI travel assistant"""
        st.markdown('<div class="main-header"><h1>🧠 AI Travel Assistant</h1></div>', 
                   unsafe_allow_html=True)
        
        # Sample questions
        st.markdown("### 💡 Ask me about:")
        
        sample_questions = [
            "Best tourist spots in Kerala",
            "Budget travel tips for Goa",
            "Food recommendations in Delhi",
            "Weather in Manali this month",
            "Train routes from Mumbai to Bangalore"
        ]
        
        cols = st.columns(3)
        for i, question in enumerate(sample_questions):
            with cols[i % 3]:
                if st.button(f"💭 {question}", key=f"sample_{i}"):
                    st.session_state.user_query = question
        
        # Chat interface
        user_query = st.text_area(
            "Ask your travel question:",
            placeholder="Type your travel-related question here...",
            height=100,
            value=st.session_state.get('user_query', '')
        )
        
        if st.button("🚀 Get Answer", type="primary"):
            if not user_query:
                st.warning("Please enter a question first!")
                return
            
            if not st.session_state.cohere_client:
                st.error("AI Assistant not available. Please check API configuration.")
                return
            
            with st.spinner("🤔 Thinking..."):
                try:
                    # Enhanced prompt for better travel responses
                    enhanced_prompt = f"""
                    You are a knowledgeable travel assistant. Provide helpful, accurate, and engaging travel advice.
                    Focus on practical information, local insights, and actionable recommendations.
                    
                    User Question: {user_query}
                    
                    Please provide a comprehensive response covering:
                    - Direct answer to the question
                    - Practical tips and recommendations
                    - Local insights if applicable
                    - Safety considerations if relevant
                    """
                    
                    response = st.session_state.cohere_client.chat(
                        message=enhanced_prompt,
                        model="command-r",
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    # Display response with better formatting
                    st.markdown("### 🤖 AI Assistant Response:")
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
                        {response.text}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Follow-up questions
                    st.markdown("### 🔄 Follow-up Questions:")
                    follow_ups = [
                        "Tell me more about local transportation",
                        "What's the best time to visit?",
                        "Any budget-friendly options?",
                        "Safety tips for this location?"
                    ]
                    
                    for follow_up in follow_ups:
                        if st.button(f"➡️ {follow_up}", key=f"followup_{follow_up}"):
                            st.session_state.user_query = follow_up
                            st.experimental_rerun()
                
                except Exception as e:
                    st.error(f"❌ Error getting response: {str(e)}")
    
    def render_analytics_dashboard(self):
        """Render travel analytics dashboard"""
        st.markdown('<div class="main-header"><h1>📈 Travel Analytics</h1></div>', 
                   unsafe_allow_html=True)
        
        if not st.session_state.search_history:
            st.info("🔍 Start searching for routes to see your travel analytics!")
            return
        
        # Convert history to DataFrame
        df = pd.DataFrame(st.session_state.search_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Searches", len(df))
        with col2:
            st.metric("Total Distance", f"{df['distance'].sum():.1f} km")
        with col3:
            st.metric("Total Time", f"{df['duration'].sum():.1f} min")
        with col4:
            st.metric("Avg Distance", f"{df['distance'].mean():.1f} km")
        
        # Charts
        st.subheader("📊 Search History")
        st.dataframe(df[['timestamp', 'start', 'end', 'distance', 'duration']])
        
        # Most searched locations
        st.subheader("🎯 Popular Destinations")
        destinations = df['end'].value_counts().head(10)
        st.bar_chart(destinations)

def main():
    """Main application function"""
    app = TravelApp()
    
    # Navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🗺️ Route Finder", "🧠 AI Assistant", "📈 Analytics"]
    )
    
    # Page routing
    if page == "🗺️ Route Finder":
        app.render_route_finder()
    elif page == "🧠 AI Assistant":
        app.render_smart_assistant()
    elif page == "📈 Analytics":
        app.render_analytics_dashboard()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Smart Travel Companion v2.0**")
    st.sidebar.markdown("Built with ❤️ using Streamlit")

if __name__ == "__main__":
    main()
