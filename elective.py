import streamlit as st
import json
import requests
import pandas as pd
from datetime import datetime
import openai

# -------------------- Constants --------------------
STORAGE_FILE = "crops.json"

# -------------------- Load API keys from secrets --------------------
OPENAI_KEY = st.secrets["OPENAI_KEY"]
WEATHER_KEY = st.secrets["WEATHER_KEY"]

# -------------------- Helper Functions --------------------

def load_crops():
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_crops(crops):
    with open(STORAGE_FILE, "w") as f:
        json.dump(crops, f, indent=2)

def get_weather(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        r = requests.get(url).json()
        if "main" in r:
            return f"{city}: {r['main']['temp']}°C, {r['weather'][0]['description']}"
        else:
            return "Error: check city name or API key"
    except:
        return "Error: Could not fetch weather"

def load_market_prices():
    data = {
        "Crop": ["Wheat", "Rice", "Maize", "Tomato"],
        "Price per Qtl": [2200, 2500, 1800, 6000],
        "Market": ["Market A", "Market B", "Market A", "Market C"]
    }
    return pd.DataFrame(data)

def gpt4o_chatbot_response(query, api_key):
    try:
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agriculture assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="🌾 Agri Dashboard", layout="wide")
st.title("🌾 Agri Dashboard - All in One")

# -------------------- Crop Dashboard --------------------
st.header("🌱 Crop Records")

crops = load_crops()
if crops:
    st.table(crops)
else:
    st.write("No crop records yet.")

st.subheader("Add a New Crop")
with st.form("add_crop_form"):
    name = st.text_input("Crop Name")
    area = st.number_input("Area (hectares)", min_value=0.0)
    yield_est = st.number_input("Expected Yield (qt/ha)", min_value=0.0)
    submitted = st.form_submit_button("Save Crop")
    if submitted:
        if name:
            new_crop = {
                "name": name,
                "area": area,
                "expected_yield": yield_est,
                "added_on": str(datetime.now())
            }
            crops.append(new_crop)
            save_crops(crops)
            st.success("Crop saved!")
        else:
            st.warning("Enter crop name!")

st.markdown("---")

# -------------------- Weather --------------------
st.header("☀️ Weather Forecast")
with st.form("weather_form"):
    city = st.text_input("Enter City", key="weather_city")
    weather_submitted = st.form_submit_button("Get Weather")
    if weather_submitted:
        if city:
            st.write(get_weather(city, WEATHER_KEY))
        else:
            st.warning("Enter city name")

st.markdown("---")

# -------------------- Market Prices --------------------
st.header("💰 Market Prices")
df = load_market_prices()
st.table(df)

st.markdown("---")

# -------------------- GPT-4o-mini Chatbot --------------------
st.header("🤖 Ask AgriBot")
with st.form("chat_form"):
    query = st.text_input("Ask me something...", key="chat_query")
    chat_submitted = st.form_submit_button("Ask")
    if chat_submitted:
        if query:
            answer = gpt4o_chatbot_response(query, OPENAI_KEY)
            st.write(answer)
        else:
            st.warning("Enter your question")
