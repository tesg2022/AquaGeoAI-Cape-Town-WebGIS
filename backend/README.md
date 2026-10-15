# AquaGeoAI Cape Town API

FastAPI + Google Earth Engine API for selected Cape Town environmental indicators.

## API endpoints

- `GET /api/health` — service and configuration status (does not prove AOI access).
- `GET /api/v1/layers` — layer catalogue and readiness notes.
- `GET /api/v1/rainfall/annual?year=2020` — AOI mean of annual CHIRPS pixel totals (mm/year).
- `GET /api/v1/rainfall/annual/map?year=2020` — MapLibre raster tile URL for annual rainfall.
- `GET /api/v1/vegetation/ndvi?year=2020` — AOI mean of annual median MODIS NDVI.
- `GET /api/v1/vegetation/ndvi/map?year=2020` — MapLibre raster tile URL for NDVI.
- `GET /api/v1/aoi` — AOI configuration metadata, not boundary geometry.
- `GET /docs` — interactive API docs.

## Local setup

Use Python 3.10+ from this folder. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
earthengine authenticate
```

Set environment variables in your shell (or deployment settings):

```powershell
$env:GEE_PROJECT_ID="your-google-cloud-project-id"
$env:AOI_ASSET="projects/ee-ttgintamo/assets/City_of_Cape_Town"
$env:FRONTEND_ORIGINS="http://localhost:5500,http://127.0.0.1:5500"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Earth Engine authentication must be available to the process, and the selected Cloud project and identity must have Earth Engine access. Confirm that the AOI asset is a FeatureCollection or adjust `get_aoi()` to match its actual asset type.

## Frontend

Serve the project root with a local static server (for example `python -m http.server 5500`) and open `http://127.0.0.1:5500`. The frontend API origin is configured in `js/app.js`. For production, deploy the API separately, use HTTPS, set the correct `FRONTEND_ORIGINS`, and replace the frontend API origin.

## Important scientific and security limitations

- CHIRPS rainfall is a gridded estimate; the returned AOI statistic is the mean of annual pixel totals, not a water balance.
- MODIS NDVI is a vegetation-condition indicator, not a direct soil-moisture or water-quality measure.
- No groundwater-recharge model, forecast model, water-quality assessment, or operational warning system is implemented here. Those require fit-for-purpose data, documented methods, calibration/validation and uncertainty reporting.
- The map endpoints return Earth Engine tile URLs to the browser. These URLs may contain temporary tokens. For private data or strict access control, proxy tile requests through an authenticated backend.
- Keep credentials and `.env` files out of GitHub. Use a managed identity or service account in production and grant least-privilege access.
- External basemap and MapLibre CDN require internet access. Review their terms, attribution and uptime before production use.
