"""
Gemini AI Orchestrator for Crop Recommendations
Handles structured input/output with Gemini, validation, caching, and fallback.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any
from cachetools import TTLCache
import google.generativeai as genai
from dotenv import load_dotenv

# Import local modules
from .crop_catalog import (
    get_allowed_crops, 
    get_crop_metadata, 
    validate_crop_name,
    validate_duration,
    validate_yield,
    CROP_METADATA,
    WATER_NEED_DISPLAY
)
from .crop_recommend import get_crop_recommendations as get_rule_based_recommendations

# Load environment variables
load_dotenv()

# Initialize Gemini with API key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured with GEMINI_API_KEY from .env")
else:
    print("⚠️ GEMINI_API_KEY not found in .env - will use rule-based fallback")

# Cache for recommendations (24 hour TTL, max 1000 entries)
RECOMMENDATION_CACHE = TTLCache(maxsize=1000, ttl=86400)

# Gemini model configuration
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_TIMEOUT = 12  # seconds


def get_cache_key(lat: float, lng: float, season: str, ndvi: float) -> str:
    """Generate cache key from location, season, and soil conditions."""
    geohash = f"{round(lat, 3)}_{round(lng, 3)}"
    ndvi_bucket = round(ndvi, 1)
    key_string = f"{geohash}_{season}_{ndvi_bucket}"
    return hashlib.md5(key_string.encode()).hexdigest()[:16]


def get_state_from_coordinates(lat: float, lng: float) -> str:
    """Determine approximate state from coordinates."""
    # Simplified region detection for India
    if lat > 28:
        if lng < 76:
            return "Punjab"
        elif lng < 78:
            return "Haryana"
        else:
            return "Uttar Pradesh"
    elif lat > 23:
        if lng < 73:
            return "Gujarat"
        elif lng < 75:
            return "Rajasthan"
        elif lng < 80:
            return "Madhya Pradesh"
        elif lng < 85:
            return "Bihar"
        else:
            return "West Bengal"
    elif lat > 18:
        if lng < 75:
            return "Maharashtra"
        elif lng < 80:
            return "Telangana"
        else:
            return "Andhra Pradesh"
    elif lat > 15:
        if lng < 77:
            return "Karnataka"
        else:
            return "Andhra Pradesh"
    else:
        if lng < 77:
            return "Karnataka"
        else:
            return "Tamil Nadu"


def get_current_season() -> str:
    """Determine current growing season based on month."""
    month = datetime.now().month
    if month in [6, 7, 8, 9, 10]:
        return "kharif"
    elif month in [11, 12, 1, 2, 3, 4]:
        return "rabi"
    else:
        return "zaid"


def build_agro_profile(
    lat: float,
    lng: float,
    ndvi_value: float,
    rainfall_data: dict,
    weather_data: Optional[dict] = None,
    landcover_data: Optional[dict] = None
) -> dict:
    """
    Build structured agro-profile for Gemini input.
    """
    state = get_state_from_coordinates(lat, lng)
    season = get_current_season()
    allowed_crops = get_allowed_crops(state, season)
    
    # Extract weather info
    avg_temp = 28
    humidity = 65
    if weather_data and not weather_data.get("error"):
        avg_temp = weather_data.get("temperature", 28)
        humidity = weather_data.get("humidity", 65)
    
    # Extract rainfall info
    rainfall_total = 0
    rainfall_last_30d = 0
    if rainfall_data:
        stats = rainfall_data.get("statistics", {})
        rainfall_total = stats.get("total_rainfall", 0)
        rainfall_last_30d = stats.get("mean_monthly", 0) if stats.get("mean_monthly") else rainfall_total / 12
    
    # Determine NDVI trend (simplified)
    ndvi_trend = "stable"
    if ndvi_value > 0.5:
        ndvi_trend = "healthy"
    elif ndvi_value < 0.25:
        ndvi_trend = "stressed"
    
    # Build profile
    agro_profile = {
        "location": {
            "lat": round(lat, 4),
            "lng": round(lng, 4),
            "state": state,
            "country": "India"
        },
        "season": {
            "current": season,
            "sowing_month": datetime.now().strftime("%B")
        },
        "weather": {
            "avg_temp_celsius": round(avg_temp, 1),
            "humidity_percent": round(humidity, 0),
            "annual_rainfall_mm": round(rainfall_total, 0),
            "recent_rainfall_mm": round(rainfall_last_30d, 0)
        },
        "satellite": {
            "ndvi_current": round(ndvi_value, 3),
            "ndvi_trend": ndvi_trend,
            "vegetation_health": "good" if ndvi_value > 0.4 else "moderate" if ndvi_value > 0.25 else "poor"
        },
        "allowed_crops": allowed_crops,
        "request": {
            "top_n": 5,
            "include_reasons": True
        }
    }
    
    return agro_profile


def build_gemini_prompt(agro_profile: dict) -> str:
    """Build the prompt for Gemini API."""
    
    prompt = f"""You are an expert agricultural advisor for Indian farming. Analyze the agro-profile below and recommend the TOP 5 most suitable crops for this location and season.

