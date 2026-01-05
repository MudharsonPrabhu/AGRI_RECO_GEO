"""
Crop Catalog Module
Contains valid crops per state/season and metadata for validation.
Used as knowledge constraints for Gemini AI recommendations.
"""

# Valid crops by state and season for India
# These will be provided to Gemini as allowed crops
VALID_CROPS_BY_REGION = {
    "Tamil Nadu": {
        "kharif": ["rice", "cotton", "maize", "groundnut", "sugarcane", "turmeric", "chilli", "banana"],
        "rabi": ["maize", "groundnut", "sunflower", "sorghum", "pulses", "onion", "potato", "tomato"],
        "zaid": ["groundnut", "vegetables", "melons"]
    },
    "Karnataka": {
        "kharif": ["rice", "maize", "cotton", "groundnut", "soybean", "chilli", "turmeric"],
        "rabi": ["wheat", "maize", "groundnut", "pulses", "onion", "potato"],
        "zaid": ["vegetables", "melons", "groundnut"]
    },
    "Andhra Pradesh": {
        "kharif": ["rice", "cotton", "maize", "groundnut", "chilli", "turmeric"],
        "rabi": ["rice", "groundnut", "pulses", "tomato", "chilli", "onion"],
        "zaid": ["vegetables", "melons"]
    },
    "Telangana": {
        "kharif": ["rice", "cotton", "maize", "soybean", "chilli", "turmeric"],
        "rabi": ["maize", "groundnut", "pulses", "onion"],
        "zaid": ["vegetables"]
    },
    "Maharashtra": {
        "kharif": ["rice", "cotton", "soybean", "maize", "groundnut", "sugarcane"],
        "rabi": ["wheat", "pulses", "onion", "potato", "tomato"],
        "zaid": ["vegetables", "melons"]
    },
    "Gujarat": {
        "kharif": ["cotton", "groundnut", "maize", "rice", "sugarcane"],
        "rabi": ["wheat", "mustard", "potato", "onion", "pulses"],
        "zaid": ["vegetables", "melons"]
    },
    "Madhya Pradesh": {
        "kharif": ["soybean", "maize", "cotton", "rice", "groundnut"],
        "rabi": ["wheat", "pulses", "mustard", "potato", "onion"],
        "zaid": ["vegetables"]
    },
    "Uttar Pradesh": {
        "kharif": ["rice", "maize", "sugarcane", "cotton"],
        "rabi": ["wheat", "potato", "mustard", "pulses", "onion"],
        "zaid": ["vegetables", "melons"]
    },
    "Punjab": {
        "kharif": ["rice", "maize", "cotton", "sugarcane"],
        "rabi": ["wheat", "potato", "mustard", "pulses"],
        "zaid": ["vegetables", "melons"]
    },
    "Haryana": {
        "kharif": ["rice", "cotton", "maize", "sugarcane"],
        "rabi": ["wheat", "mustard", "potato", "pulses"],
        "zaid": ["vegetables"]
    },
    "Rajasthan": {
        "kharif": ["maize", "groundnut", "cotton", "soybean"],
        "rabi": ["wheat", "mustard", "pulses", "potato"],
        "zaid": ["vegetables"]
    },
    "West Bengal": {
        "kharif": ["rice", "maize", "jute"],
        "rabi": ["wheat", "potato", "pulses", "mustard"],
        "zaid": ["vegetables"]
    },
    "Bihar": {
        "kharif": ["rice", "maize", "sugarcane"],
        "rabi": ["wheat", "potato", "pulses", "onion"],
        "zaid": ["vegetables"]
    },
    "Odisha": {
        "kharif": ["rice", "maize", "groundnut", "turmeric"],
        "rabi": ["pulses", "groundnut", "potato"],
        "zaid": ["vegetables"]
    },
    # Default fallback for unknown regions
    "default": {
        "kharif": ["rice", "maize", "cotton", "groundnut", "soybean"],
        "rabi": ["wheat", "pulses", "mustard", "potato", "onion"],
        "zaid": ["vegetables", "melons"]
    }
}

