const routeConfig = [
  { key: "shortest", title: "Shortest Route" },
  { key: "fastest", title: "Fastest Route" },
  { key: "healthiest", title: "Healthiest Route" }
];

function scoreBand(aqi) {
  if (aqi <= 50) return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive";
  if (aqi <= 200) return "Unhealthy";
  return "Very Unhealthy";
}

export default function RoutePanel({ routes, selectedRoute, onSelectRoute }) {
  if (!routes) {
    return <div className="panel placeholder">Compute routes to view details.</div>;
  }

  return (
    <div className="panel">
      <h2>Route Insights</h2>
      <div className="cards">
        {routeConfig.map(({ key, title }) => {
          const route = routes[key];
          return (
            <button
              type="button"
              key={key}
              onClick={() => onSelectRoute(key)}
              className={`route-card ${selectedRoute === key ? "active" : ""}`}
            >
              <h3>{title}</h3>
              <p>Distance: {route.distance_km} km</p>
              <p>Time: {route.duration_min} min</p>
              <p>AQI Exposure: {route.avg_aqi}</p>
              <p>Density: {Math.round(route.avg_density)} people/km2</p>
              <p>Health Score: {route.health_score}/100</p>
              <p className="aqi-band">AQI Band: {scoreBand(route.avg_aqi)}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