STRICT RULES - YOU MUST FOLLOW THESE EXACTLY:
1. Return ONLY valid JSON - no markdown, no code blocks, no explanations outside JSON
2. Use ONLY crops from the "allowed_crops" list provided below
3. Base all decisions on the supplied data only - no external assumptions
4. confidence must be a decimal between 0.0 and 1.0
5. match_level must be exactly one of: "Excellent", "Good", or "Moderate"
6. water_need must be exactly one of: "Low", "Medium", "High", or "Very High"
7. Provide exactly 5 crop recommendations
8. Each explanation must have 3-5 bullet points

AGRO-PROFILE DATA:
{json.dumps(agro_profile, indent=2)}

REQUIRED OUTPUT FORMAT (return ONLY this JSON structure):
{{
  "recommendations": [
    {{
      "crop_name": "Full Crop Name",
      "crop_id": "crop_key_from_allowed_list",
      "match_level": "Excellent",
      "confidence": 0.85,
      "yield_range": "X-Y tons/ha",
      "duration_days": "90-120",
      "water_need": "Medium",
      "explanation": [
        "First reason explaining why this crop suits the conditions",
        "Second reason about soil/weather compatibility",
        "Third reason about seasonal suitability"
      ],
      "cautions": ["Optional warning about growing this crop"]
    }}
  ]
}}

