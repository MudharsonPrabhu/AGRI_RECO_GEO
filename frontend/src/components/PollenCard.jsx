function PollenCard({ pollen }) {
  if (!pollen) return null;

  const { daily_forecast, overall_index, status } = pollen;

  const getLevelColor = (level) => {
    if (level <= 1) return '#22c55e';
    if (level <= 2) return '#84cc16';
    if (level <= 3) return '#eab308';
    if (level <= 4) return '#f59e0b';
    return '#ef4444';
  };

  const getPollenIcon = (type) => {
    const icons = {
      'Grass': '🌿',
      'Tree': '🌳',
      'Weed': '🌱'
    };
    return icons[type] || '🌸';
  };

  return (
    <div className="pollen-card glass-card">
      <div className="pollen-header">
        <h3>🌸 Pollen Index</h3>
        <div className="pollen-status" style={{ color: getLevelColor(overall_index) }}>
          {status?.emoji} {status?.level}
        </div>
      </div>

      {/* Overall Index */}
      <div className="pollen-overall">
        <div className="pollen-score" style={{ color: getLevelColor(overall_index) }}>
          {overall_index}
        </div>
        <div className="pollen-scale">/ 5</div>
      </div>

      {/* Impact on farming */}
      {status?.impact && (
        <div className="pollen-impact">{status.impact}</div>
      )}

      {/* Today's Pollen Types */}
      {daily_forecast && daily_forecast[0]?.pollen_types && (
        <div className="pollen-types">
          {daily_forecast[0].pollen_types.map((type, index) => (
            <div key={index} className="pollen-type-item">
              <span className="pollen-type-icon">{getPollenIcon(type.type)}</span>
              <span className="pollen-type-name">{type.type}</span>
              <div className="pollen-type-bar">
                <div 
                  className="pollen-type-fill" 
                  style={{ 
                    width: `${(type.level / 5) * 100}%`,
                    backgroundColor: getLevelColor(type.level)
                  }}
                />
              </div>
              <span className="pollen-type-level">{type.category}</span>
            </div>
          ))}
        </div>
      )}

      {/* 5-Day Trend */}
      {daily_forecast && daily_forecast.length > 1 && (
        <div className="pollen-trend">
          <span className="trend-label">5-Day Trend:</span>
          <div className="trend-dots">
            {daily_forecast.slice(0, 5).map((day, index) => {
              const avgLevel = day.pollen_types 
                ? day.pollen_types.reduce((sum, p) => sum + p.level, 0) / day.pollen_types.length 
                : 0;
              return (
                <div 
                  key={index}
                  className="trend-dot"
                  style={{ backgroundColor: getLevelColor(avgLevel) }}
                  title={day.date}
                />
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default PollenCard;
