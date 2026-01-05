"""
Crop Recommendation Module
Suggests optimal crops based on location, climate, soil conditions, and seasonal factors
"""

import ee
from datetime import datetime

# Comprehensive crop database with growing requirements
CROP_DATABASE = {
    "rice": {
        "name": "Rice (Paddy)",
        "emoji": "🌾",
        "min_temp": 20,
        "max_temp": 35,
        "optimal_rainfall": (1200, 2000),  # mm per year
        "min_ndvi": 0.3,
        "growing_season": ["kharif"],  # June-November
        "soil_types": ["clay", "loamy"],
        "water_requirement": "high",
        "yield_potential": "4-6 tons/ha",
        "growing_days": "120-150",
        "best_states": ["West Bengal", "Punjab", "Uttar Pradesh", "Andhra Pradesh", "Tamil Nadu"]
    },
    "wheat": {
        "name": "Wheat",
        "emoji": "🌾",
        "min_temp": 10,
        "max_temp": 25,
        "optimal_rainfall": (400, 750),
        "min_ndvi": 0.25,
        "growing_season": ["rabi"],  # November-April
        "soil_types": ["loamy", "clay loam"],
        "water_requirement": "medium",
        "yield_potential": "3-5 tons/ha",
        "growing_days": "100-120",
        "best_states": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan"]
    },
    "maize": {
        "name": "Maize (Corn)",
        "emoji": "🌽",
        "min_temp": 18,
        "max_temp": 32,
        "optimal_rainfall": (500, 1000),
        "min_ndvi": 0.3,
        "growing_season": ["kharif", "rabi"],
        "soil_types": ["loamy", "sandy loam"],
        "water_requirement": "medium",
        "yield_potential": "5-8 tons/ha",
        "growing_days": "90-120",
        "best_states": ["Karnataka", "Madhya Pradesh", "Bihar", "Tamil Nadu", "Andhra Pradesh"]
    },
    "cotton": {
        "name": "Cotton",
        "emoji": "☁️",
        "min_temp": 21,
        "max_temp": 35,
        "optimal_rainfall": (500, 1000),
        "min_ndvi": 0.25,
        "growing_season": ["kharif"],
        "soil_types": ["black cotton", "loamy"],
        "water_requirement": "medium",
        "yield_potential": "1.5-2.5 tons/ha",
        "growing_days": "150-180",
        "best_states": ["Gujarat", "Maharashtra", "Telangana", "Madhya Pradesh", "Punjab"]
    },
    "sugarcane": {
        "name": "Sugarcane",
        "emoji": "🎋",
        "min_temp": 20,
        "max_temp": 35,
        "optimal_rainfall": (1500, 2500),
        "min_ndvi": 0.4,
        "growing_season": ["annual"],
        "soil_types": ["loamy", "clay loam"],
        "water_requirement": "very_high",
        "yield_potential": "70-100 tons/ha",
        "growing_days": "300-365",
        "best_states": ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat"]
    },
    "soybean": {
        "name": "Soybean",
        "emoji": "🫘",
        "min_temp": 20,
        "max_temp": 30,
        "optimal_rainfall": (600, 1000),
        "min_ndvi": 0.3,
        "growing_season": ["kharif"],
        "soil_types": ["loamy", "clay loam"],
        "water_requirement": "medium",
        "yield_potential": "2-3 tons/ha",
        "growing_days": "90-120",
        "best_states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka"]
    },
    "groundnut": {
        "name": "Groundnut (Peanut)",
        "emoji": "🥜",
        "min_temp": 22,
        "max_temp": 32,
        "optimal_rainfall": (500, 750),
        "min_ndvi": 0.25,
        "growing_season": ["kharif", "rabi"],
        "soil_types": ["sandy loam", "loamy"],
        "water_requirement": "low",
        "yield_potential": "1.5-2.5 tons/ha",
        "growing_days": "100-130",
        "best_states": ["Gujarat", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Rajasthan"]
    },
    "mustard": {
        "name": "Mustard",
        "emoji": "🌻",
        "min_temp": 10,
        "max_temp": 25,
        "optimal_rainfall": (250, 500),
        "min_ndvi": 0.2,
        "growing_season": ["rabi"],
        "soil_types": ["loamy", "sandy loam"],
        "water_requirement": "low",
        "yield_potential": "1-1.5 tons/ha",
        "growing_days": "90-120",
        "best_states": ["Rajasthan", "Uttar Pradesh", "Haryana", "Madhya Pradesh"]
    },
    "potato": {
        "name": "Potato",
        "emoji": "🥔",
        "min_temp": 15,
        "max_temp": 25,
        "optimal_rainfall": (400, 600),
        "min_ndvi": 0.3,
        "growing_season": ["rabi"],
        "soil_types": ["sandy loam", "loamy"],
        "water_requirement": "medium",
        "yield_potential": "20-30 tons/ha",
        "growing_days": "80-120",
        "best_states": ["Uttar Pradesh", "West Bengal", "Bihar", "Gujarat", "Punjab"]
    },
    "onion": {
        "name": "Onion",
        "emoji": "🧅",
        "min_temp": 13,
        "max_temp": 30,
        "optimal_rainfall": (350, 550),
        "min_ndvi": 0.2,
        "growing_season": ["rabi", "kharif"],
        "soil_types": ["loamy", "sandy loam"],
        "water_requirement": "medium",
        "yield_potential": "15-25 tons/ha",
        "growing_days": "100-150",
        "best_states": ["Maharashtra", "Karnataka", "Gujarat", "Bihar", "Madhya Pradesh"]
    },
    "tomato": {
        "name": "Tomato",
        "emoji": "🍅",
        "min_temp": 18,
        "max_temp": 30,
        "optimal_rainfall": (400, 600),
        "min_ndvi": 0.25,
        "growing_season": ["rabi", "kharif"],
        "soil_types": ["loamy", "sandy loam"],
        "water_requirement": "medium",
        "yield_potential": "25-40 tons/ha",
        "growing_days": "90-120",
        "best_states": ["Andhra Pradesh", "Madhya Pradesh", "Karnataka", "Gujarat", "Odisha"]
    },
    "chilli": {
        "name": "Chilli",
        "emoji": "🌶️",
        "min_temp": 20,
        "max_temp": 35,
        "optimal_rainfall": (600, 1200),
        "min_ndvi": 0.25,
        "growing_season": ["kharif", "rabi"],
        "soil_types": ["loamy", "sandy loam"],
        "water_requirement": "medium",
        "yield_potential": "2-4 tons/ha",
        "growing_days": "120-150",
        "best_states": ["Andhra Pradesh", "Karnataka", "Madhya Pradesh", "West Bengal"]
    },
    "turmeric": {
        "name": "Turmeric",
        "emoji": "🧡",
        "min_temp": 20,
        "max_temp": 35,
        "optimal_rainfall": (1500, 2500),
        "min_ndvi": 0.3,
        "growing_season": ["kharif"],
        "soil_types": ["loamy", "clay loam"],
        "water_requirement": "high",
        "yield_potential": "20-30 tons/ha",
        "growing_days": "240-300",
        "best_states": ["Telangana", "Tamil Nadu", "Andhra Pradesh", "Odisha", "Karnataka"]
    },
    "pulses": {
        "name": "Pulses (Lentils/Dal)",
        "emoji": "🫛",
        "min_temp": 15,
        "max_temp": 30,
        "optimal_rainfall": (300, 600),
        "min_ndvi": 0.2,
        "growing_season": ["rabi"],
        "soil_types": ["loamy", "clay loam"],
        "water_requirement": "low",
        "yield_potential": "1-1.5 tons/ha",
        "growing_days": "90-120",
        "best_states": ["Madhya Pradesh", "Uttar Pradesh", "Rajasthan", "Maharashtra"]
    },
    "banana": {
        "name": "Banana",
        "emoji": "🍌",
        "min_temp": 20,
        "max_temp": 35,
        "optimal_rainfall": (1500, 2500),
        "min_ndvi": 0.4,
        "growing_season": ["annual"],
        "soil_types": ["loamy", "clay loam"],
        "water_requirement": "very_high",
        "yield_potential": "50-70 tons/ha",
        "growing_days": "300-365",
        "best_states": ["Tamil Nadu", "Maharashtra", "Gujarat", "Andhra Pradesh", "Karnataka"]
    }
}


