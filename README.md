## 📍 Get Your Path

Get Your Path is a smart, conversational route-finding application built using Streamlit. It helps users find the best route between two named locations—no coordinates required—while offering a voice-assisted and user-friendly experience similar to a travel companion. The project aims to blend AI, map services, and real-time data into a simple yet powerful tool.

## 📌 Key Features

✅ Enter Location Names Directly
✅ Map Display with Route Visualization
✅ Text-based Route Instructions
✅ Alternate Routes: Fastest, Shortest, Recommended
✅ Step-by-step Directions
✅ Live User Location Detection
✅ LLM-powered Smart Assistant (Cohere)
✅ Smart Travel Queries
✅ Mobile Responsive

## 🏧 Project Structure
Get_Your_Path/
│
├── .streamlit/
│   └── config.toml              # Streamlit page configuration
│
├── pages/
│   └── smartassis.py            # Smart assistant chatbot page
│
├── Get_Your_Path.py            # Main route-finder page
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── assets/                     # (Optional) CSS, images, icons, etc


## 🛠️ Tech Stack

Frontend & App Framework: Streamlit
Backend & Logic: Python
Mapping & Routing: OpenRouteService API
Geocoding: Geopy + Nominatim
LLM Chat Integration: Cohere
Map Rendering: Folium + streamlit-folium

<img width="761" height="728" alt="image" src="https://github.com/user-attachments/assets/222a513a-1aa5-4c68-a267-3c19668ee10e" />

🌍[Live Demo](https://chatbotpy-nqfg3qsjtnjmr25d4ye5uh.streamlit.app/)

📊 Planned Enhancements
🌐 Public transport suggestions
📢 Voice interaction
🛰️ Real-time user tracking
📈 Analytics dashboard (e.g. most searched places)
🔐 User login and personalization
🎤 Voice-to-text route assistant (future)

🔑 API Keys Required

| API              | Usage                        | Docs/Link                                                                 |
|------------------|------------------------------|---------------------------------------------------------------------------|
| OpenRouteService | Routing and directions       | [Sign Up](https://openrouteservice.org/dev/#/signup)                     |
| Cohere           | Smart Assistant Chat API     | [Cohere Docs](https://docs.cohere.com)                                   |
| Geopy + Nominatim| Geocoding by location name   | [Nominatim](https://nominatim.openstreetmap.org/)                        |

## 🛣️ Author

Swetha B.Tech CSE Student | Full Stack Enthusiast | AI & ML Explorer📬 
[LinkedIn💡](https://www.linkedin.com/in/swetha-thirunavu/)
"Let your path be guided—not guessed."