Remember: Return ONLY the JSON object, nothing else. Start with {{ and end with }}."""

    return prompt


def validate_gemini_response(response_json: dict, allowed_crops: list) -> tuple:
    """
    Validate Gemini response against schema and constraints.
    Returns (is_valid, errors, cleaned_response)
    """
    errors = []
    
    # Check basic structure
    if not isinstance(response_json, dict):
        return False, ["Response is not a valid JSON object"], None
    
    if "recommendations" not in response_json:
        return False, ["Missing 'recommendations' key"], None
    
    recommendations = response_json.get("recommendations", [])
    if not isinstance(recommendations, list):
        return False, ["'recommendations' must be a list"], None
    
    if len(recommendations) == 0:
        return False, ["No recommendations provided"], None
    
    valid_match_levels = ["Excellent", "Good", "Moderate"]
    valid_water_needs = ["Low", "Medium", "High", "Very High"]
    
    cleaned_recommendations = []
    
    for i, rec in enumerate(recommendations[:5]):  # Max 5
        rec_errors = []
        
        # Validate crop name
        crop_name = rec.get("crop_name", "")
        crop_id = rec.get("crop_id", "").lower()
        
        is_valid_crop, validated_id, display_name = validate_crop_name(crop_name)
        if not is_valid_crop:
            is_valid_crop, validated_id, display_name = validate_crop_name(crop_id)
        
        if not is_valid_crop:
            rec_errors.append(f"Invalid crop: {crop_name}")
            continue
        
        # Validate match_level
        match_level = rec.get("match_level", "Moderate")
        if match_level not in valid_match_levels:
            match_level = "Moderate"
        
        # Validate confidence
        confidence = rec.get("confidence", 0.5)
        try:
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))
        except:
            confidence = 0.5
        
        # Validate water_need
        water_need = rec.get("water_need", "Medium")
        if water_need not in valid_water_needs:
            water_need = "Medium"
        
        # Get crop metadata for emoji
        meta = get_crop_metadata(validated_id)
        emoji = meta.get("emoji", "🌱") if meta else "🌱"
        
        # Validate and clean duration
        duration = rec.get("duration_days", "90-120")
        if not validate_duration(validated_id, str(duration)):
            if meta:
                min_d, max_d = meta.get("duration_range", (90, 120))
                duration = f"{min_d}-{max_d}"
        
        # Validate and clean yield
        yield_range = rec.get("yield_range", "2-4 tons/ha")
        if not validate_yield(validated_id, str(yield_range)):
            if meta:
                min_y, max_y = meta.get("yield_range", (2, 4))
                yield_range = f"{min_y}-{max_y} tons/ha"
        
        # Get explanations
        explanation = rec.get("explanation", [])
        if not isinstance(explanation, list) or len(explanation) == 0:
            explanation = ["Suitable for current conditions"]
        explanation = explanation[:5]  # Max 5 reasons
        
        # Get cautions (optional)
        cautions = rec.get("cautions", [])
        if not isinstance(cautions, list):
            cautions = []
        
        # Convert confidence to score (0-100)
        score = round(confidence * 100, 1)
        
        # Determine match color
        if match_level == "Excellent":
            match_color = "excellent"
        elif match_level == "Good":
            match_color = "good"
        else:
            match_color = "moderate"
        
        # Build cleaned recommendation (matching existing UI format)
        cleaned_rec = {
            "id": validated_id,
            "name": display_name,
            "emoji": emoji,
            "score": score,
            "match_level": f"{match_level} Match",
            "match_color": match_color,
            "confidence": confidence,
            "yield_potential": yield_range,
            "growing_days": str(duration),
            "water_requirement": water_need.lower().replace(" ", "_"),
            "reasons": explanation[:3],
            "cautions": cautions,
            "source": "gemini"
        }
        
        cleaned_recommendations.append(cleaned_rec)
    
    if len(cleaned_recommendations) == 0:
        return False, errors + ["No valid recommendations after validation"], None
    
    return True, errors, {"recommendations": cleaned_recommendations}


def call_gemini_api(prompt: str) -> Optional[dict]:
    """
    Call Gemini API and parse JSON response.
    Returns parsed JSON or None on failure.
    """
    if not GEMINI_API_KEY:
        print("⚠️ Gemini API key not configured")
        return None
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Configure generation settings
        generation_config = genai.GenerationConfig(
            temperature=0.3,  # Lower temperature for more consistent output
            max_output_tokens=2048,
        )
        
        # Make API call
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Extract text
        response_text = response.text.strip()
        
        # Clean up response - remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first line (```json) and last line (```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines)
        
        # Parse JSON
        response_json = json.loads(response_text)
        return response_json
        
    except json.JSONDecodeError as e:
        print(f"❌ Gemini response JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return None


def get_gemini_recommendations(
    geometry,
    ndvi_value: float,
    rainfall_data: dict,
    weather_data: Optional[dict] = None,
    landcover_data: Optional[dict] = None,
    use_cache: bool = True
) -> dict:
    """
    Main entry point for Gemini-powered crop recommendations.
    Falls back to rule-based system if Gemini fails.
    
    Args:
        geometry: ee.Geometry object
        ndvi_value: Mean NDVI value (0-1)
        rainfall_data: Rainfall data from Earth Engine
        weather_data: Weather API data (optional)
        landcover_data: Land cover data (optional)
        use_cache: Whether to use caching
    
    Returns:
        dict: Recommendations in the same format as rule-based system
    """
    
    # Extract coordinates
    try:
        centroid = geometry.centroid().coordinates().getInfo()
        lng, lat = centroid
    except:
        lat, lng = 20.0, 78.0  # Default to central India
    
    season = get_current_season()
    state = get_state_from_coordinates(lat, lng)
    
    # Check cache first
    if use_cache:
        cache_key = get_cache_key(lat, lng, season, ndvi_value or 0.3)
        if cache_key in RECOMMENDATION_CACHE:
            print("✅ Returning cached Gemini recommendations")
            cached = RECOMMENDATION_CACHE[cache_key]
            cached["from_cache"] = True
            return cached
    
    # Try Gemini first
    gemini_result = None
    
    if GEMINI_API_KEY:
        try:
            print("🤖 Calling Gemini AI for crop recommendations...")
            
            # Build agro profile
            agro_profile = build_agro_profile(
                lat=lat,
                lng=lng,
                ndvi_value=ndvi_value or 0.3,
                rainfall_data=rainfall_data or {},
                weather_data=weather_data,
                landcover_data=landcover_data
            )
            
            # Build prompt
            prompt = build_gemini_prompt(agro_profile)
            
            # Call Gemini
            response_json = call_gemini_api(prompt)
            
            if response_json:
                # Validate response
                is_valid, errors, cleaned = validate_gemini_response(
                    response_json,
                    agro_profile.get("allowed_crops", [])
                )
                
                if is_valid and cleaned:
                    gemini_result = {
                        "recommendations": cleaned["recommendations"],
                        "season": season,
                        "region": state,
                        "analysis_factors": {
                            "ndvi": ndvi_value,
                            "rainfall": rainfall_data.get("statistics", {}).get("total_rainfall", 0) if rainfall_data else 0,
                            "temperature_estimate": weather_data.get("temperature", 28) if weather_data else 28,
                            "location": {"lat": lat, "lng": lng}
                        },
                        "source": "gemini",
                        "from_cache": False
                    }
                    
                    # Cache the result
                    if use_cache:
                        RECOMMENDATION_CACHE[cache_key] = gemini_result.copy()
                    
                    print("✅ Gemini recommendations generated successfully")
                    return gemini_result
                else:
                    print(f"⚠️ Gemini response validation failed: {errors}")
                    
        except Exception as e:
            print(f"❌ Gemini processing error: {e}")
    
    # Fallback to rule-based system
    print("🔄 Falling back to rule-based recommendations...")
    
    rule_based_result = get_rule_based_recommendations(
        geometry,
        ndvi_value,
        rainfall_data.get("statistics", {}).get("total_rainfall", 0) if rainfall_data else 0,
        landcover_data
    )
    
    # Mark as rule-based
    rule_based_result["source"] = "rule_based"
    rule_based_result["from_cache"] = False
    
    # Add source to each recommendation
    for rec in rule_based_result.get("recommendations", []):
        rec["source"] = "rule_based"
    
    return rule_based_result
