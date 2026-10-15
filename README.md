# AquaGeoAI Cape Town WebGIS

An interactive Leaflet map for Cape Town with an OpenStreetMap basemap and two Google Earth Engine tile layers.

## Publish using GitHub Pages

1. Create a public GitHub repository.
2. Upload `index.html`, `README.md`, and `.gitignore` to the repository root.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, select **Deploy from a branch**.
5. Select branch `main` and folder `/ (root)`, then save.
6. Wait for GitHub Pages to publish and open the displayed URL.

## Important limitations

- The Earth Engine tile URLs were retained from the supplied HTML. They may expire; refresh them from Earth Engine before production use.
- The supplied HTML does not identify the scientific meaning of the two Earth Engine layers. The layer labels are provisional; confirm the datasets before renaming them.
- Confirm that each layer is intended for public viewing before publishing.
- Never commit private credentials, service-account keys, or `.env` files.
- This is a static map page. It does not run a FastAPI backend or perform new Earth Engine calculations.
- An internet connection is required for the external Leaflet libraries and map tiles.
- OpenStreetMap attribution is included in the map.

## Local preview

Run from this folder:

```bash
python -m http.server 5500
```

Then visit `http://127.0.0.1:5500`.