# Crop metadata for validation - defines valid ranges
CROP_METADATA = {
    "rice": {
        "name": "Rice (Paddy)",
        "emoji": "🌾",
        "duration_range": (90, 180),  # days
        "yield_range": (2.5, 8.0),     # tons/ha
        "valid_water_needs": ["high", "very_high"],
        "seasons": ["kharif", "rabi"]
    },
    "wheat": {
        "name": "Wheat",
        "emoji": "🌾",
        "duration_range": (100, 150),
        "yield_range": (2.0, 6.0),
        "valid_water_needs": ["medium"],
        "seasons": ["rabi"]
    },
    "maize": {
        "name": "Maize (Corn)",
        "emoji": "🌽",
        "duration_range": (80, 130),
        "yield_range": (3.0, 10.0),
        "valid_water_needs": ["medium"],
        "seasons": ["kharif", "rabi"]
    },
    "cotton": {
        "name": "Cotton",
        "emoji": "☁️",
        "duration_range": (150, 200),
        "yield_range": (1.0, 3.0),
        "valid_water_needs": ["medium"],
        "seasons": ["kharif"]
    },
    "sugarcane": {
        "name": "Sugarcane",
        "emoji": "🎋",
        "duration_range": (270, 400),
        "yield_range": (50, 120),
        "valid_water_needs": ["high", "very_high"],
        "seasons": ["annual"]
    },
    "soybean": {
        "name": "Soybean",
        "emoji": "🫘",
        "duration_range": (80, 130),
        "yield_range": (1.5, 4.0),
        "valid_water_needs": ["medium"],
        "seasons": ["kharif"]
    },
    "groundnut": {
        "name": "Groundnut (Peanut)",
        "emoji": "🥜",
        "duration_range": (90, 150),
        "yield_range": (1.0, 3.5),
        "valid_water_needs": ["low", "medium"],
        "seasons": ["kharif", "rabi"]
    },
    "mustard": {
        "name": "Mustard",
        "emoji": "🌻",
        "duration_range": (80, 130),
        "yield_range": (0.8, 2.0),
        "valid_water_needs": ["low"],
        "seasons": ["rabi"]
    },
    "potato": {
        "name": "Potato",
        "emoji": "🥔",
        "duration_range": (70, 140),
        "yield_range": (15, 40),
        "valid_water_needs": ["medium"],
        "seasons": ["rabi"]
    },
    "onion": {
        "name": "Onion",
        "emoji": "🧅",
        "duration_range": (90, 160),
        "yield_range": (10, 30),
        "valid_water_needs": ["medium"],
        "seasons": ["rabi", "kharif"]
    },
    "tomato": {
        "name": "Tomato",
        "emoji": "🍅",
        "duration_range": (80, 140),
        "yield_range": (20, 50),
        "valid_water_needs": ["medium"],
        "seasons": ["rabi", "kharif"]
    },
    "chilli": {
        "name": "Chilli",
        "emoji": "🌶️",
        "duration_range": (100, 180),
        "yield_range": (1.5, 5.0),
        "valid_water_needs": ["medium"],
        "seasons": ["kharif", "rabi"]
    },
    "turmeric": {
        "name": "Turmeric",
        "emoji": "🧡",
        "duration_range": (200, 320),
        "yield_range": (15, 35),
        "valid_water_needs": ["medium", "high"],
        "seasons": ["kharif"]
    },
    "pulses": {
        "name": "Pulses (Lentils/Dal)",
        "emoji": "🫛",
        "duration_range": (80, 140),
        "yield_range": (0.8, 2.5),
        "valid_water_needs": ["low"],
        "seasons": ["rabi"]
    },
    "banana": {
        "name": "Banana",
        "emoji": "🍌",
        "duration_range": (270, 400),
        "yield_range": (40, 80),
        "valid_water_needs": ["high", "very_high"],
        "seasons": ["annual"]
    },
    "sunflower": {
        "name": "Sunflower",
        "emoji": "🌻",
        "duration_range": (80, 120),
        "yield_range": (1.0, 2.5),
        "valid_water_needs": ["low", "medium"],
        "seasons": ["rabi", "kharif"]
    },
    "sorghum": {
        "name": "Sorghum (Jowar)",
        "emoji": "🌾",
        "duration_range": (90, 130),
        "yield_range": (1.5, 4.0),
        "valid_water_needs": ["low"],
        "seasons": ["kharif", "rabi"]
    }
}

# Water need display mapping
WATER_NEED_DISPLAY = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "very_high": "Very High"
}

# Match level thresholds based on confidence
MATCH_LEVEL_THRESHOLDS = {
    "Excellent": 0.75,
    "Good": 0.50,
    "Moderate": 0.25
}


def get_allowed_crops(state: str, season: str) -> list:
    """Get list of allowed crops for a state and season."""
    region_crops = VALID_CROPS_BY_REGION.get(state, VALID_CROPS_BY_REGION["default"])
    return region_crops.get(season, region_crops.get("kharif", []))


def get_crop_metadata(crop_id: str) -> dict:
    """Get metadata for a specific crop."""
    return CROP_METADATA.get(crop_id, None)


def validate_crop_name(crop_name: str) -> tuple:
    """
    Validate and normalize a crop name.
    Returns (is_valid, crop_id, display_name)
    """
    crop_name_lower = crop_name.lower().strip()
    
    # Direct match
    if crop_name_lower in CROP_METADATA:
        meta = CROP_METADATA[crop_name_lower]
        return True, crop_name_lower, meta["name"]
    
    # Check display names
    for crop_id, meta in CROP_METADATA.items():
        if crop_name_lower in meta["name"].lower():
            return True, crop_id, meta["name"]
    
    return False, None, None


def validate_duration(crop_id: str, duration_str: str) -> bool:
    """Validate if duration is within valid range for the crop."""
    meta = CROP_METADATA.get(crop_id)
    if not meta:
        return True  # Can't validate unknown crop
    
    try:
        # Parse "90-120" format
        parts = duration_str.replace(" ", "").split("-")
        if len(parts) == 2:
            min_dur, max_dur = int(parts[0]), int(parts[1])
        else:
            min_dur = max_dur = int(parts[0])
        
        valid_min, valid_max = meta["duration_range"]
        return valid_min <= min_dur and max_dur <= valid_max + 30  # 30 day buffer
    except:
        return False


def validate_yield(crop_id: str, yield_str: str) -> bool:
    """Validate if yield is within valid range for the crop."""
    meta = CROP_METADATA.get(crop_id)
    if not meta:
        return True  # Can't validate unknown crop
    
    try:
        # Parse "3-5 tons/ha" format
        yield_part = yield_str.lower().replace("tons/ha", "").replace("ton/ha", "").strip()
        parts = yield_part.split("-")
        if len(parts) == 2:
            min_yield, max_yield = float(parts[0]), float(parts[1])
        else:
            min_yield = max_yield = float(parts[0])
        
        valid_min, valid_max = meta["yield_range"]
        # Allow 50% buffer for yield variations
        return valid_min * 0.5 <= min_yield and max_yield <= valid_max * 1.5
    except:
        return False
