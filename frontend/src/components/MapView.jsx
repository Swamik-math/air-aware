import { Fragment, useEffect } from "react";
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";

const MAP_TILE_URL =
  import.meta.env.VITE_MAP_TILE_URL ||
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}";

const MAP_ATTRIBUTION =
  import.meta.env.VITE_MAP_ATTRIBUTION ||
  "Tiles &copy; Esri - Source: Esri, Maxar, Earthstar Geographics";

const routeStyles = {
  shortest: { color: "#1280ff", weight: 6 },
  fastest: { color: "#ff9f0a", weight: 6 },
  healthiest: { color: "#32d74b", weight: 6 }
};

function normalizePoint(point) {
  if (!Array.isArray(point) || point.length !== 2) {
    return null;
  }

  const a = Number(point[0]);
  const b = Number(point[1]);
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    return null;
  }

  if (Math.abs(a) <= 90 && Math.abs(b) <= 180) {
    return [a, b];
  }

  if (Math.abs(b) <= 90 && Math.abs(a) <= 180) {
    return [b, a];
  }

  return null;
}

function resolveRouteGeometry(route, source, destination) {
  const normalized = (route?.geometry || []).map(normalizePoint).filter(Boolean);
  if (normalized.length >= 2) {
    return normalized;
  }

  if (Array.isArray(source) && Array.isArray(destination)) {
    return [source, destination];
  }

  return [];
}

const BENGALURU_BOUNDS = [
  [12.75, 77.35],
  [13.2, 77.85]
];

function FitRouteView({ source, destination, routes, selectedRoute }) {
  const map = useMap();

  useEffect(() => {
    const selectedGeometry = resolveRouteGeometry(routes?.[selectedRoute], source, destination);
    const points = [];

    if (Array.isArray(source) && source.length === 2) {
      points.push(source);
    }
    if (Array.isArray(destination) && destination.length === 2) {
      points.push(destination);
    }
    if (selectedGeometry.length > 0) {
      points.push(...selectedGeometry);
    }

    if (points.length > 1) {
      map.fitBounds(points, { padding: [28, 28], maxZoom: 15, animate: true, duration: 1.1 });
    } else if (points.length === 1) {
      map.setView(points[0], 14, { animate: true, duration: 1.1 });
    } else {
      map.fitBounds(BENGALURU_BOUNDS, { padding: [18, 18], animate: true, duration: 1.1 });
    }
  }, [map, source, destination, routes, selectedRoute]);

  return null;
}

export default function MapView({
  source,
  destination,
  routes,
  animationToken,
  selectedRoute,
  hoveredRoute,
  onSelectRoute,
  onHoverRoute
}) {
  const center = source || [12.9716, 77.5946];
  const routeEntries = routes
    ? Object.entries(routes).filter(([key]) => ["shortest", "fastest", "healthiest"].includes(key))
    : [];
  const selected = routes?.[selectedRoute];
  const orderedRoutes = [
    ...routeEntries.filter(([key]) => key !== selectedRoute),
    ...routeEntries.filter(([key]) => key === selectedRoute)
  ];


  return (
    <div className="map-shell">
      <MapContainer
        center={center}
        zoom={13}
        minZoom={11}
        maxZoom={18}
        maxBounds={BENGALURU_BOUNDS}
        maxBoundsViscosity={1.0}
        scrollWheelZoom
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution={MAP_ATTRIBUTION}
          url={MAP_TILE_URL}
        />

        <FitRouteView source={source} destination={destination} routes={routes} selectedRoute={selectedRoute} />

        {source && (
          <Marker position={source}>
            <Popup>Source (Bengaluru)</Popup>
          </Marker>
        )}

        {destination && (
          <Marker position={destination}>
            <Popup>Destination (Bengaluru)</Popup>
          </Marker>
        )}

        {orderedRoutes.map(([key, route]) => {
          const style = routeStyles[key];
          const isSelected = key === selectedRoute;
          const isHovered = key === hoveredRoute;
          const geometry = resolveRouteGeometry(route, source, destination);

          return (
            <Fragment key={`route-${key}-${animationToken}`}>
              {isSelected && (
                <Polyline
                  positions={geometry}
                  className="route-line route-outline"
                  pathOptions={{
                    color: "#ffffff",
                    weight: style.weight + 8,
                    opacity: 0.9
                  }}
                />
              )}
              <Polyline
                positions={geometry}
                className={`route-line route-main route-${key} ${isSelected ? "route-animate" : ""} ${isHovered ? "route-hover" : ""}`}
                eventHandlers={{
                  click: () => onSelectRoute?.(key),
                  mouseover: () => onHoverRoute?.(key),
                  mouseout: () => onHoverRoute?.("")
                }}
                pathOptions={{
                  color: style.color,
                  lineCap: "round",
                  lineJoin: "round",
                  weight: isSelected ? style.weight + 1 : isHovered ? style.weight : 4,
                  opacity: isSelected ? 0.96 : isHovered ? 0.68 : 0.3,
                  dashArray: isSelected || isHovered ? undefined : "7 10"
                }}
              />
            </Fragment>
          );
        })}
      </MapContainer>

      {selected && (
        <div className="map-hud">
          <p className="map-hud-title">{selectedRoute.charAt(0).toUpperCase() + selectedRoute.slice(1)} selected</p>
          <p>{selected.distance_km} km · {selected.duration_min} min · AQI {selected.avg_aqi}</p>
        </div>
      )}
    </div>
  );
}
