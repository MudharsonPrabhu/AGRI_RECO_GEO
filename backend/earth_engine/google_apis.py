"""
Google APIs Integration Module
Provides access to Pollen, Weather, and Solar APIs
"""

import os
import requests
from datetime import datetime, timedelta

# Get API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyDK9z8CiEjqUjxtTzwRALKLw-7LiieTxks")

# API Base URLs
POLLEN_API_URL = "https://pollen.googleapis.com/v1/forecast:lookup"
SOLAR_API_URL = "https://solar.googleapis.com/v1/buildingInsights:findClosest"
WEATHER_API_URL = "https://weather.googleapis.com/v1/forecast:lookup"


def get_pollen_data(lat, lng):
    """
    Fetch pollen forecast data from Google Pollen API.
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        dict: Pollen data including grass, tree, and weed pollen levels
    """
    try:
        params = {
            "key": GOOGLE_API_KEY,
            "location.latitude": lat,
            "location.longitude": lng,
            "days": 5,
            "languageCode": "en"
        }
        
        response = requests.get(POLLEN_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Process pollen data
            daily_info = data.get("dailyInfo", [])
            
            if not daily_info:
                return get_simulated_pollen_data(lat, lng)
            
            pollen_data = []
            for day in daily_info[:5]:
                day_data = {
                    "date": day.get("date", {}).get("year", "") + "-" + 
                            str(day.get("date", {}).get("month", "")).zfill(2) + "-" +
                            str(day.get("date", {}).get("day", "")).zfill(2),
                    "pollen_types": []
                }
                
                for pollen_type in day.get("pollenTypeInfo", []):
                    day_data["pollen_types"].append({
                        "type": pollen_type.get("displayName", "Unknown"),
                        "level": pollen_type.get("indexInfo", {}).get("value", 0),
                        "category": pollen_type.get("indexInfo", {}).get("category", "Unknown"),
                        "color": pollen_type.get("indexInfo", {}).get("color", {})
                    })
                
                pollen_data.append(day_data)
            
            # Calculate overall pollen index
            overall_index = calculate_overall_pollen(pollen_data)
            
            return {
                "daily_forecast": pollen_data,
                "overall_index": overall_index,
                "status": get_pollen_status(overall_index),
                "source": "Google Pollen API"
            }
        else:
            print(f"Pollen API error: {response.status_code} - {response.text}")
            return get_simulated_pollen_data(lat, lng)
            
    except Exception as e:
        print(f"Pollen API error: {e}")
        return get_simulated_pollen_data(lat, lng)


def get_simulated_pollen_data(lat, lng):
    """Generate simulated pollen data when API is unavailable."""
    month = datetime.now().month
    
    # Seasonal pollen patterns for India
    if month in [2, 3, 4]:  # Spring - high pollen
        grass_level = 4
        tree_level = 5
        weed_level = 3
    elif month in [9, 10, 11]:  # Autumn - moderate
        grass_level = 3
        tree_level = 2
        weed_level = 4
    elif month in [6, 7, 8]:  # Monsoon - low
        grass_level = 1
        tree_level = 1
        weed_level = 2
    else:  # Winter - very low
        grass_level = 1
        tree_level = 1
        weed_level = 1
    
    today = datetime.now()
    pollen_data = []
    
    for i in range(5):
        date = today + timedelta(days=i)
        pollen_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "pollen_types": [
                {"type": "Grass", "level": grass_level, "category": get_pollen_category(grass_level)},
                {"type": "Tree", "level": tree_level, "category": get_pollen_category(tree_level)},
                {"type": "Weed", "level": weed_level, "category": get_pollen_category(weed_level)}
            ]
        })
    
    overall_index = (grass_level + tree_level + weed_level) / 3
    
    return {
        "daily_forecast": pollen_data,
        "overall_index": round(overall_index, 1),
        "status": get_pollen_status(overall_index),
        "source": "Simulated (based on seasonal patterns)"
    }


def calculate_overall_pollen(pollen_data):
    """Calculate overall pollen index from daily data."""
    if not pollen_data:
        return 0
    
    total = 0
    count = 0
    for day in pollen_data:
        for pollen in day.get("pollen_types", []):
            total += pollen.get("level", 0)
            count += 1
    
    return round(total / count, 1) if count > 0 else 0


def get_pollen_category(level):
    """Get pollen category from level."""
    if level <= 1:
        return "Very Low"
    elif level <= 2:
        return "Low"
    elif level <= 3:
        return "Moderate"
    elif level <= 4:
        return "High"
    else:
        return "Very High"


def get_pollen_status(index):
    """Get overall pollen status."""
    if index <= 1:
        return {"level": "Very Low", "emoji": "🟢", "impact": "Minimal impact on crops"}
    elif index <= 2:
        return {"level": "Low", "emoji": "🟢", "impact": "Low pollination activity"}
    elif index <= 3:
        return {"level": "Moderate", "emoji": "🟡", "impact": "Good for crop pollination"}
    elif index <= 4:
        return {"level": "High", "emoji": "🟠", "impact": "Excellent pollination conditions"}
    else:
        return {"level": "Very High", "emoji": "🔴", "impact": "Very active pollination"}