def get_current_season():
    """Determine current growing season based on month."""
    month = datetime.now().month
    if month in [6, 7, 8, 9, 10, 11]:
        return "kharif"
    elif month in [11, 12, 1, 2, 3, 4]:
        return "rabi"
    else:
        return "zaid"


def get_region_from_coordinates(lat, lng):
    """Approximate region/state based on coordinates (simplified)."""
    # Simplified region detection for India
    if lat > 28:
        if lng < 77:
            return "Punjab/Haryana"
        else:
            return "Uttar Pradesh"
    elif lat > 23:
        if lng < 75:
            return "Rajasthan/Gujarat"
        elif lng < 82:
            return "Madhya Pradesh"
        else:
            return "West Bengal/Bihar"
    elif lat > 15:
        if lng < 75:
            return "Maharashtra"
        elif lng < 80:
            return "Telangana/Andhra Pradesh"
        else:
            return "Odisha"
    else:
        if lng < 77:
            return "Karnataka"
        else:
            return "Tamil Nadu"


def calculate_crop_score(crop_data, ndvi, rainfall, temperature, season, lat, lng):
    """
    Calculate suitability score for a crop based on environmental factors.
    Score ranges from 0 to 100.
    """
    score = 0
    reasons = []
    
    # NDVI score (25 points)
    if ndvi >= crop_data["min_ndvi"]:
        ndvi_score = min(25, (ndvi / crop_data["min_ndvi"]) * 15 + 10)
        score += ndvi_score
        if ndvi >= 0.5:
            reasons.append("Excellent soil health")
        elif ndvi >= 0.3:
            reasons.append("Good vegetation cover")
    else:
        score += 5
        reasons.append("Low vegetation - may need soil preparation")
    
    # Rainfall score (30 points)
    min_rain, max_rain = crop_data["optimal_rainfall"]
    if min_rain <= rainfall <= max_rain:
        score += 30
        reasons.append("Ideal rainfall conditions")
    elif rainfall < min_rain:
        # Partial score based on how close
        score += max(10, 30 * (rainfall / min_rain))
        reasons.append("May need irrigation")
    else:
        # Too much rain
        score += max(15, 30 - (rainfall - max_rain) / 100)
        reasons.append("Excess rainfall - drainage important")
    
    # Season match (25 points)
    if season in crop_data["growing_season"] or "annual" in crop_data["growing_season"]:
        score += 25
        reasons.append(f"Perfect for {season} season")
    else:
        score += 5
        reasons.append(f"Better suited for other seasons")
    
    # Regional suitability (20 points)
    region = get_region_from_coordinates(lat, lng)
    regional_match = any(state.lower() in region.lower() for state in crop_data.get("best_states", []))
    if regional_match:
        score += 20
        reasons.append(f"Well-suited for {region}")
    else:
        score += 10
        reasons.append("Can grow in this region")
    
    return min(100, score), reasons


