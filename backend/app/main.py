"""AquaGeoAI Cape Town geospatial API powered by Google Earth Engine.

Earth Engine credentials must be configured in the hosting environment. Never
commit service-account keys or user credentials to source control.
"""
import logging
import os
from typing import Any

import ee
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("aquageoai")
GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "").strip()
AOI_ASSET = os.getenv("AOI_ASSET", "projects/ee-ttgintamo/assets/City_of_Cape_Town").strip()
CHIRPS_COLLECTION = "UCSB-CHG/CHIRPS/DAILY"
MODIS_NDVI_COLLECTION = "MODIS/061/MOD13Q1"
FIRST_YEAR = 2000
LAST_COMPLETE_YEAR = 2025

app = FastAPI(title="AquaGeoAI Cape Town API", description="Earth observation and climate indicators for Cape Town.", version="1.0.0")
origins = [x.strip() for x in os.getenv("FRONTEND_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET"], allow_headers=["*"])


def initialize_earth_engine() -> None:
    if not GEE_PROJECT_ID:
        raise RuntimeError("GEE_PROJECT_ID is not configured on the server.")
    ee.Initialize(project=GEE_PROJECT_ID)


def get_aoi() -> Any:
    """Load AOI as a FeatureCollection; configure AOI_ASSET to a compatible asset."""
    aoi = ee.FeatureCollection(AOI_ASSET)
    count = aoi.size().getInfo()
    if not count:
        raise RuntimeError("The configured AOI FeatureCollection is empty or inaccessible.")
    return aoi


def annual_rainfall_image(year: int):
    start, end = ee.Date.fromYMD(year, 1, 1), ee.Date.fromYMD(year + 1, 1, 1)
    daily = ee.ImageCollection(CHIRPS_COLLECTION).filterDate(start, end).select("precipitation")
    count = daily.size().getInfo()
    if not count:
        raise RuntimeError(f"No CHIRPS images found for {year}.")
    aoi = get_aoi()
    return daily.sum().rename("rainfall_mm").clip(aoi.geometry()), aoi, count


def ndvi_image(year: int):
    start, end = ee.Date.fromYMD(year, 1, 1), ee.Date.fromYMD(year + 1, 1, 1)
    collection = ee.ImageCollection(MODIS_NDVI_COLLECTION).filterDate(start, end).select("NDVI")
    count = collection.size().getInfo()
    if not count:
        raise RuntimeError(f"No MODIS NDVI images found for {year}.")
    aoi = get_aoi()
    # MODIS MOD13Q1 NDVI scale factor is 0.0001. Median annual NDVI is unitless.
    return collection.median().multiply(0.0001).rename("ndvi").clip(aoi.geometry()), aoi, count


def image_stats(image, band: str, aoi, scale: int) -> float:
    result = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi.geometry(), scale=scale, maxPixels=10_000_000, tileScale=2).getInfo()
    value = result.get(band)
    if value is None:
        raise RuntimeError(f"No valid {band} pixels found inside the configured AOI.")
    return float(value)


def tile_result(image, vis: dict, year: int, layer: str, units: str, count: int, caveat: str):
    map_id = image.getMapId(vis)
    tile_url = map_id["tile_fetcher"].url_format
    if not tile_url:
        raise RuntimeError("Earth Engine did not return a tile URL.")
    return {"year": year, "layer": layer, "dataset": CHIRPS_COLLECTION if layer == "rainfall" else MODIS_NDVI_COLLECTION,
            "units": units, "layer_type": "raster", "tile_url": tile_url, "image_count": count,
            "display": {"min": vis["min"], "max": vis["max"], "palette": vis["palette"]}, "status": "computed", "caveat": caveat}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AquaGeoAI Cape Town API", "earth_engine_project_configured": bool(GEE_PROJECT_ID), "aoi_asset": AOI_ASSET}


@app.get("/api/v1/layers")
def list_layers():
    return {"layers": [
        {"id": "rainfall", "label": "Annual rainfall (CHIRPS)", "endpoint": "/api/v1/rainfall/annual/map", "units": "mm/year", "status": "available when Earth Engine is configured"},
        {"id": "ndvi", "label": "Annual median NDVI (MODIS)", "endpoint": "/api/v1/vegetation/ndvi/map", "units": "unitless (-1 to 1)", "status": "available when Earth Engine is configured"},
        {"id": "recharge-screening", "label": "Groundwater recharge potential", "status": "not implemented; requires hydrogeological method and local validation"},
        {"id": "water-quality", "label": "Water quality", "status": "not implemented; requires fit-for-purpose observations or validated retrievals"}
    ]}


