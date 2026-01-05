import { useState, useCallback, useRef } from 'react';
import { GoogleMap, useJsApiLoader, DrawingManager, Marker, Polygon, Circle } from '@react-google-maps/api';
import axios from 'axios';
import './App.css';
import ResultsPanel from './components/ResultsPanel';
import RainfallChart from './components/RainfallChart';

const libraries = ['drawing', 'places', 'geometry'];

const mapContainerStyle = {
  width: '100%',
  height: '100%',
};

const defaultCenter = {
  lat: 20.5937,
  lng: 78.9629,
};

const mapOptions = {
  disableDefaultUI: false,
  zoomControl: true,
  streetViewControl: false,
  mapTypeControl: true,
  mapTypeId: 'hybrid',
  styles: [
    {
      featureType: 'all',
      elementType: 'labels.text.fill',
      stylers: [{ color: '#ffffff' }],
    },
  ],
};

// Preset radius options in meters
const RADIUS_OPTIONS = [
  { label: 'Small (100m)', value: 100 },
  { label: 'Medium (250m)', value: 250 },
  { label: 'Large (500m)', value: 500 },
  { label: 'XL (1km)', value: 1000 },
  { label: 'Custom', value: 'custom' },
];

function App() {
  const [userLocation, setUserLocation] = useState(null);
  const [mapCenter, setMapCenter] = useState(defaultCenter);
  const [mapRef, setMapRef] = useState(null);
  const [polygon, setPolygon] = useState(null);
  const [polygonPath, setPolygonPath] = useState([]);
  const [circleCenter, setCircleCenter] = useState(null);
  const [circleRadius, setCircleRadius] = useState(250);
  const [drawMode, setDrawMode] = useState(null); // null, 'circle', 'polygon'
  const [showDrawOptions, setShowDrawOptions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [error, setError] = useState(null);

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries,
  });

  const handleEnableLocation = useCallback(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setUserLocation(location);
          setMapCenter(location);
        },
        (err) => {
          console.error('Error getting location:', err);
          setError('Unable to get your location. Please enable location services.');
        },
        { enableHighAccuracy: true }
      );
    } else {
      setError('Geolocation is not supported by your browser.');
    }
  }, []);

  // Generate polygon points from circle
  const circleToPolygon = useCallback((center, radius, numPoints = 32) => {
    const points = [];
    for (let i = 0; i < numPoints; i++) {
      const angle = (i / numPoints) * 2 * Math.PI;
      const lat = center.lat + (radius / 111320) * Math.cos(angle);
      const lng = center.lng + (radius / (111320 * Math.cos(center.lat * Math.PI / 180))) * Math.sin(angle);
      points.push({ lat, lng });
    }
    return points;
  }, []);

  // Quick circle selection - click on map to place
  const handleMapClick = useCallback((e) => {
    if (drawMode === 'circle') {
      const clickedLocation = {
        lat: e.latLng.lat(),
        lng: e.latLng.lng(),
      };
      setCircleCenter(clickedLocation);
      const polygonPoints = circleToPolygon(clickedLocation, circleRadius);
      setPolygonPath(polygonPoints);
      setDrawMode(null);
      setShowDrawOptions(false);
    }
  }, [drawMode, circleRadius, circleToPolygon]);

  // Use current location as center
  const handleUseMyLocation = useCallback(() => {
    if (userLocation) {
      setCircleCenter(userLocation);
      const polygonPoints = circleToPolygon(userLocation, circleRadius);
      setPolygonPath(polygonPoints);
      setDrawMode(null);
      setShowDrawOptions(false);
    } else {
      setError('Please enable location first by clicking "Enable Location"');
    }
  }, [userLocation, circleRadius, circleToPolygon]);

  const handlePolygonComplete = useCallback((poly) => {
    setPolygon(poly);
    const path = poly.getPath().getArray().map((latLng) => ({
      lat: latLng.lat(),
      lng: latLng.lng(),
    }));
    setPolygonPath(path);
    setDrawMode(null);
    setShowDrawOptions(false);
  }, []);

  // Cancel drawing and restore default UI
  const handleCancelDrawing = useCallback(() => {
    if (polygon) {
      polygon.setMap(null);
      setPolygon(null);
    }
    setDrawMode(null);
    setShowDrawOptions(false);
  }, [polygon]);

  const handleClearBoundary = useCallback(() => {
    if (polygon) {
      polygon.setMap(null);
    }
    setPolygon(null);
    setPolygonPath([]);
    setCircleCenter(null);
    setAnalysisResults(null);
    setDrawMode(null);
  }, [polygon]);

  const handleAnalyze = useCallback(async () => {
    if (polygonPath.length < 3) {
      setError('Please select a farm area first.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const coordinates = polygonPath.map((point) => [point.lng, point.lat]);
      coordinates.push(coordinates[0]);

      const geometry = {
        type: 'Polygon',
        coordinates: [coordinates],
      };

      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/analyze`,
        { geometry },
        { timeout: 120000 }
      );

      setAnalysisResults(response.data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.error || 'Failed to analyze the area. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [polygonPath]);

  if (loadError) {
    return (
      <div className="app">
        <div className="loading-overlay">
          <div className="empty-icon">⚠️</div>
          <div className="loading-text">Error loading Google Maps</div>
        </div>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div className="app">
        <div className="loading-overlay">
          <div className="loader"></div>
          <div className="loading-text">Loading map...</div>
        </div>
      </div>
    );
  }

  const hasBoundary = polygonPath.length > 0 || polygon;

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="logo">
          <div className="logo-icon">🌾</div>
          <span className="logo-text">Smart Farmer Geo Dashboard</span>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={handleEnableLocation}>
            📍 Enable Location
          </button>
        </div>
      </header>

      {/* Main Container */}
      <div className="main-container">
        {/* Map Panel */}
        <div className="map-panel">
          <GoogleMap
            mapContainerStyle={mapContainerStyle}
            center={mapCenter}
            zoom={userLocation ? 16 : 5}
            options={mapOptions}
            onClick={handleMapClick}
            onLoad={(map) => setMapRef(map)}
          >
            {/* User Location Marker */}
            {userLocation && (
              <Marker
                position={userLocation}
                icon={{
                  path: window.google.maps.SymbolPath.CIRCLE,
                  scale: 10,
                  fillColor: '#3b82f6',
                  fillOpacity: 1,
                  strokeColor: '#ffffff',
                  strokeWeight: 3,
                }}
              />
            )}

            {/* Drawing Manager for Polygon */}
            {drawMode === 'polygon' && (
              <DrawingManager
                drawingMode={window.google.maps.drawing.OverlayType.POLYGON}
                options={{
                  drawingControl: false,
                  polygonOptions: {
                    fillColor: '#10b981',
                    fillOpacity: 0.3,
                    strokeColor: '#10b981',
                    strokeWeight: 2,
                    clickable: true,
                    editable: true,
                    draggable: true,
                  },
                }}
                onPolygonComplete={handlePolygonComplete}
              />
            )}

            {/* Display Circle */}
            {circleCenter && (
              <Circle
                center={circleCenter}
                radius={circleRadius}
                options={{
                  fillColor: '#10b981',
                  fillOpacity: 0.3,
                  strokeColor: '#10b981',
                  strokeWeight: 2,
                }}
              />
            )}

            {/* Display Polygon (for manual drawing) */}
            {polygon === null && polygonPath.length > 0 && !circleCenter && (
              <Polygon
                paths={polygonPath}
                options={{
                  fillColor: '#10b981',
                  fillOpacity: 0.3,
                  strokeColor: '#10b981',
                  strokeWeight: 2,
                }}
              />
            )}
          </GoogleMap>

          {/* Draw Options Panel - hidden when drawing mode is active */}
          {showDrawOptions && !hasBoundary && !drawMode && (
            <div className="draw-options-panel">
              <div className="draw-options-header">
                <h3>📍 Select Farm Area</h3>
                <button className="close-btn" onClick={() => setShowDrawOptions(false)}>×</button>
              </div>

              <div className="draw-option-section">
                <h4>🎯 Quick Select (Recommended)</h4>
                <p className="option-description">Choose a radius and click on the map to select your farm area</p>

                <div className="radius-buttons">
                  {RADIUS_OPTIONS.filter(r => r.value !== 'custom').map((option) => (
                    <button
                      key={option.value}
                      className={`radius-btn ${circleRadius === option.value ? 'active' : ''}`}
                      onClick={() => setCircleRadius(option.value)}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>

                <div className="quick-actions">
                  <button
                    className="btn btn-primary"
                    onClick={() => setDrawMode('circle')}
                  >
                    👆 Click on Map to Place
                  </button>
                  {userLocation && (
                    <button
                      className="btn btn-secondary"
                      onClick={handleUseMyLocation}
                    >
                      📍 Use My Location
                    </button>
                  )}
                </div>
              </div>

              <div className="draw-option-divider">
                <span>OR</span>
              </div>

              <div className="draw-option-section">
                <h4>✏️ Draw Custom Shape</h4>
                <p className="option-description">Click points on the map to draw a custom boundary</p>
                <button
                  className="btn btn-secondary full-width"
                  onClick={() => setDrawMode('polygon')}
                >
                  ✏️ Start Drawing Polygon
                </button>
              </div>
            </div>
          )}

          {/* Drawing Instructions - Circle Mode */}
          {drawMode === 'circle' && (
            <div className="drawing-instructions">
              <div className="instruction-icon">👆</div>
              <div className="instruction-text">
                <strong>Click anywhere on the map</strong> to place your farm area
                <br />
                <span className="instruction-sub">Radius: {circleRadius >= 1000 ? `${circleRadius / 1000}km` : `${circleRadius}m`}</span>
              </div>
              <button className="btn btn-danger btn-sm" onClick={handleCancelDrawing}>✕ Cancel</button>
            </div>
          )}

          {/* Drawing Instructions - Polygon Mode */}
          {drawMode === 'polygon' && (
            <div className="drawing-instructions">
              <div className="instruction-icon">✏️</div>
              <div className="instruction-text">
                <strong>Click points on the map</strong> to draw your boundary
                <br />
                <span className="instruction-sub">Click the first point again to close the shape</span>
              </div>
              <button className="btn btn-danger btn-sm" onClick={handleCancelDrawing}>✕ Cancel</button>
            </div>
          )}

          {/* Map Controls */}
          <div className="map-controls">
            {!hasBoundary && !drawMode && (
              <button className="btn btn-primary btn-large" onClick={() => setShowDrawOptions(true)}>
                🗺️ Select Farm Area
              </button>
            )}
            {hasBoundary && !drawMode && (
              <>
                <button
                  className="btn btn-primary btn-large"
                  onClick={handleAnalyze}
                  disabled={isLoading}
                >
                  {isLoading ? '⏳ Analyzing...' : '🔍 Analyze Farm'}
                </button>
                <button className="btn btn-danger" onClick={handleClearBoundary}>
                  🗑️ Clear Selection
                </button>
              </>
            )}
          </div>

          {/* Location Info */}
          {userLocation && (
            <div className="location-info">
              📍 Your location: <span>{userLocation.lat.toFixed(4)}, {userLocation.lng.toFixed(4)}</span>
            </div>
          )}
        </div>

        {/* Results Panel */}
        <ResultsPanel
          results={analysisResults}
          isLoading={isLoading}
          error={error}
          onClearError={() => setError(null)}
        />
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loader"></div>
          <div className="loading-text">Analyzing satellite imagery...</div>
          <div className="loading-text" style={{ fontSize: '0.85rem', opacity: 0.7 }}>
            This may take up to 2 minutes
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
