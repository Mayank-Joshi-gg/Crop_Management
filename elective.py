import streamlit as st
import json
import requests
import pandas as pd
from datetime import datetime

# Local file to store crop records
STORAGE_FILE = "crops.json"

# Load existing crops
def load_crops():
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Save crops
def save_crops(crops):
    with open(STORAGE_FILE, "w") as f:
        json.dump(crops, f, indent=2)

# Get weather from OpenWeatherMap
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

# Sample market prices
def load_market_prices():
    data = {
        "Crop": ["Wheat", "Rice", "Maize", "Tomato"],
        "Price per Qtl": [2200, 2500, 1800, 6000],
        "Market": ["Market A", "Market B", "Market A", "Market C"]
    }
    return pd.DataFrame(data)

# Simple chatbot response
def chatbot_response(query):
    query = query.lower()
    if "weather" in query:
        return "Go to the Weather tab to check forecasts."
    elif "crop" in query:
        return "You can add or view crops in the Dashboard tab."
    elif "price" in query or "market" in query:
        return "Check the Market Prices tab for latest rates."
    else:
        return "I can help with crops, weather, and prices!"

# ------------------- Streamlit UI -------------------

st.title("🌾 Simple Agri Dashboard")

tabs = st.tabs(["Dashboard", "Weather", "Market Prices", "Chatbot"])

# Dashboard tab
with tabs[0]:
    st.header("Crop Records")

    crops = load_crops()

    if crops:
        st.table(crops)
    else:
        st.write("No crop records yet.")

    st.subheader("Add a New Crop")
    name = st.text_input("Crop Name")
    area = st.number_input("Area (hectares)", min_value=0.0)
    yield_est = st.number_input("Expected Yield (qt/ha)", min_value=0.0)
    if st.button("Save Crop"):
        new_crop = {
            "name": name,
            "area": area,
            "expected_yield": yield_est,
            "added_on": str(datetime.now())
        }
        crops.append(new_crop)
        save_crops(crops)
        st.success("Crop saved!")

# Weather tab
with tabs[1]:
    st.header("Weather Forecast")
    city = st.text_input("Enter City")
    api_key = st.text_input("Enter OpenWeatherMap API Key", type="password")
    if st.button("Get Weather"):
        if city and api_key:
            st.write(get_weather(city, api_key))
        else:
            st.warning("Enter both city and API key")

# Market Prices tab
with tabs[2]:
    st.header("Market Prices")
    df = load_market_prices()
    st.table(df)

# Chatbot tab
with tabs[3]:
    st.header("Chatbot")
    query = st.text_input("Ask me something...")
    if st.button("Ask"):
        st.write(chatbot_response(query))