@app.get("/api/v1/rainfall/annual")
def annual_rainfall(year: int = Query(2020, ge=1981, le=LAST_COMPLETE_YEAR)):
    try:
        initialize_earth_engine(); image, aoi, count = annual_rainfall_image(year)
        value = image_stats(image, "rainfall_mm", aoi, 5566)
        return {"year": year, "mean_annual_rainfall_mm": round(value, 3), "units": "mm/year", "dataset": CHIRPS_COLLECTION,
                "study_area_asset": AOI_ASSET, "aggregation": "Mean of annual pixel totals over AOI", "daily_images_used": count,
                "status": "computed", "caveat": "CHIRPS is a gridded precipitation estimate, not a groundwater-recharge estimate."}
    except Exception as exc:
        logger.exception("Annual rainfall calculation failed")
        raise HTTPException(status_code=503, detail="Rainfall unavailable. Check GEE authentication/project, AOI asset type/access, and data availability.") from exc


@app.get("/api/v1/rainfall/annual/map")
def annual_rainfall_map(year: int = Query(2020, ge=1981, le=LAST_COMPLETE_YEAR)):
    try:
        initialize_earth_engine(); image, _aoi, count = annual_rainfall_image(year)
        vis = {"min": 0, "max": 1500, "palette": ["fff7ec", "fee8c8", "fdd49e", "fdbb84", "fc8d59", "ef6548", "d7301f", "990000"]}
        result = tile_result(image, vis, year, "rainfall", "mm/year", count, "CHIRPS precipitation estimate; not groundwater recharge. Tile URL may contain a temporary token.")
        result["daily_images_used"] = count
        return result
    except Exception as exc:
        logger.exception("Rainfall map failed")
        raise HTTPException(status_code=503, detail="Rainfall map unavailable. Check Earth Engine authentication and AOI/data access.") from exc


@app.get("/api/v1/vegetation/ndvi")
def annual_ndvi(year: int = Query(2020, ge=2000, le=LAST_COMPLETE_YEAR)):
    try:
        initialize_earth_engine(); image, aoi, count = ndvi_image(year)
        value = image_stats(image, "ndvi", aoi, 250)
        return {"year": year, "mean_annual_median_ndvi": round(value, 4), "units": "unitless", "dataset": MODIS_NDVI_COLLECTION,
                "images_used": count, "status": "computed", "caveat": "NDVI indicates vegetation greenness/condition; it is not a direct measure of water quality or soil moisture."}
    except Exception as exc:
        logger.exception("NDVI statistic failed")
        raise HTTPException(status_code=503, detail="NDVI statistic unavailable. Check Earth Engine authentication and AOI/data access.") from exc


@app.get("/api/v1/vegetation/ndvi/map")
def annual_ndvi_map(year: int = Query(2020, ge=2000, le=LAST_COMPLETE_YEAR)):
    try:
        initialize_earth_engine(); image, _aoi, count = ndvi_image(year)
        vis = {"min": 0, "max": 0.8, "palette": ["8c510a", "d8b365", "f6e8c3", "c7eae5", "5ab4ac", "01665e"]}
        return tile_result(image, vis, year, "ndvi", "unitless", count, "MODIS NDVI is a vegetation-condition indicator, not water quality or a direct soil-moisture measurement.")
    except Exception as exc:
        logger.exception("NDVI map failed")
        raise HTTPException(status_code=503, detail="NDVI map unavailable. Check Earth Engine authentication and AOI/data access.") from exc


@app.get("/api/v1/aoi")
def aoi_metadata():
    """Return metadata only; avoids exposing the boundary as an unreviewed public GeoJSON."""
    return {"asset": AOI_ASSET, "expected_type": "Earth Engine FeatureCollection", "configured": bool(AOI_ASSET),
            "note": "Confirm the asset type and permissions in Earth Engine. This endpoint does not publish AOI geometry."}
