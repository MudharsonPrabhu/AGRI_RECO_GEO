import RainfallChart from './RainfallChart';
import CropRecommendations from './CropRecommendations';
import WeatherCard from './WeatherCard';
import PollenCard from './PollenCard';
import SolarCard from './SolarCard';

const LANDCOVER_CLASSES = {
  10: { name: 'Tree Cover', color: '#22c55e', class: 'forest' },
  20: { name: 'Shrubland', color: '#84cc16', class: 'forest' },
  30: { name: 'Grassland', color: '#a3e635', class: 'forest' },
  40: { name: 'Cropland', color: '#10b981', class: 'cropland' },
  50: { name: 'Built-up', color: '#64748b', class: 'urban' },
  60: { name: 'Bare/Sparse', color: '#d4a574', class: 'urban' },
  70: { name: 'Snow/Ice', color: '#e0f2fe', class: 'water' },
  80: { name: 'Water', color: '#3b82f6', class: 'water' },
  90: { name: 'Wetland', color: '#06b6d4', class: 'water' },
  95: { name: 'Mangroves', color: '#059669', class: 'forest' },
  100: { name: 'Moss/Lichen', color: '#65a30d', class: 'forest' },
};

function getNDVIStatus(ndvi) {
  if (ndvi >= 0.6) return { status: 'Excellent', class: 'ndvi-healthy', emoji: '🌿' };
  if (ndvi >= 0.4) return { status: 'Good', class: 'ndvi-healthy', emoji: '🌱' };
  if (ndvi >= 0.2) return { status: 'Moderate', class: 'ndvi-moderate', emoji: '🌾' };
  return { status: 'Poor', class: 'ndvi-poor', emoji: '🏜️' };
}

function getDroughtStatus(rainfall, droughtData) {
  // Use drought data from backend if available
  if (droughtData && droughtData.status) {
    const status = droughtData.status;
    if (status === 'Normal') return { status: 'No Drought', class: 'status-healthy', emoji: '💧' };
    if (status === 'Mild Drought') return { status: 'Mild Drought', class: 'status-warning', emoji: '⚠️' };
    if (status === 'Moderate Drought') return { status: 'Moderate', class: 'status-warning', emoji: '⚠️' };
    return { status: status, class: 'status-critical', emoji: '🔥' };
  }
  
  if (!rainfall || rainfall.length === 0) return { status: 'Unknown', class: 'status-warning', emoji: '❓' };
  
  const avgRain = rainfall.reduce((sum, d) => sum + (d.rain || 0), 0) / rainfall.length;
  if (avgRain >= 5) return { status: 'No Drought', class: 'status-healthy', emoji: '💧' };
  if (avgRain >= 2) return { status: 'Mild Drought', class: 'status-warning', emoji: '⚠️' };
  return { status: 'Severe Drought', class: 'status-critical', emoji: '🔥' };
}

