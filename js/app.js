document.getElementById("year").textContent = new Date().getFullYear();

// Local development default. Replace with your deployed HTTPS API origin for production.
const AQUAGEOAI_API_BASE = "http://127.0.0.1:8000";
(function initializeAquaGeoAIMap() {
  const mapElement = document.getElementById("aquageoai-map");
  if (!mapElement) return;
  const center = [18.4241, -33.9249];
  const statusElement = document.getElementById("map-status");
  const yearSelect = document.getElementById("rainfall-year");
  const layerSelect = document.getElementById("map-layer");
  const loadButton = document.getElementById("load-rainfall");
  const legend = document.getElementById("map-legend");
  let map;
  function setStatus(message, state) {
    statusElement.textContent = message;
    if (state) statusElement.dataset.state = state; else delete statusElement.dataset.state;
  }
  function mapError(message) {
    mapElement.innerHTML = "";
    const box = document.createElement("div"); box.className = "map-error"; box.textContent = message; mapElement.appendChild(box);
  }
  if (typeof maplibregl === "undefined") { mapError("Map library did not load. Check internet access and refresh."); return; }
  try {
    map = new maplibregl.Map({container: "aquageoai-map", style: "https://tiles.openfreemap.org/styles/liberty", center, zoom: 9.5, attributionControl: true});
    map.addControl(new maplibregl.NavigationControl({visualizePitch: true}), "top-right");
    map.addControl(new maplibregl.ScaleControl({maxWidth: 120, unit: "metric"}), "bottom-left");
    map.addControl(new maplibregl.FullscreenControl(), "top-right");
    map.on("load", () => setStatus("Basemap ready. Choose a data layer and select Load data layer.", "success"));
    map.on("error", e => console.warn("AquaGeoAI map error", e && e.error ? e.error : e));
    document.getElementById("reset-map")?.addEventListener("click", () => map.flyTo({center, zoom: 9.5, pitch: 0, bearing: 0, essential: true}));
    async function loadLayer() {
      if (!map.isStyleLoaded()) { setStatus("Map is still loading. Try again shortly.", "error"); return; }
      const layer = layerSelect.value, year = Number(yearSelect.value);
      const isNdvi = layer === "ndvi";
      const endpoint = isNdvi ? "/api/v1/vegetation/ndvi/map" : "/api/v1/rainfall/annual/map";
      loadButton.disabled = true; loadButton.textContent = "Loading…";
      setStatus(`Requesting ${isNdvi ? "MODIS NDVI" : "CHIRPS rainfall"} for ${year}…`);
      try {
        const url = new URL(endpoint, AQUAGEOAI_API_BASE); url.searchParams.set("year", String(year));
        const response = await fetch(url);
        if (!response.ok) { let message = `API returned HTTP ${response.status}`; try { const body = await response.json(); if (body.detail) message = body.detail; } catch (_) {} throw new Error(message); }
        const result = await response.json(); if (!result.tile_url) throw new Error("API response did not include a raster tile URL.");
        if (map.getLayer("analysis-layer")) map.removeLayer("analysis-layer");
        if (map.getSource("analysis-source")) map.removeSource("analysis-source");
        map.addSource("analysis-source", {type: "raster", tiles: [result.tile_url], tileSize: 256, attribution: isNdvi ? "NDVI: MODIS MOD13Q1 · NASA/USGS via Earth Engine" : "Rainfall: CHIRPS · UCSB-CHG via Earth Engine"});
        map.addLayer({id: "analysis-layer", type: "raster", source: "analysis-source", paint: {"raster-opacity": 0.72}});
        const colors = result.display.palette || [];
        legend.replaceChildren();
        const heading = document.createElement("strong"); heading.textContent = isNdvi ? `Annual median NDVI · ${year}` : `Annual rainfall · ${year}`; legend.appendChild(heading);
        const bar = document.createElement("div"); bar.className = "legend-gradient"; bar.style.background = `linear-gradient(to right, ${colors.map((c, i) => `${c} ${colors.length < 2 ? 0 : i * 100 / (colors.length - 1)}%`).join(", ")})`; legend.appendChild(bar);
        const range = document.createElement("span"); range.className = "layer-chip"; range.textContent = `${result.display.min} to ${result.display.max} ${result.units}`; legend.appendChild(range);
        const note = isNdvi ? "NDVI represents vegetation greenness/condition; it is not a water-quality or direct soil-moisture measurement." : "CHIRPS is an estimated precipitation product; rainfall is not groundwater recharge.";
        setStatus(`${isNdvi ? "MODIS annual median NDVI" : "Annual CHIRPS rainfall"} layer loaded for ${year}. ${note}`, "success");
      } catch (error) {
        console.error("AquaGeoAI layer request failed", error);
        setStatus(`Could not load the layer. Ensure the API is running, Earth Engine is configured, and the AOI is accessible. ${error.message}`, "error");
      } finally { loadButton.disabled = false; loadButton.textContent = "Load data layer"; }
    }
    loadButton?.addEventListener("click", loadLayer);
    // Test API connectivity without implying that Earth Engine is configured.
    fetch(new URL("/api/health", AQUAGEOAI_API_BASE)).then(r => r.json()).then(data => {
      if (!data.earth_engine_project_configured) setStatus("API reachable, but GEE_PROJECT_ID is not configured on the backend.", "error");
    }).catch(() => setStatus("Basemap is available. Start the FastAPI backend to enable analysis layers.", "error"));
  } catch (error) { console.error(error); mapError("The interactive map could not be initialized. Check browser console and network access."); }
})();
