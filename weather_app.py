import os
import pytz
import pyowm
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# API key
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    st.error("API Key is missing. Please check your .env file!")
    st.stop()

owm = pyowm.OWM(API_KEY)
mgr = owm.weather_manager()

# Frontend
st.title("Weather Forecast for 5 Days! 🌦")
st.write("### Enter a city, select the temperature unit and graph type from the sidebar.")

# Sidebar Inputs
st.sidebar.header("Weather Settings")
place = st.sidebar.text_input("City Name:", "")
Temp_Unit = st.sidebar.selectbox("Temperature Unit", ("Celsius", "Fahrenheit"))
Graph_type = st.sidebar.selectbox("Graph Type", ("Line Graph", "Bar Graph"))

# Submit button
if st.sidebar.button("Get Forecast") and place:
    try:
        # Fetch the 5-day forecast (3-hour interval)
        forecast = mgr.forecast_at_place(place, '3h').forecast
        dates_dict = {}

        for weather in forecast.weathers:  # Fix: Correct way to iterate
            timestamp = weather.reference_time()
            dt_object = datetime.utcfromtimestamp(timestamp).date()  # Keep only date

            temp_kelvin = weather.temperature('kelvin')
            temp_min = temp_kelvin.get("temp_min")
            temp_max = temp_kelvin.get("temp_max")

            if temp_min is None or temp_max is None:
                continue  # Skip if temperature data is missing

            # Convert temperature
            if Temp_Unit == "Celsius":
                temp_min = round(temp_min - 273.15, 1)
                temp_max = round(temp_max - 273.15, 1)
            else:
                temp_min = round((temp_min - 273.15) * 9/5 + 32, 1)
                temp_max = round((temp_max - 273.15) * 9/5 + 32, 1)

            # Initialize the date dictionary entry if it doesn't exist
            if dt_object not in dates_dict:
                dates_dict[dt_object] = {"min": float("inf"), "max": float("-inf")}

            # Update min/max temperatures for the date
            dates_dict[dt_object]["min"] = min(dates_dict[dt_object]["min"], temp_min)
            dates_dict[dt_object]["max"] = max(dates_dict[dt_object]["max"], temp_max)

        # Ensure data is available
        if not dates_dict:
            st.warning("No temperature data available for this city. Try another one!")
            st.stop()

        # Prepare final data
        dates_list = list(dates_dict.keys())
        temp_min_list = [dates_dict[d]["min"] for d in dates_list]
        temp_max_list = [dates_dict[d]["max"] for d in dates_list]

        # Generate numeric positions for the x-axis
        x = np.arange(len(dates_list))  

        # Plot the data
        fig, ax = plt.subplots(figsize=(6, 4))

        if Graph_type == "Line Graph":
            ax.plot(x, temp_min_list, marker="o", linestyle="-", color="darkblue", label="Min Temp")
            ax.plot(x, temp_max_list, marker="o", linestyle="-", color="orange", label="Max Temp")
        else:  # Bar Graph
            width = 0.35  # Adjusted width for spacing
            ax.bar(x - width/2, temp_min_list, width, color="darkblue", label="Min Temp")
            ax.bar(x + width/2, temp_max_list, width, color="orange", label="Max Temp")
        
            # Add temperature labels on top of bars
            for i in range(len(dates_list)):
                ax.text(i - width/2, temp_min_list[i] + 1, f"{temp_min_list[i]}°", ha='center', color="white", fontsize=10, fontweight="bold")
                ax.text(i + width/2, temp_max_list[i] + 1, f"{temp_max_list[i]}°", ha='center', color="black", fontsize=10, fontweight="bold")

        # Formatting
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime("%m/%d") for d in dates_list], rotation=0, fontsize=10)
        plt.xlabel("Date", fontsize=8)
        plt.ylabel(f"Temperature ({Temp_Unit})", fontsize=8)
        plt.title(f"Temperature Forecast for {place}", fontsize=12, pad=20)
        plt.legend(loc='upper left', bbox_to_anchor=(1,1))
        plt.grid(False)

        # Show the plot in Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error("Error fetching weather data. Please check the city name and try again!")
        st.write(f"Error details: {e}")

    # Fetching the current weather data
    try:
        current_weather = mgr.weather_at_place(place).weather

        # Additional Weather Details
        st.subheader("🌍 Additional Weather Details")

        # Checking for certain weather conditions
        forecaster = mgr.forecast_at_place(place, '3h')
        weather_conditions = {
            "Rain": forecaster.will_have_rain(),
            "Clear Skies": forecaster.will_have_clear(),
            "Fog": forecaster.will_have_fog(),
            "Clouds": forecaster.will_have_clouds(),
            "Snow": forecaster.will_have_snow(),
            "Storm": forecaster.will_have_storm(),
            "Tornado": forecaster.will_have_tornado(),
            "Hurricane": forecaster.will_have_hurricane()
        }    

        # Display upcoming weather conditions
        st.write("### ☁ Impending Weather Changes:")
        for condition, will_happen in weather_conditions.items():
            emoji = "✅" if will_happen else "❌"
            st.write(f"{emoji} {condition} expected in the next 5 days.")

        # Cloud coverage, wind speed, and humidity
        cloud_coverage = current_weather.clouds
        wind_speed = current_weather.wind().get("speed", 0)  # Fix: Handle missing key
        humidity = current_weather.humidity

        st.write(f"☁ **Cloud Coverage:** {cloud_coverage}%")
        st.write(f"💨 **Wind Speed:** {wind_speed} m/s")
        st.write(f"💧 **Humidity:** {humidity}%")

        # Sunrise and Sunset Times
        sunrise_time = datetime.utcfromtimestamp(current_weather.sunrise_time()).strftime('%Y-%m-%d %H:%M:%S GMT')
        sunset_time = datetime.utcfromtimestamp(current_weather.sunset_time()).strftime('%Y-%m-%d %H:%M:%S GMT')

        st.write(f"🌅 **Sunrise Time:** {sunrise_time}")
        st.write(f"🌇 **Sunset Time:** {sunset_time}")

    except Exception as e:
        st.error("Error fetching current weather data.")
        st.write(f"Error details: {e}")




 










