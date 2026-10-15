# Deployment checklist

1. **Frontend:** publish `index.html`, `css/`, `js/`, and `assets/` with GitHub Pages or another static host.
2. **Backend:** deploy `backend/` as a separate Python service using `backend/Dockerfile` or the documented Uvicorn command.
3. **Secrets:** configure `GEE_PROJECT_ID`, `AOI_ASSET`, and `FRONTEND_ORIGINS` in the hosting provider's environment settings. Do not commit secrets.
4. **Earth Engine:** authorize the runtime identity, enable required APIs, ensure Earth Engine access and grant access to the AOI asset.
5. **Frontend URL:** update `AQUAGEOAI_API_BASE` in `js/app.js` to the HTTPS backend origin.
6. **CORS:** set `FRONTEND_ORIGINS` to the exact published frontend origin(s).
7. **Verification:** test `/api/health`, `/api/v1/layers`, rainfall and NDVI statistic/map endpoints, browser console and mobile layout. A healthy API does not guarantee that the AOI is readable.
8. **Production hardening:** add rate limiting, monitoring, structured logs, error tracking, authentication if private datasets are added, and a secure tile proxy if tile tokens/data must not be exposed.
9. **Scientific QA:** validate rainfall estimates against local observations; do not publish recharge, forecast or water-quality outputs until their methods and uncertainty have been validated.

GitHub Pages does not run FastAPI or Earth Engine Python code. The backend must be hosted separately.
