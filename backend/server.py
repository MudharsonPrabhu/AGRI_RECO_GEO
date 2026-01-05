"""
Smart Farmer Geo Dashboard - Backend Server
Flask API for Earth Engine analysis endpoints
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import ee
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000", "*"])

# Initialize Earth Engine
def initialize_earth_engine():
    """Initialize Earth Engine with service account or user credentials."""
    project_id = os.getenv("GCP_PROJECT_ID", "gen-lang-client-0415859748")
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./service-account-key.json")
    
    # Try user credentials first (from earthengine authenticate)
    try:
        ee.Initialize(project=project_id)
        print(f"Earth Engine initialized with user credentials for project: {project_id}")
        return
    except Exception as e1:
        print(f"User credentials failed: {e1}")
    
    # Try service account credentials
    try:
        if os.path.exists(credentials_file):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/earthengine']
            )
            ee.Initialize(credentials=credentials, project=project_id)
            print(f"Earth Engine initialized with service account for project: {project_id}")
            return
    except Exception as e2:
        print(f"Service account failed: {e2}")
    
    # Final fallback - no project
    try:
        ee.Initialize()
        print("Earth Engine initialized with default credentials (no project)")
    except Exception as e3:
        print(f"All initialization methods failed: {e3}")
        raise e3

# Initialize on startup
initialize_earth_engine()

# Import Earth Engine modules after initialization
from earth_engine.ndvi import get_ndvi, get_ndvi_timeseries
from earth_engine.rainfall import get_rainfall_timeseries, get_drought_index
from earth_engine.landcover import get_landcover_stats, get_landcover_area
from earth_engine.yield_model import estimate_yield
from earth_engine.crop_recommend import get_crop_recommendations
from earth_engine.gemini_orchestrator import get_gemini_recommendations
from earth_engine.google_apis import get_pollen_data, get_solar_data, get_weather_data


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Smart Farmer Geo Dashboard API",
        "version": "1.0.0",
        "earth_engine": "connected"
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.
    Accepts GeoJSON geometry and returns comprehensive analysis.
    
    Request body:
    {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[lng, lat], ...]]
        }
    }
    
    Returns:
    {
        "ndvi": float,
        "rainfall": {...},
        "landcover": {...},
        "yield_prediction": float
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or "geometry" not in data:
            return jsonify({"error": "Missing geometry in request body"}), 400
        
        geojson = data["geometry"]
        
        # Convert GeoJSON to Earth Engine Geometry
        geometry = ee.Geometry(geojson)
        
        print(f"📍 Analyzing geometry: {geojson['type']}")
        
        # Run all analyses
        # 1. NDVI Analysis
        print("🌿 Calculating NDVI...")
        ndvi_result = get_ndvi(geometry)
        ndvi_value = ndvi_result.get("ndvi", 0)
        
        # 2. Rainfall Analysis
        print("🌧️ Fetching rainfall data...")
        rainfall_result = get_rainfall_timeseries(geometry)
        rainfall_total = rainfall_result.get("statistics", {}).get("total_rainfall", 0)
        
        # 3. Land Cover Analysis
        print("🗺️ Analyzing land cover...")
        landcover_result = get_landcover_stats(geometry)
        
        # 4. Yield Prediction
        print("🌾 Predicting yield...")
        yield_result = estimate_yield(ndvi_value, rainfall_total)
        yield_prediction = yield_result.get("yield_prediction", 0)
        
        # 5. Drought Index
        print("Calculating drought index...")
        drought_result = get_drought_index(geometry)
        
        # Get center coordinates for API calls (needed for weather and crop recommendations)
        try:
            centroid = geometry.centroid().coordinates().getInfo()
            lng, lat = centroid
        except:
            lat, lng = 20.0, 78.0  # Default to central India
        
        # 6. Weather Data (fetch before crop recommendations)
        print("🌤️ Fetching weather data...")
        weather_data = get_weather_data(lat, lng)
        
        # 7. Pollen Data
        print("🌸 Fetching pollen data...")
        pollen_data = get_pollen_data(lat, lng)
        
        # 8. Solar Data
        print("☀️ Fetching solar data...")
        solar_data = get_solar_data(lat, lng)
        
        # 9. Crop Recommendations (Gemini AI with fallback to rule-based)
        print("🤖 Generating AI-powered crop recommendations...")
        crop_recommendations = get_gemini_recommendations(
            geometry=geometry,
            ndvi_value=ndvi_value,
            rainfall_data=rainfall_result,
            weather_data=weather_data,
            landcover_data=landcover_result
        )
        
        # Compile response
        response = {
            "ndvi": ndvi_value,
            "ndvi_details": ndvi_result,
            "rainfall": rainfall_result,
            "landcover": landcover_result.get("raw", {}),
            "landcover_details": landcover_result,
            "yield_prediction": yield_prediction,
            "yield_details": yield_result,
            "drought": drought_result,
            "crop_recommendations": crop_recommendations,
            "pollen": pollen_data,
            "solar": solar_data,
            "weather": weather_data,
            "location": {"lat": lat, "lng": lng},
            "analysis_complete": True
        }
        
        print("✅ Analysis complete!")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return jsonify({
            "error": str(e),
            "analysis_complete": False
        }), 500


@app.route("/ndvi", methods=["POST"])
def ndvi_endpoint():
    """Get NDVI analysis for a geometry."""
    try:
        data = request.get_json()
        geometry = ee.Geometry(data["geometry"])
        
        result = get_ndvi(geometry)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ndvi-timeseries", methods=["POST"])
def ndvi_timeseries_endpoint():
    """Get NDVI time series for a geometry."""
    try:
        data = request.get_json()
        geometry = ee.Geometry(data["geometry"])
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        result = get_ndvi_timeseries(geometry, start_date, end_date)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/rainfall", methods=["POST"])
def rainfall_endpoint():
    """Get rainfall analysis for a geometry."""
    try:
        data = request.get_json()
        geometry = ee.Geometry(data["geometry"])
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        result = get_rainfall_timeseries(geometry, start_date, end_date)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/landcover", methods=["POST"])
def landcover_endpoint():
    """Get land cover classification for a geometry."""
    try:
        data = request.get_json()
        geometry = ee.Geometry(data["geometry"])
        
        stats = get_landcover_stats(geometry)
        area = get_landcover_area(geometry)
        
        return jsonify({
            "statistics": stats,
            "area": area
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/yield", methods=["POST"])
def yield_endpoint():
    """Get yield prediction for a geometry."""
    try:
        data = request.get_json()
        geometry = ee.Geometry(data["geometry"])
        crop_type = data.get("crop_type", "default")
        
        # Get required data
        ndvi_result = get_ndvi(geometry)
        rainfall_result = get_rainfall_timeseries(geometry)
        
        ndvi_value = ndvi_result.get("ndvi", 0.3)
        rainfall_total = rainfall_result.get("statistics", {}).get("total_rainfall", 500)
        
        result = estimate_yield(ndvi_value, rainfall_total, crop_type)
        result["source_data"] = {
            "ndvi": ndvi_value,
            "rainfall_total": rainfall_total
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/drought", methods=["POST"])
def drought_endpoint():
    """Get drought index for a geometry."""
    try:
        data = request.get_json()
        geometry = ee.Geometry(data["geometry"])
        
        result = get_drought_index(geometry)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n🌾 Smart Farmer Geo Dashboard API")
    print("=" * 40)
    print("Starting server on http://localhost:5000")
    print("=" * 40 + "\n")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
