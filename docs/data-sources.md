# Data sources and interpretation

| Indicator | Dataset | Resolution / temporal basis | Interpretation and limitations |
|---|---|---|---|
| Precipitation | CHIRPS Daily (`UCSB-CHG/CHIRPS/DAILY`) | About 0.05°; daily, aggregated to calendar year | Gridded rainfall estimate; not direct local gauge observation or recharge. |
| Vegetation | MODIS MOD13Q1 (`MODIS/061/MOD13Q1`) | 250 m; 16-day composites, annual median | NDVI is scaled by 0.0001 and used here as a vegetation-condition indicator. Clouds, mixed pixels and seasonality affect interpretation. |
| Basemap | OpenFreeMap Liberty style | Web map tiles | Requires internet; attribution and service terms apply. |

## Required before operational use

- Confirm AOI geometry, coordinate reference, coverage and Earth Engine asset type.
- Compare CHIRPS rainfall with appropriate South African Weather Service / municipal gauges where available.
- For recharge: document hydrogeology, soil, geology, land cover, ET, runoff, abstraction and validation observations; P−ET alone is insufficient.
- For water quality: use verified in-situ samples or sensor-specific retrievals with calibration/validation. NDVI is not a water-quality indicator.
- Record data versions, processing dates, units, missing-data handling and uncertainty for every public result.
