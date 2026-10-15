# AquaGeoAI Cape Town WebGIS

A working WebGIS MVP with a responsive landing page, MapLibre interactive basemap, FastAPI backend and Google Earth Engine endpoints for annual CHIRPS rainfall and annual median MODIS NDVI.

## Project layout

```text
index.html                 Website and interactive map
css/styles.css             Responsive styles
js/app.js                  Map UI and API integration
assets/logo.svg            Brand asset
docs/data-sources.md       Dataset and interpretation notes
backend/app/main.py        FastAPI + Earth Engine endpoints
backend/app/hydrology.py   P - ET screening helper (not recharge)
backend/tests/             Unit tests
```

## Run locally

1. Install Python 3.10+ and configure Earth Engine access. Follow `backend/README.md`.
2. Start the API from the `backend` directory with `uvicorn app.main:app --reload`.
3. In another terminal, serve the project root with `python -m http.server 5500`.
4. Open `http://127.0.0.1:5500`.
5. Set the `AQUAGEOAI_API_BASE` constant in `js/app.js` to the deployed API origin for production.

## What is working vs. not yet implemented

Implemented in code: interactive basemap; annual CHIRPS rainfall map/statistic endpoint; annual median MODIS NDVI map/statistic endpoint; API health and layer catalogue. Actual results require successful Earth Engine authentication, project access and AOI asset access. These integrations have not been live-tested from this build environment.

Not yet implemented: validated groundwater-recharge model, precipitation/ET water-balance model, drought forecasts, water-quality analytics, user accounts, AOI upload/drawing, export-to-GeoTIFF, automated deployment and production monitoring. Do not present these as operational capabilities until built and validated.

## Study area configuration

Default AOI: `projects/ee-ttgintamo/assets/City_of_Cape_Town`. The backend assumes this is an Earth Engine FeatureCollection. Confirm the asset type and permissions in the Earth Engine Code Editor before running the analysis. Override it with `AOI_ASSET` in the backend environment if necessary.

## Science and security

P - ET is a water-availability screening indicator, not groundwater recharge. NDVI measures vegetation greenness/condition, not water quality. Recharge and water-quality products need appropriate local data, defensible methods, validation and uncertainty documentation. Never commit credentials or `.env` files.