def get_crop_recommendations(geometry, ndvi_value, rainfall_total, landcover_data=None):
    """
    Generate crop recommendations based on environmental analysis.
    
    Args:
        geometry: ee.Geometry object (used to extract coordinates)
        ndvi_value: Mean NDVI value (0-1)
        rainfall_total: Total rainfall in mm
        landcover_data: Land cover classification data
    
    Returns:
        dict: Contains recommended crops with scores and reasons
    """
    try:
        # Get center coordinates
        try:
            centroid = geometry.centroid().coordinates().getInfo()
            lng, lat = centroid
        except:
            lat, lng = 20.0, 78.0  # Default to central India
        
        # Get current season
        season = get_current_season()
        
        # Estimate temperature based on latitude and season (simplified)
        if season == "kharif":
            temperature = 30  # Summer/monsoon
        else:
            temperature = 22  # Winter
        
        # Calculate scores for all crops
        crop_scores = []
        for crop_id, crop_data in CROP_DATABASE.items():
            score, reasons = calculate_crop_score(
                crop_data, 
                ndvi_value or 0.3, 
                rainfall_total or 500, 
                temperature, 
                season,
                lat, lng
            )
            
            crop_scores.append({
                "id": crop_id,
                "name": crop_data["name"],
                "emoji": crop_data["emoji"],
                "score": round(score, 1),
                "reasons": reasons[:3],  # Top 3 reasons
                "water_requirement": crop_data["water_requirement"],
                "yield_potential": crop_data["yield_potential"],
                "growing_days": crop_data["growing_days"],
                "growing_season": crop_data["growing_season"]
            })
        
        # Sort by score and get top 5
        crop_scores.sort(key=lambda x: x["score"], reverse=True)
        top_crops = crop_scores[:5]
        
        # Add match level labels
        for crop in top_crops:
            if crop["score"] >= 80:
                crop["match_level"] = "Excellent Match"
                crop["match_color"] = "excellent"
            elif crop["score"] >= 60:
                crop["match_level"] = "Good Match"
                crop["match_color"] = "good"
            elif crop["score"] >= 40:
                crop["match_level"] = "Moderate Match"
                crop["match_color"] = "moderate"
            else:
                crop["match_level"] = "Low Match"
                crop["match_color"] = "low"
        
        return {
            "recommendations": top_crops,
            "season": season,
            "region": get_region_from_coordinates(lat, lng),
            "analysis_factors": {
                "ndvi": ndvi_value,
                "rainfall": rainfall_total,
                "temperature_estimate": temperature,
                "location": {"lat": lat, "lng": lng}
            }
        }
        
    except Exception as e:
        return {
            "recommendations": [],
            "error": str(e)
        }