def get_solar_data(lat, lng):
    """
    Fetch solar potential data from Google Solar API.
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        dict: Solar irradiance and potential data
    """
    try:
        params = {
            "key": GOOGLE_API_KEY,
            "location.latitude": lat,
            "location.longitude": lng
        }
        
        response = requests.get(SOLAR_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            solar_potential = data.get("solarPotential", {})
            
            return {
                "max_sunshine_hours": solar_potential.get("maxSunshineHoursPerYear", 0),
                "carbon_offset": solar_potential.get("carbonOffsetFactorKgPerMwh", 0),
                "panels_count": solar_potential.get("maxArrayPanelsCount", 0),
                "yearly_energy_dc_kwh": solar_potential.get("maxArrayAnnualEnergyDcKwh", 0),
                "roof_segment_stats": solar_potential.get("roofSegmentStats", []),
                "source": "Google Solar API"
            }
        else:
            return get_simulated_solar_data(lat, lng)
            
    except Exception as e:
        print(f"Solar API error: {e}")
        return get_simulated_solar_data(lat, lng)


def get_simulated_solar_data(lat, lng):
    """Generate simulated solar data based on location."""
    # Solar irradiance varies by latitude
    # India ranges from 4-7 kWh/m²/day
    
    if lat > 25:  # Northern India
        daily_irradiance = 5.2
        sunshine_hours = 2600
    elif lat > 20:  # Central India
        daily_irradiance = 5.5
        sunshine_hours = 2800
    elif lat > 15:  # Southern India
        daily_irradiance = 5.8
        sunshine_hours = 2900
    else:  # Far South
        daily_irradiance = 5.4
        sunshine_hours = 2700
    
    # Seasonal adjustment
    month = datetime.now().month
    if month in [4, 5, 6]:  # Summer - highest
        seasonal_factor = 1.2
    elif month in [10, 11, 12, 1, 2]:  # Winter - good
        seasonal_factor = 1.0
    else:  # Monsoon - lower
        seasonal_factor = 0.7
    
    adjusted_irradiance = round(daily_irradiance * seasonal_factor, 2)
    
    # Calculate solar potential for farming
    solar_score = min(100, round((adjusted_irradiance / 7) * 100))
    
    return {
        "daily_irradiance_kwh": adjusted_irradiance,
        "annual_sunshine_hours": sunshine_hours,
        "solar_score": solar_score,
        "status": get_solar_status(solar_score),
        "recommendations": get_solar_recommendations(adjusted_irradiance),
        "source": "Calculated (based on location and season)"
    }


def get_solar_status(score):
    """Get solar potential status."""
    if score >= 80:
        return {"level": "Excellent", "emoji": "☀️", "color": "#f59e0b"}
    elif score >= 60:
        return {"level": "Good", "emoji": "🌤️", "color": "#eab308"}
    elif score >= 40:
        return {"level": "Moderate", "emoji": "⛅", "color": "#84cc16"}
    else:
        return {"level": "Low", "emoji": "🌥️", "color": "#64748b"}


def get_solar_recommendations(irradiance):
    """Get farming recommendations based on solar irradiance."""
    recommendations = []
    
    if irradiance >= 5.5:
        recommendations.append("Ideal for solar-powered irrigation")
        recommendations.append("Good for solar drying of crops")
        recommendations.append("Consider solar pumps for water management")
    elif irradiance >= 4.5:
        recommendations.append("Suitable for solar water heating")
        recommendations.append("Good conditions for most crops")
    else:
        recommendations.append("Supplement with irrigation during cloudy days")
        recommendations.append("Consider shade-tolerant crops")
    
    return recommendations


def get_weather_data(lat, lng):
    """
    Fetch weather forecast data.
    Uses OpenWeatherMap or simulated data.
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        dict: Weather forecast data
    """
    try:
        # Try OpenWeatherMap API (free tier available)
        OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
        
        if OPENWEATHER_API_KEY:
            url = f"https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": lat,
                "lon": lng,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return process_openweather_data(data)
        
        # Fallback to simulated weather
        return get_simulated_weather_data(lat, lng)
        
    except Exception as e:
        print(f"Weather API error: {e}")
        return get_simulated_weather_data(lat, lng)


def get_simulated_weather_data(lat, lng):
    """Generate simulated weather data based on location and season."""
    month = datetime.now().month
    today = datetime.now()
    
    # Base temperature by latitude
    if lat > 28:  # Northern India
        base_temp = 25
    elif lat > 23:  # Central India
        base_temp = 28
    elif lat > 15:  # Southern India
        base_temp = 30
    else:
        base_temp = 28
    
    # Seasonal adjustments
    if month in [12, 1, 2]:  # Winter
        temp_adj = -8
        humidity = 50
        rain_chance = 10
        condition = "Clear"
    elif month in [3, 4, 5]:  # Summer
        temp_adj = 8
        humidity = 35
        rain_chance = 15
        condition = "Sunny"
    elif month in [6, 7, 8, 9]:  # Monsoon
        temp_adj = 2
        humidity = 85
        rain_chance = 70
        condition = "Rainy"
    else:  # Post-monsoon
        temp_adj = 0
        humidity = 60
        rain_chance = 25
        condition = "Partly Cloudy"
    
    current_temp = base_temp + temp_adj
    
    # Generate 5-day forecast
    forecast = []
    for i in range(5):
        date = today + timedelta(days=i)
        daily_variation = (i % 3) - 1  # Small variation
        
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A"),
            "temp_max": round(current_temp + 4 + daily_variation),
            "temp_min": round(current_temp - 4 + daily_variation),
            "humidity": humidity + (i * 2) % 10,
            "rain_chance": min(100, rain_chance + (i * 5) % 20),
            "condition": condition,
            "wind_speed": 10 + (i * 2),
            "wind_direction": "NE" if i % 2 == 0 else "SW"
        })
    
    # Current weather
    current = {
        "temperature": current_temp,
        "feels_like": current_temp + 2,
        "humidity": humidity,
        "condition": condition,
        "wind_speed": 12,
        "wind_direction": "NE",
        "pressure": 1013,
        "visibility": 10,
        "uv_index": 6 if month in [3, 4, 5] else 4
    }
    
    # Farming recommendations based on weather
    recommendations = get_weather_recommendations(current_temp, humidity, rain_chance, condition)
    
    return {
        "current": current,
        "forecast": forecast,
        "recommendations": recommendations,
        "alerts": get_weather_alerts(current_temp, humidity, rain_chance),
        "source": "Simulated (based on seasonal patterns)"
    }


