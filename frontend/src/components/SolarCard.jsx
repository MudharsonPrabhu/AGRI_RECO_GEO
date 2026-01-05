function SolarCard({ solar }) {
  if (!solar) return null;

  const { daily_irradiance_kwh, annual_sunshine_hours, solar_score, status, recommendations } = solar;

  const getScoreColor = (score) => {
    if (score >= 80) return '#f59e0b';
    if (score >= 60) return '#eab308';
    if (score >= 40) return '#84cc16';
    return '#64748b';
  };

  return (
    <div className="solar-card glass-card">
      <div className="solar-header">
        <h3>☀️ Solar Potential</h3>
        {status && (
          <div className="solar-status" style={{ color: status.color }}>
            {status.emoji} {status.level}
          </div>
        )}
      </div>

      {/* Solar Score Gauge */}
      {solar_score !== undefined && (
        <div className="solar-gauge">
          <svg viewBox="0 0 100 60" className="solar-meter">
            <defs>
              <linearGradient id="solarGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style={{ stopColor: '#64748b' }} />
                <stop offset="50%" style={{ stopColor: '#eab308' }} />
                <stop offset="100%" style={{ stopColor: '#f59e0b' }} />
              </linearGradient>
            </defs>
            <path
              d="M 10 50 A 40 40 0 0 1 90 50"
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="8"
              strokeLinecap="round"
            />
            <path
              d="M 10 50 A 40 40 0 0 1 90 50"
              fill="none"
              stroke="url(#solarGradient)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${(solar_score / 100) * 126} 126`}
            />
          </svg>
          <div className="solar-score" style={{ color: getScoreColor(solar_score) }}>
            {solar_score}%
          </div>
        </div>
      )}

      {/* Solar Stats */}
      <div className="solar-stats">
        {daily_irradiance_kwh && (
          <div className="solar-stat">
            <span className="stat-value">{daily_irradiance_kwh}</span>
            <span className="stat-label">kWh/m²/day</span>
          </div>
        )}
        {annual_sunshine_hours && (
          <div className="solar-stat">
            <span className="stat-value">{annual_sunshine_hours}</span>
            <span className="stat-label">hrs/year</span>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="solar-recommendations">
          {recommendations.map((rec, index) => (
            <span key={index} className="recommendation-tag solar">✓ {rec}</span>
          ))}
        </div>
      )}
    </div>
  );
}

export default SolarCard;
