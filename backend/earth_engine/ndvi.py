"""
NDVI Calculation Module
Uses Sentinel-2 imagery to calculate Normalized Difference Vegetation Index
NDVI = (NIR - RED) / (NIR + RED)
Sentinel-2 bands: RED = B4, NIR = B8
"""

import ee
from datetime import datetime, timedelta


def get_ndvi(geometry, start_date=None, end_date=None):
    """
    Calculate mean NDVI for a given geometry using Sentinel-2 imagery.
    
    Args:
        geometry: ee.Geometry object representing the area of interest
        start_date: Start date string (YYYY-MM-DD), defaults to 6 months ago
        end_date: End date string (YYYY-MM-DD), defaults to today
    
    Returns:
        dict: Contains mean NDVI value and tile URL for visualization
    """
    # Set default date range (last 6 months)
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    
    try:
        # Load Sentinel-2 Surface Reflectance imagery
        s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(geometry)
              .filterDate(start_date, end_date)
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
              .select(['B4', 'B8']))  # RED and NIR bands
        
        # Check if we have any images
        image_count = s2.size().getInfo()
        if image_count == 0:
            return {
                "ndvi": 0,
                "tile_url": None,
                "image_count": 0,
                "error": "No cloud-free images found for this area and time period"
            }
        
        # Create median composite
        composite = s2.median()
        
        # Calculate NDVI
        ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
        # Calculate mean NDVI for the region
        mean_ndvi = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        )
        
        ndvi_value = mean_ndvi.get('NDVI').getInfo()
        
        # Generate visualization tile URL
        vis_params = {
            'min': -0.2,
            'max': 0.8,
            'palette': ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850']
        }
        
        map_id = ndvi.clip(geometry).getMapId(vis_params)
        tile_url = map_id['tile_fetcher'].url_format
        
        return {
            "ndvi": ndvi_value if ndvi_value is not None else 0,
            "tile_url": tile_url,
            "image_count": image_count,
            "date_range": f"{start_date} to {end_date}"
        }
        
    except Exception as e:
        return {
            "ndvi": 0,
            "tile_url": None,
            "image_count": 0,
            "error": str(e)
        }


def get_ndvi_timeseries(geometry, start_date=None, end_date=None):
    """
    Get NDVI time series for a given geometry.
    
    Args:
        geometry: ee.Geometry object
        start_date: Start date string
        end_date: End date string
    
    Returns:
        list: Time series of NDVI values with dates
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    try:
        s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(geometry)
              .filterDate(start_date, end_date)
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)))
        
        def calculate_ndvi(image):
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            mean = ndvi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            )
            return ee.Feature(None, {
                'date': image.date().format('YYYY-MM-dd'),
                'ndvi': mean.get('NDVI')
            })
        
        features = s2.map(calculate_ndvi)
        result = features.getInfo()
        
        return [
            {'date': f['properties']['date'], 'ndvi': f['properties']['ndvi']}
            for f in result['features']
            if f['properties']['ndvi'] is not None
        ]
        
    except Exception as e:
        return {"error": str(e)}
