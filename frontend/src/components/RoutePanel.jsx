const routeConfig = [
  { key: "shortest", title: "Shortest Route" },
  { key: "fastest", title: "Fastest Route" },
  { key: "healthiest", title: "Healthiest Route" }
];

const routeKeys = routeConfig.map((route) => route.key);

function scoreBand(aqi) {
  if (aqi <= 50) return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive";
  if (aqi <= 200) return "Unhealthy";
  return "Very Unhealthy";
}

function routeTone(key) {
  if (key === "healthiest") return "tone-green";
  if (key === "fastest") return "tone-amber";
  return "tone-blue";
}

function isLiveValue(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) && numeric > 0;
}

function normalizeWidth(value, min, max) {
  if (!Number.isFinite(value)) {
    return 0;
  }

  if (max <= min) {
    return 100;
  }

  return ((value - min) / (max - min)) * 100;
}

function getBestFlags(routes) {
  const pool = routeKeys
    .filter((key) => routes?.[key])
    .map((key) => ({ key, route: routes[key] }));

  if (!pool.length) {
    return {};
  }

  const shortestKey = [...pool].sort((a, b) => a.route.distance_km - b.route.distance_km)[0].key;
  const fastestKey = [...pool].sort((a, b) => a.route.duration_min - b.route.duration_min)[0].key;
  const healthiestKey = [...pool].sort((a, b) => b.route.health_score - a.route.health_score)[0].key;

  return {
    [shortestKey]: "Shortest",
    [fastestKey]: "Fastest",
    [healthiestKey]: "Healthiest"
  };
}

function LoadingSkeleton() {
  return (
    <div className="cards">
      {["s1", "s2", "s3"].map((id) => (
        <div key={id} className="route-card route-skeleton" aria-hidden="true">
          <div className="skeleton-line skeleton-title" />
          <div className="skeleton-grid">
            <div className="skeleton-line" />
            <div className="skeleton-line" />
            <div className="skeleton-line" />
            <div className="skeleton-line" />
          </div>
          <div className="skeleton-line skeleton-footer" />
        </div>
      ))}
    </div>
  );
}

export default function RoutePanel({
  routes,
  loading,
  selectedRoute,
  hoveredRoute,
  onSelectRoute,
  onHoverRoute
}) {
  if (loading) {
    return (
      <div className="panel">
        <h2>Route Insights</h2>
        <LoadingSkeleton />
      </div>
    );
  }

  if (!routes) {
    return <div className="panel placeholder">Compute routes to view details.</div>;
  }

  const distanceList = routeKeys.map((key) => routes[key]?.distance_km).filter(Number.isFinite);
  const etaList = routeKeys.map((key) => routes[key]?.duration_min).filter(Number.isFinite);

  const minDistance = Math.min(...distanceList);
  const maxDistance = Math.max(...distanceList);
  const minEta = Math.min(...etaList);
  const maxEta = Math.max(...etaList);
  const bestFlags = getBestFlags(routes);

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
              onMouseEnter={() => onHoverRoute?.(key)}
              onMouseLeave={() => onHoverRoute?.("")}
              className={`route-card ${routeTone(key)} ${selectedRoute === key ? "active" : ""} ${hoveredRoute === key ? "hovered" : ""}`}
            >
              <div className="route-head">
                <h3>{title}</h3>
                <div className="route-badges">
                  {bestFlags[key] && <span className="best-badge">Best {bestFlags[key]}</span>}
                  <span className="route-health">{route.health_score}/100</span>
                </div>
              </div>
              <div className="route-metrics">
                <p>
                  <span>Distance</span>
                  {route.distance_km} km
                  <em className="metric-bar"><i style={{ width: `${normalizeWidth(route.distance_km, minDistance, maxDistance)}%` }} /></em>
                </p>
                <p>
                  <span>ETA</span>
                  {route.duration_min} min
                  <em className="metric-bar"><i style={{ width: `${normalizeWidth(route.duration_min, minEta, maxEta)}%` }} /></em>
                </p>
                <p>
                  <span>AQI</span>
                  {isLiveValue(route.avg_aqi) ? route.avg_aqi : "No live data"}
                </p>
                <p>
                  <span>Density</span>
                  {isLiveValue(route.avg_density) ? `${Math.round(route.avg_density)} /km2` : "No live data"}
                </p>
              </div>
              <p className="aqi-band">AQI Band: {isLiveValue(route.avg_aqi) ? scoreBand(route.avg_aqi) : "Unknown"}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
