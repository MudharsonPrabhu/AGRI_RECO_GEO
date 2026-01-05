function WeatherCard({ weather }) {
  if (!weather) return null;

  const { current, forecast, recommendations, alerts } = weather;

  const getConditionIcon = (condition) => {
    const icons = {
      'Clear': '☀️',
      'Sunny': '☀️',
      'Partly Cloudy': '⛅',
      'Cloudy': '☁️',
      'Rainy': '🌧️',
      'Thunderstorm': '⛈️',
      'Snow': '❄️',
      'Fog': '🌫️'
    };
    return icons[condition] || '🌤️';
  };

  return (
    <div className="weather-card glass-card">
      <h3>🌤️ Weather Forecast</h3>
      
      {/* Current Weather */}
      {current && (
        <div className="current-weather">
          <div className="weather-main">
            <span className="weather-icon">{getConditionIcon(current.condition)}</span>
            <span className="weather-temp">{current.temperature}°C</span>
          </div>
          <div className="weather-details">
            <span>Feels like: {current.feels_like}°C</span>
            <span>Humidity: {current.humidity}%</span>
            <span>Wind: {current.wind_speed} km/h</span>
          </div>
          <div className="weather-condition">{current.condition}</div>
        </div>
      )}

      {/* 5-Day Forecast */}
      {forecast && forecast.length > 0 && (
        <div className="forecast-strip">
          {forecast.slice(0, 5).map((day, index) => (
            <div key={index} className="forecast-day">
              <span className="forecast-date">{day.day?.substring(0, 3) || day.date?.substring(5)}</span>
              <span className="forecast-icon">{getConditionIcon(day.condition)}</span>
              <span className="forecast-temp">{day.temp_max}°/{day.temp_min}°</span>
              {day.rain_chance !== undefined && (
                <span className="forecast-rain">💧 {day.rain_chance}%</span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Weather Alerts */}
      {alerts && alerts.length > 0 && (
        <div className="weather-alerts">
          {alerts.map((alert, index) => (
            <div key={index} className={`alert-item ${alert.severity}`}>
              ⚠️ {alert.message}
            </div>
          ))}
        </div>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="weather-recommendations">
          {recommendations.slice(0, 3).map((rec, index) => (
            <span key={index} className="recommendation-tag">{rec}</span>
          ))}
        </div>
      )}
    </div>
  );
}

export default WeatherCard;