def process_openweather_data(data):
    """Process OpenWeatherMap API response."""
    forecast = []
    seen_dates = set()
    
    for item in data.get("list", []):
        date = item.get("dt_txt", "").split(" ")[0]
        if date not in seen_dates and len(forecast) < 5:
            seen_dates.add(date)
            forecast.append({
                "date": date,
                "temp_max": item.get("main", {}).get("temp_max", 0),
                "temp_min": item.get("main", {}).get("temp_min", 0),
                "humidity": item.get("main", {}).get("humidity", 0),
                "condition": item.get("weather", [{}])[0].get("main", "Unknown"),
                "description": item.get("weather", [{}])[0].get("description", ""),
                "wind_speed": item.get("wind", {}).get("speed", 0)
            })
    
    current = data.get("list", [{}])[0] if data.get("list") else {}
    
    return {
        "current": {
            "temperature": current.get("main", {}).get("temp", 0),
            "feels_like": current.get("main", {}).get("feels_like", 0),
            "humidity": current.get("main", {}).get("humidity", 0),
            "condition": current.get("weather", [{}])[0].get("main", "Unknown"),
            "wind_speed": current.get("wind", {}).get("speed", 0)
        },
        "forecast": forecast,
        "city": data.get("city", {}).get("name", "Unknown"),
        "source": "OpenWeatherMap API"
    }


def get_weather_recommendations(temp, humidity, rain_chance, condition):
    """Get farming recommendations based on weather."""
    recommendations = []
    
    # Temperature-based
    if temp > 38:
        recommendations.append("⚠️ Extreme heat - increase irrigation frequency")
        recommendations.append("Protect plants with shade nets")
    elif temp > 32:
        recommendations.append("Apply mulch to retain soil moisture")
        recommendations.append("Water crops in early morning or evening")
    elif temp < 10:
        recommendations.append("Protect frost-sensitive crops")
        recommendations.append("Delay sowing of summer crops")
    
    # Rain-based
    if rain_chance > 60:
        recommendations.append("🌧️ Postpone pesticide application")
        recommendations.append("Ensure proper drainage in fields")
    elif rain_chance < 20 and humidity < 40:
        recommendations.append("💧 Increase irrigation")
    
    # Humidity-based
    if humidity > 80:
        recommendations.append("🍃 Monitor for fungal diseases")
        recommendations.append("Improve air circulation in crop canopy")
    
    if not recommendations:
        recommendations.append("✅ Good conditions for farming activities")
    
    return recommendations


def get_weather_alerts(temp, humidity, rain_chance):
    """Generate weather alerts for farming."""
    alerts = []
    
    if temp > 40:
        alerts.append({
            "type": "Heat Wave",
            "severity": "high",
            "message": "Extreme heat expected. Take precautions for livestock and crops."
        })
    
    if rain_chance > 80:
        alerts.append({
            "type": "Heavy Rain",
            "severity": "medium",
            "message": "Heavy rainfall expected. Avoid harvesting and spraying."
        })
    
    if humidity > 90:
        alerts.append({
            "type": "High Humidity",
            "severity": "low",
            "message": "High humidity may increase disease pressure."
        })
    
    return alerts
