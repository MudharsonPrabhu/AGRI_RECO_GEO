"""
Rainfall Trends Module
Uses CHIRPS daily precipitation data to analyze rainfall patterns
Dataset: UCSB-CHG/CHIRPS/DAILY
"""

import ee
from datetime import datetime, timedelta


def get_rainfall_timeseries(geometry, start_date=None, end_date=None):
    """
    Get daily rainfall time series for a given geometry using CHIRPS data.
    
    Args:
        geometry: ee.Geometry object representing the area of interest
        start_date: Start date string (YYYY-MM-DD), defaults to 90 days ago
        end_date: End date string (YYYY-MM-DD), defaults to today
    
    Returns:
        dict: Contains rainfall time series and statistics
    """
    # Set default date range (last 90 days)
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    try:
        # Load CHIRPS daily precipitation data
        chirps = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
                  .filterBounds(geometry)
                  .filterDate(start_date, end_date))
        
        # Check if we have data
        image_count = chirps.size().getInfo()
        if image_count == 0:
            return {
                "features": [],
                "statistics": {},
                "error": "No rainfall data found for this area and time period"
            }
        
        def daily_rain(img):
            """Extract mean daily rainfall for the geometry."""
            rain = img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=5000,
                maxPixels=1e9
            )
            return ee.Feature(None, {
                "date": img.date().format('YYYY-MM-dd'),
                "rain": rain.get("precipitation")
            })
        
        # Map over collection to get daily values
        features = chirps.map(daily_rain)
        result = features.getInfo()
        
        # Process results
        rainfall_data = []
        total_rain = 0
        rain_days = 0
        
        for f in result['features']:
            rain_value = f['properties']['rain']
            if rain_value is not None:
                rainfall_data.append({
                    'date': f['properties']['date'],
                    'rain': round(rain_value, 2)
                })
                total_rain += rain_value
                if rain_value > 0.1:  # Count as rain day if > 0.1mm
                    rain_days += 1
        
        # Calculate statistics
        num_days = len(rainfall_data)
        avg_daily = total_rain / num_days if num_days > 0 else 0
        
        return {
            "features": rainfall_data,
            "statistics": {
                "total_rainfall": round(total_rain, 2),
                "average_daily": round(avg_daily, 2),
                "rain_days": rain_days,
                "dry_days": num_days - rain_days,
                "data_days": num_days
            }
        }
        
    except Exception as e:
        return {
            "features": [],
            "statistics": {},
            "error": str(e)
        }


def get_drought_index(geometry, start_date=None, end_date=None):
    """
    Calculate drought index based on precipitation deviation from normal.
    
    Args:
        geometry: ee.Geometry object
        start_date: Start date string
        end_date: End date string
    
    Returns:
        dict: Drought status and index
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        # Get current period rainfall
        chirps = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
                  .filterBounds(geometry)
                  .filterDate(start_date, end_date))
        
        total_precip = chirps.sum().reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=5000,
            maxPixels=1e9
        ).get('precipitation').getInfo()
        
        # Calculate expected normal (approximate)
        # Average monthly rainfall in India is around 100-200mm during monsoon
        expected_monthly = 100  # mm
        days = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
        expected = expected_monthly * (days / 30)
        
        # Calculate deviation
        if expected > 0:
            deviation = ((total_precip or 0) - expected) / expected * 100
        else:
            deviation = 0
        
        # Determine drought status
        if deviation >= -10:
            status = "Normal"
            severity = 0
        elif deviation >= -25:
            status = "Mild Drought"
            severity = 1
        elif deviation >= -50:
            status = "Moderate Drought"
            severity = 2
        elif deviation >= -75:
            status = "Severe Drought"
            severity = 3
        else:
            status = "Extreme Drought"
            severity = 4
        
        return {
            "status": status,
            "severity": severity,
            "precipitation_mm": round(total_precip or 0, 2),
            "deviation_percent": round(deviation, 2)
        }
        
    except Exception as e:
        return {
            "status": "Unknown",
            "severity": -1,
            "error": str(e)
        }
