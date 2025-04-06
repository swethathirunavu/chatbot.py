import streamlit as st
import cohere

st.set_page_config(page_title="Smart Assistant", layout="wide")
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
if st.button("← Back to Route Planner"):
    st.switch_page("chatbot.py")

