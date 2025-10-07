import streamlit as st
import json
import requests
import pandas as pd
from datetime import datetime
import openai

# -------------------- Constants --------------------
STORAGE_FILE = "crops.json"

# -------------------- Load API keys --------------------
OPENAI_KEY = st.secrets.get("OPENAI_KEY", None)
WEATHER_KEY = st.secrets.get("WEATHER_KEY", None)

# Fallback if secrets missing
if OPENAI_KEY is None:
    OPENAI_KEY = st.text_input("Enter OpenAI API Key", type="password")
if WEATHER_KEY is None:
    WEATHER_KEY = st.text_input("Enter OpenWeatherMap API Key", type="password")

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

def get_weather(city_name):
    try:
        # Get coordinates from city name
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={WEATHER_KEY}"
        geo_data = requests.get(geo_url).json()
        if not geo_data:
            return "⚠️ City not found."
        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
        # Get weather using coordinates
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric"
        weather_data = requests.get(weather_url).json()
        description = weather_data["weather"][0]["description"].capitalize()
        temp = weather_data["main"]["temp"]
        wind = weather_data["wind"]["speed"]

        return (
            f"📍 Location: {city_name}\n"
            f"🌤 Weather: {description}\n"
            f"🌡 Temperature: {temp} °C\n"
            f"💨 Wind Speed: {wind} m/s"
        )

    except Exception:
        return "⚠️ Unable to fetch weather data."

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

def load_market_prices():
    data = {
        "Crop": ["Wheat", "Rice", "Maize", "Tomato", "Potato", "Onion", "Sugarcane", "Soybean"],
        "Market A": [2200, 2400, 1800, 6000, 1200, 1500, 3000, 2500],
        "Market B": [2250, 2500, 1850, 6100, 1250, 1550, 3050, 2600],
        "Market C": [2180, 2450, 1900, 5950, 1180, 1520, 2980, 2550]
    }
    return pd.DataFrame(data)

# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="🌾 Agri Dashboard", layout="wide")
st.title("🌾 Agri Dashboard ")

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
        if city and WEATHER_KEY:
            st.text(get_weather(city))
        else:
            st.warning("Enter city name and API key")

st.markdown("---")

# -------------------- Market Prices --------------------
st.header("💰 Market Prices")
df = load_market_prices()

# Crop filter
crop_filter = st.selectbox("Select a crop to view prices", ["All"] + df["Crop"].tolist())
if crop_filter != "All":
    df_filtered = df[df["Crop"] == crop_filter]
else:
    df_filtered = df.copy()

# Format numeric columns as integers
df_filtered_formatted = df_filtered.copy()
numeric_cols = df_filtered_formatted.select_dtypes(include="number").columns
df_filtered_formatted[numeric_cols] = df_filtered_formatted[numeric_cols].astype(int)

# Display table
st.dataframe(df_filtered_formatted)

# Bar chart visualization
st.subheader("📊 Price Comparison Chart")
chart_data = df_filtered_formatted.set_index("Crop")
st.bar_chart(chart_data)

st.markdown("---")

# -------------------- GPT-4o-mini Chatbot --------------------
st.header("🤖 Ask AgriBot ")
with st.form("chat_form"):
    query = st.text_input("Ask me something...", key="chat_query")
    chat_submitted = st.form_submit_button("Ask")
    if chat_submitted:
        if query and OPENAI_KEY:
            answer = gpt4o_chatbot_response(query, OPENAI_KEY)
            st.write(answer)
        else:
            st.warning("Enter your question and make sure API key is available")
