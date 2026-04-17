import { useEffect, useState } from "react";
import MapView from "./components/MapView";
import RoutePanel from "./components/RoutePanel";
import { geocodePlace, getRoutes, searchPlaces } from "./api/client";

const BENGALURU_BOUNDS = {
  minLat: 12.75,
  maxLat: 13.2,
  minLon: 77.35,
  maxLon: 77.85
};

function isInBengaluru(point) {
  return (
    point.lat >= BENGALURU_BOUNDS.minLat &&
    point.lat <= BENGALURU_BOUNDS.maxLat &&
    point.lon >= BENGALURU_BOUNDS.minLon &&
    point.lon <= BENGALURU_BOUNDS.maxLon
  );
}

export default function App() {
  const [sourceText, setSourceText] = useState("MG Road, Bengaluru");
  const [destinationText, setDestinationText] = useState("Electronic City, Bengaluru");
  const [preference, setPreference] = useState("healthiest");
  const [weights, setWeights] = useState({ distance: 0.2, aqi: 0.55, density: 0.25 });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [routes, setRoutes] = useState(null);
  const [routeAnimationToken, setRouteAnimationToken] = useState(0);
  const [selectedRoute, setSelectedRoute] = useState("healthiest");
  const [hoveredRoute, setHoveredRoute] = useState("");
  const [panelExpanded, setPanelExpanded] = useState(false);
  const [sourcePoint, setSourcePoint] = useState({ lat: 28.6139, lon: 77.2090 });
  const [destinationPoint, setDestinationPoint] = useState({ lat: 28.5355, lon: 77.391 });

  const [sourceSuggestions, setSourceSuggestions] = useState([]);
  const [destinationSuggestions, setDestinationSuggestions] = useState([]);

  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (!sourceText.trim()) {
        setSourceSuggestions([]);
        return;
      }

      try {
        const results = await searchPlaces(sourceText.trim());
        setSourceSuggestions(results);
      } catch {
        setSourceSuggestions([]);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [sourceText]);

  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (!destinationText.trim()) {
        setDestinationSuggestions([]);
        return;
      }

      try {
        const results = await searchPlaces(destinationText.trim());
        setDestinationSuggestions(results);
      } catch {
        setDestinationSuggestions([]);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [destinationText]);

  async function handleFindRoutes(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const resolvedSource = await geocodePlace(sourceText.trim());
      const resolvedDestination = await geocodePlace(destinationText.trim());

      if (!isInBengaluru(resolvedSource) || !isInBengaluru(resolvedDestination)) {
        throw new Error("Both source and destination must be inside Bengaluru");
      }

      setSourcePoint({ lat: resolvedSource.lat, lon: resolvedSource.lon });
      setDestinationPoint({ lat: resolvedDestination.lat, lon: resolvedDestination.lon });

      const payload = {
        source: { lat: resolvedSource.lat, lon: resolvedSource.lon },
        destination: { lat: resolvedDestination.lat, lon: resolvedDestination.lon },
        preference,
        weights
      };
      const result = await getRoutes(payload);
      setRoutes(result);
      setRouteAnimationToken((prev) => prev + 1);
      setSelectedRoute(preference);
      setPanelExpanded(true);
    } catch (err) {
      const message = err?.response?.data?.error || err?.message || "Route calculation failed. Check source/destination.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  function selectSuggestion(kind, suggestion) {
    const nextPoint = { lat: Number(suggestion.lat), lon: Number(suggestion.lon) };
    if (kind === "source") {
      setSourceText(suggestion.display_name);
      setSourcePoint(nextPoint);
      setSourceSuggestions([]);
      return;
    }

    setDestinationText(suggestion.display_name);
    setDestinationPoint(nextPoint);
    setDestinationSuggestions([]);
  }

  function setWeight(name, value) {
    const next = { ...weights, [name]: Number(value) };
    const sum = next.distance + next.aqi + next.density;
    setWeights({
      distance: Number((next.distance / sum).toFixed(2)),
      aqi: Number((next.aqi / sum).toFixed(2)),
      density: Number((next.density / sum).toFixed(2))
    });
  }

  return (
    <div className={`layout ${panelExpanded ? "sheet-expanded" : "sheet-collapsed"}`}>
      <main className="content">
        <MapView
          source={[sourcePoint.lat, sourcePoint.lon]}
          destination={[destinationPoint.lat, destinationPoint.lon]}
          routes={routes}
          animationToken={routeAnimationToken}
          selectedRoute={selectedRoute}
          hoveredRoute={hoveredRoute}
          onSelectRoute={setSelectedRoute}
          onHoverRoute={setHoveredRoute}
        />
      </main>

      <aside className={`sidebar ${panelExpanded ? "expanded" : "collapsed"}`}>
        <button
          type="button"
          className="sheet-toggle"
          onClick={() => setPanelExpanded((prev) => !prev)}
          aria-expanded={panelExpanded}
          aria-label="Toggle route controls"
        >
          <span className="sheet-handle" />
        </button>

        <div className="brand-row">
          <h1>AirAware</h1>
          <p className="subtitle">Bengaluru</p>
        </div>

        <form onSubmit={handleFindRoutes} className="form-grid">
          <div className="location-field">
            <label>
              Source
              <input
                className="input-control"
                value={sourceText}
                onChange={(e) => setSourceText(e.target.value)}
                placeholder="Enter source in Bengaluru"
              />
            </label>
            {sourceSuggestions.length > 0 && (
              <div className="suggestions">
                {sourceSuggestions.map((item) => (
                  <button
                    key={`${item.place_id}-source`}
                    type="button"
                    className="suggestion-item"
                    onClick={() => selectSuggestion("source", item)}
                  >
                    {item.display_name}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="location-field">
            <label>
              Destination
              <input
                className="input-control"
                value={destinationText}
                onChange={(e) => setDestinationText(e.target.value)}
                placeholder="Enter destination in Bengaluru"
              />
            </label>
            {destinationSuggestions.length > 0 && (
              <div className="suggestions">
                {destinationSuggestions.map((item) => (
                  <button
                    key={`${item.place_id}-destination`}
                    type="button"
                    className="suggestion-item"
                    onClick={() => selectSuggestion("destination", item)}
                  >
                    {item.display_name}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="mode-wrap">
            <p className="control-title">Route Priority</p>
            <div className="mode-toggle" role="tablist" aria-label="Route priority">
              <button
                type="button"
                className={`mode-btn ${preference === "shortest" ? "active" : ""}`}
                onClick={() => setPreference("shortest")}
              >
                Shortest
              </button>
              <button
                type="button"
                className={`mode-btn ${preference === "fastest" ? "active" : ""}`}
                onClick={() => setPreference("fastest")}
              >
                Fastest
              </button>
              <button
                type="button"
                className={`mode-btn ${preference === "healthiest" ? "active" : ""}`}
                onClick={() => setPreference("healthiest")}
              >
                Healthiest
              </button>
            </div>
          </div>

          <div className="weights">
            <p className="control-title">Dynamic Weights</p>
            <label className="weight-row">
              <span>Distance</span>
              <strong>{weights.distance}</strong>
              <input
                type="range"
                min="0.05"
                max="0.9"
                step="0.05"
                value={weights.distance}
                onChange={(e) => setWeight("distance", e.target.value)}
              />
            </label>
            <label className="weight-row">
              <span>AQI</span>
              <strong>{weights.aqi}</strong>
              <input
                type="range"
                min="0.05"
                max="0.9"
                step="0.05"
                value={weights.aqi}
                onChange={(e) => setWeight("aqi", e.target.value)}
              />
            </label>
            <label className="weight-row">
              <span>Population</span>
              <strong>{weights.density}</strong>
              <input
                type="range"
                min="0.05"
                max="0.9"
                step="0.05"
                value={weights.density}
                onChange={(e) => setWeight("density", e.target.value)}
              />
            </label>
          </div>

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "Calculating..." : "Find Routes"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        <RoutePanel
          routes={routes}
          loading={loading}
          selectedRoute={selectedRoute}
          hoveredRoute={hoveredRoute}
          onSelectRoute={setSelectedRoute}
          onHoverRoute={setHoveredRoute}
        />
      </aside>
    </div>
  );
}
