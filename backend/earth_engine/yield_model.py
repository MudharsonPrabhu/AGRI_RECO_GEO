"""
Yield Prediction Module
Estimates crop yield based on NDVI, rainfall, and environmental factors
"""

import ee
from datetime import datetime, timedelta


# Crop coefficients (approximate values for common crops)
CROP_COEFFICIENTS = {
    "rice": 1.2,
    "wheat": 1.0,
    "maize": 1.1,
    "soybean": 0.9,
    "cotton": 0.85,
    "sugarcane": 1.3,
    "default": 1.0
}


def estimate_yield(ndvi_value, rainfall_total, crop_type="default"):
    """
    Estimate crop yield using a simple empirical model.
    
    Formula: Yield = Base_Yield × NDVI_Factor × Rainfall_Factor × Crop_Coefficient
    
    Args:
        ndvi_value: Mean NDVI value (0-1)
        rainfall_total: Total rainfall in mm
        crop_type: Type of crop for coefficient adjustment
    
    Returns:
        dict: Yield prediction in tons/hectare
    """
    try:
        # Validate inputs
        if ndvi_value is None or ndvi_value < 0:
            ndvi_value = 0.3  # Default moderate value
        
        if rainfall_total is None or rainfall_total < 0:
            rainfall_total = 500  # Default moderate rainfall
        
        # Base yield (tons/hectare) - calibrated for Indian agriculture
        base_yield = 3.0
        
        # NDVI factor (healthy vegetation = higher yield)
        # NDVI < 0.2 = very poor, > 0.6 = excellent
        if ndvi_value < 0.2:
            ndvi_factor = 0.4
        elif ndvi_value < 0.4:
            ndvi_factor = 0.7
        elif ndvi_value < 0.6:
            ndvi_factor = 1.0
        else:
            ndvi_factor = 1.2
        
        # Rainfall factor (optimal range varies by crop)
        # Using general optimal range of 500-1000mm
        if rainfall_total < 200:
            rainfall_factor = 0.5  # Severe drought conditions
        elif rainfall_total < 400:
            rainfall_factor = 0.75
        elif rainfall_total < 800:
            rainfall_factor = 1.0
        elif rainfall_total < 1200:
            rainfall_factor = 1.1
        else:
            rainfall_factor = 0.9  # Too much rain can reduce yield
        
        # Get crop coefficient
        crop_coeff = CROP_COEFFICIENTS.get(crop_type.lower(), CROP_COEFFICIENTS["default"])
        
        # Calculate final yield estimate
        estimated_yield = base_yield * ndvi_factor * rainfall_factor * crop_coeff
        
        # Add variability range (±15%)
        yield_min = estimated_yield * 0.85
        yield_max = estimated_yield * 1.15
        
        return {
            "yield_prediction": round(estimated_yield, 2),
            "yield_range": {
                "min": round(yield_min, 2),
                "max": round(yield_max, 2)
            },
            "factors": {
                "ndvi_factor": round(ndvi_factor, 2),
                "rainfall_factor": round(rainfall_factor, 2),
                "crop_coefficient": crop_coeff
            },
            "unit": "tons/hectare",
            "confidence": "medium"
        }
        
    except Exception as e:
        return {
            "yield_prediction": 0,
            "error": str(e)
        }


def get_yield_prediction(geometry, crop_type="default"):
    """
    Full yield prediction pipeline using Earth Engine data.
    
    Args:
        geometry: ee.Geometry object
        crop_type: Type of crop
    
    Returns:
        dict: Complete yield prediction with all factors
    """
    from earth_engine.ndvi import get_ndvi
    from earth_engine.rainfall import get_rainfall_timeseries
    
    try:
        # Get NDVI
        ndvi_result = get_ndvi(geometry)
        ndvi_value = ndvi_result.get("ndvi", 0.3)
        
        # Get rainfall (last 6 months)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
        rainfall_result = get_rainfall_timeseries(geometry, start_date, end_date)
        rainfall_total = rainfall_result.get("statistics", {}).get("total_rainfall", 500)
        
        # Estimate yield
        yield_result = estimate_yield(ndvi_value, rainfall_total, crop_type)
        
        # Add source data to result
        yield_result["source_data"] = {
            "ndvi": ndvi_value,
            "rainfall_total_mm": rainfall_total,
            "analysis_period": f"{start_date} to {end_date}"
        }
        
        return yield_result
        
    except Exception as e:
        return {
            "yield_prediction": 0,
            "error": str(e)
        }


def get_historical_productivity(geometry, years=5):
    """
    Analyze historical productivity trends using MODIS data.
    
    Args:
        geometry: ee.Geometry object
        years: Number of years to analyze
    
    Returns:
        dict: Historical NDVI trends as productivity proxy
    """
    try:
        results = []
        current_year = datetime.now().year
        
        for i in range(years):
            year = current_year - i
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            # Use MODIS for historical data (available since 2000)
            modis = (ee.ImageCollection("MODIS/006/MOD13Q1")
                     .filterBounds(geometry)
                     .filterDate(start_date, end_date)
                     .select("NDVI"))
            
            # Get annual mean NDVI
            annual_ndvi = modis.mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=250,
                maxPixels=1e9
            )
            
            ndvi_value = annual_ndvi.get("NDVI").getInfo()
            if ndvi_value:
                # MODIS NDVI is scaled by 10000
                ndvi_value = ndvi_value / 10000
            
            results.append({
                "year": year,
                "ndvi": round(ndvi_value, 3) if ndvi_value else None
            })
        
        return {
            "historical_data": results,
            "trend": "stable" if len(results) > 1 else "insufficient_data"
        }
        
    except Exception as e:
        return {
            "historical_data": [],
            "error": str(e)
        }
