import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000
});

export async function getRoutes(payload) {
  const response = await api.post("/get-routes", payload);
  return response.data;
}

export async function getAqi(lat, lon) {
  const response = await api.get("/aqi-data", { params: { lat, lon } });
  return response.data;
}

export async function searchPlaces(query) {
  const response = await api.get("/search-places", {
    params: { q: query, limit: 5 },
    timeout: 12000
  });
  return response.data?.results || [];
}

export async function geocodePlace(query) {
  const places = await searchPlaces(query);
  if (!places.length) {
    throw new Error("No matching Bengaluru place found");
  }

  const best = places[0];
  return {
    label: best.display_name,
    lat: Number(best.lat),
    lon: Number(best.lon)
  };
}
