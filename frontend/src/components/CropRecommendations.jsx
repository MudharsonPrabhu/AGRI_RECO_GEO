function CropRecommendations({ recommendations }) {
  if (!recommendations || !recommendations.recommendations || recommendations.recommendations.length === 0) {
    return null;
  }

  const { recommendations: crops, season, region } = recommendations;

  const getMatchColor = (color) => {
    switch (color) {
      case 'excellent': return '#10b981';
      case 'good': return '#3b82f6';
      case 'moderate': return '#f59e0b';
      default: return '#64748b';
    }
  };

  const getWaterIcon = (requirement) => {
    switch (requirement) {
      case 'very_high': return '💧💧💧';
      case 'high': return '💧💧';
      case 'medium': return '💧';
      default: return '🌵';
    }
  };

  return (
    <div className="crop-recommendations">
      <div className="crop-header">
        <h3>🌱 Recommended Crops</h3>
        <div className="crop-meta">
          <span className="season-badge">{season?.toUpperCase()} Season</span>
          <span className="region-text">{region}</span>
        </div>
      </div>

      <div className="crop-list">
        {crops.map((crop, index) => (
          <div key={crop.id} className={`crop-card ${crop.match_color}`}>
            <div className="crop-rank">#{index + 1}</div>
            
            <div className="crop-main">
              <div className="crop-title">
                <span className="crop-emoji">{crop.emoji}</span>
                <span className="crop-name">{crop.name}</span>
              </div>
              
              <div className="crop-score-bar">
                <div 
                  className="crop-score-fill" 
                  style={{ 
                    width: `${crop.score}%`,
                    backgroundColor: getMatchColor(crop.match_color)
                  }}
                />
                <span className="crop-score-text">{crop.score}%</span>
              </div>
              
              <div className="crop-match-label" style={{ color: getMatchColor(crop.match_color) }}>
                {crop.match_level}
              </div>
            </div>

            <div className="crop-details">
              <div className="crop-detail-item">
                <span className="detail-label">Yield</span>
                <span className="detail-value">{crop.yield_potential}</span>
              </div>
              <div className="crop-detail-item">
                <span className="detail-label">Duration</span>
                <span className="detail-value">{crop.growing_days} days</span>
              </div>
              <div className="crop-detail-item">
                <span className="detail-label">Water</span>
                <span className="detail-value">{getWaterIcon(crop.water_requirement)}</span>
              </div>
            </div>

            <div className="crop-reasons">
              {crop.reasons.map((reason, i) => (
                <span key={i} className="reason-tag">✓ {reason}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CropRecommendations;