function ResultsPanel({ results, isLoading, error, onClearError }) {
  if (error) {
    return (
      <div className="results-panel">
        <div className="panel-header">
          <h2 className="panel-title">Analysis Results</h2>
        </div>
        <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '16px' }}>⚠️</div>
          <h3 style={{ color: 'var(--danger)', marginBottom: '8px' }}>Error</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>{error}</p>
          <button className="btn btn-secondary" onClick={onClearError}>
            Dismiss
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="results-panel">
        <div className="panel-header">
          <h2 className="panel-title">Analysis Results</h2>
        </div>
        <div className="empty-state">
          <div className="empty-icon">🗺️</div>
          <h3 className="empty-title">No Analysis Yet</h3>
          <p className="empty-text">
            Select a farm area on the map and click "Analyze Farm" to get crop recommendations and insights.
          </p>
        </div>
      </div>
    );
  }

  const ndviValue = results.ndvi || 0;
  const ndviStatus = getNDVIStatus(ndviValue);
  const rainfallData = results.rainfall?.features || [];
  const rainfallStats = results.rainfall?.statistics || {};
  const droughtData = results.drought || {};
  const droughtStatus = getDroughtStatus(rainfallData, droughtData);
  const landcover = results.landcover || {};
  const yieldPrediction = results.yield_prediction || 0;
  const cropRecommendations = results.crop_recommendations || null;
  const weatherData = results.weather || null;
  const pollenData = results.pollen || null;
  const solarData = results.solar || null;

  // Process landcover data
  const totalPixels = Object.values(landcover).reduce((sum, val) => sum + val, 0);
  const landcoverStats = Object.entries(landcover)
    .map(([code, count]) => ({
      code: parseInt(code),
      name: LANDCOVER_CLASSES[code]?.name || `Class ${code}`,
      color: LANDCOVER_CLASSES[code]?.color || '#64748b',
      cssClass: LANDCOVER_CLASSES[code]?.class || 'urban',
      percent: totalPixels > 0 ? ((count / totalPixels) * 100).toFixed(1) : 0,
    }))
    .sort((a, b) => b.percent - a.percent)
    .slice(0, 5);

  // Calculate gauge needle rotation (-90 to 90 degrees based on NDVI 0-1)
  const needleRotation = (ndviValue * 180) - 90;

  return (
    <div className="results-panel">
      <div className="panel-header">
        <h2 className="panel-title">📊 Analysis Results</h2>
        <span className={`status-badge ${ndviStatus.class === 'ndvi-healthy' ? 'status-healthy' : ndviStatus.class === 'ndvi-moderate' ? 'status-warning' : 'status-critical'}`}>
          {ndviStatus.emoji} {ndviStatus.status}
        </span>
      </div>

      {/* Crop Recommendations - Show first! */}
      {cropRecommendations && (
        <CropRecommendations recommendations={cropRecommendations} />
      )}

      {/* NDVI Gauge */}
      <div className="glass-card ndvi-gauge">
        <h3 style={{ marginBottom: '16px', textAlign: 'center' }}>🌿 Crop Health (NDVI)</h3>
        <div className="gauge-container">
          <div className="gauge-visual">
            <div className="gauge-arc"></div>
            <div 
              className="gauge-needle" 
              style={{ transform: `translateX(-50%) rotate(${needleRotation}deg)` }}
            ></div>
          </div>
          <div className={`gauge-value ${ndviStatus.class}`} style={{ marginTop: '-10px' }}>
            {ndviValue.toFixed(3)}
          </div>
          <div className="gauge-label">{ndviStatus.status} Vegetation</div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="analysis-grid">
        <div className="glass-card analysis-card">
          <div className="icon">{droughtStatus.emoji}</div>
          <div className="value" style={{ fontSize: '1rem' }}>{droughtStatus.status}</div>
          <div className="label">Drought Status</div>
        </div>
        <div className="glass-card analysis-card">
          <div className="icon">🌧️</div>
          <div className="value">
            {rainfallStats.total_rainfall 
              ? rainfallStats.total_rainfall.toFixed(1)
              : rainfallData.length > 0 
                ? (rainfallData.reduce((sum, d) => sum + (d.rain || 0), 0)).toFixed(1)
                : 'N/A'
            }
          </div>
          <div className="label">Total Rain (mm)</div>
        </div>
      </div>

      {/* Yield Prediction */}
      <div className="glass-card yield-card">
        <h3 style={{ marginBottom: '16px' }}>🌾 Yield Prediction</h3>
        <div className="yield-value">{yieldPrediction.toFixed(2)}</div>
        <div className="yield-unit">tons/hectare</div>
        <div className="yield-label">Estimated Annual Yield</div>
      </div>

      {/* Land Cover Stats */}
      {landcoverStats.length > 0 && (
        <div className="glass-card landcover-card">
          <h3>🗺️ Land Cover Classification</h3>
          <div className="landcover-bars">
            {landcoverStats.map((item) => (
              <div key={item.code} className="landcover-item">
                <span className="landcover-label">{item.name}</span>
                <div className="landcover-bar">
                  <div 
                    className={`landcover-fill ${item.cssClass}`}
                    style={{ width: `${item.percent}%`, backgroundColor: item.color }}
                  ></div>
                </div>
                <span className="landcover-percent">{item.percent}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rainfall Chart */}
      {rainfallData.length > 0 && (
        <div className="glass-card rainfall-card">
          <h3>📈 Rainfall Trends</h3>
          <div className="chart-container">
            <RainfallChart data={rainfallData} />
          </div>
        </div>
      )}

      {/* Weather Forecast */}
      <WeatherCard weather={weatherData} />

      {/* Pollen Index */}
      <PollenCard pollen={pollenData} />

      {/* Solar Potential */}
      <SolarCard solar={solarData} />
    </div>
  );
}

export default ResultsPanel;
