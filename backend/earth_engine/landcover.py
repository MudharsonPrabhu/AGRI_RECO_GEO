"""
Land Cover Classification Module
Uses ESA WorldCover dataset to classify land cover types
Dataset: ESA/WorldCover/v200
"""

import ee


# ESA WorldCover class definitions
LANDCOVER_CLASSES = {
    10: "Tree Cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / Sparse Vegetation",
    70: "Snow and Ice",
    80: "Permanent Water Bodies",
    90: "Herbaceous Wetland",
    95: "Mangroves",
    100: "Moss and Lichen"
}


def get_landcover_stats(geometry):
    """
    Get land cover classification statistics for a given geometry.
    
    Args:
        geometry: ee.Geometry object representing the area of interest
    
    Returns:
        dict: Land cover class percentages and raw counts
    """
    try:
        # Load ESA WorldCover 2021 (v200)
        # Fallback to v100 (2020) if v200 not available
        try:
            lc = ee.Image("ESA/WorldCover/v200/2021")
        except:
            lc = ee.Image("ESA/WorldCover/v100/2020")
        
        # Get frequency histogram of land cover classes
        stats = lc.reduceRegion(
            reducer=ee.Reducer.frequencyHistogram(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        )
        
        # Get the histogram
        histogram = stats.get("Map").getInfo()
        
        if histogram is None:
            return {
                "raw": {},
                "percentages": {},
                "dominant_class": None,
                "error": "No land cover data found for this area"
            }
        
        # Convert string keys to integers
        raw_counts = {int(k): v for k, v in histogram.items()}
        
        # Calculate total pixels
        total_pixels = sum(raw_counts.values())
        
        # Calculate percentages
        percentages = {}
        for class_code, count in raw_counts.items():
            class_name = LANDCOVER_CLASSES.get(class_code, f"Class {class_code}")
            percentages[class_name] = round((count / total_pixels) * 100, 2) if total_pixels > 0 else 0
        
        # Find dominant class
        if raw_counts:
            dominant_code = max(raw_counts, key=raw_counts.get)
            dominant_class = LANDCOVER_CLASSES.get(dominant_code, f"Class {dominant_code}")
        else:
            dominant_class = None
        
        # Calculate agricultural potential
        cropland_percent = raw_counts.get(40, 0) / total_pixels * 100 if total_pixels > 0 else 0
        
        return {
            "raw": raw_counts,
            "percentages": percentages,
            "dominant_class": dominant_class,
            "cropland_percent": round(cropland_percent, 2),
            "total_pixels": total_pixels
        }
        
    except Exception as e:
        return {
            "raw": {},
            "percentages": {},
            "dominant_class": None,
            "error": str(e)
        }


def get_landcover_area(geometry):
    """
    Calculate actual area in hectares for each land cover class.
    
    Args:
        geometry: ee.Geometry object
    
    Returns:
        dict: Area in hectares for each land cover class
    """
    try:
        lc = ee.Image("ESA/WorldCover/v200/2021")
        
        # Calculate pixel area
        pixel_area = ee.Image.pixelArea()
        
        areas = {}
        for class_code, class_name in LANDCOVER_CLASSES.items():
            # Create mask for this class
            mask = lc.eq(class_code)
            
            # Calculate area
            area = pixel_area.updateMask(mask).reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            )
            
            # Convert to hectares
            area_m2 = area.get('area').getInfo()
            if area_m2:
                areas[class_name] = round(area_m2 / 10000, 2)  # Convert m² to hectares
        
        # Calculate total area
        total_area = sum(areas.values())
        
        return {
            "areas_hectares": areas,
            "total_hectares": round(total_area, 2)
        }
        
    except Exception as e:
        return {
            "areas_hectares": {},
            "total_hectares": 0,
            "error": str(e)
        }
