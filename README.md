# UK Wind Generation: Day-Ahead Forecast Portal

Web app for a day-ahead power buying team. It shows the latest wind forecast available at decision time and measures how accurate those forecasts were, using Elexon data only (WINDFOR forecasts and FUELHH actuals, fuel type WIND, national level).

Live app: <add Vercel or Heroku link here>

AI tools: this application was built with the help of an AI assistant (Claude by Anthropic).

## Files and directories

- `backend/app.py` Flask app with the API routes and static file serving
- `backend/analysis.py` forecast selection and error metrics
- `backend/prepare_data.py` converts the raw Elexon JSON export into `backend/data/wind.json`
- `backend/data/wind.json` processed January 2026 actuals and forecasts used by the app
- `api/index.py` entry point used by Vercel
- `frontend/` React (Vite) app, `src/App.jsx` holds the dashboard
- `Dockerfile`, `docker-compose.yml` container setup (builds the frontend, serves everything from Flask)
- `vercel.json`, `heroku.yml` deployment config
- `requirements.txt` Python dependencies

## Start the application

With Docker:

    docker compose up --build

Open http://localhost:5000

Without Docker:

    pip install -r requirements.txt
    cd frontend && npm install && npm run build && cd ..
    python -m flask --app backend.app run --port 5000

For frontend development run `npm run dev` inside `frontend` (proxies `/api` to port 5000).

## Method

- Decisions are made the day before delivery. For each delivery hour, the forecast used is the latest WINDFOR forecast published before the chosen cutoff on the previous day (default 09:00 UTC, adjustable from 06:00 to 12:00). UK time equals UTC in January.
- Scope is delivery days 2 to 31 January 2026, which are the days whose decisions fall in January and for which actuals exist.
- FUELHH actuals are half-hourly, WINDFOR is hourly, so the two half-hours of each hour are averaged.
- Metrics: MAE, RMSE, bias (forecast minus actual), MAPE, MAE as a percent of mean actual, and P50/P90/P95 of absolute error. Error is also broken down by hour of day, by day, and by forecast horizon.
- The shaded band on the day chart shifts the forecast by the 10th and 90th percentile of the January errors, giving a likely range of actual wind.

## API

- `GET /api/meta`
- `GET /api/day?date=YYYY-MM-DD&cutoff=9`
- `GET /api/metrics?cutoff=9`
- `GET /api/horizon`

## Deploy

Vercel: import the repo, defaults from `vercel.json` apply.
Heroku: `heroku stack:set container` then push the repo.
