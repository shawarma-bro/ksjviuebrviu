# UK Wind Generation: Day-Ahead Forecast Portal

A full-stack web application for a day-ahead electricity procurement team. It shows the latest wind generation forecast available at decision time and evaluates forecast accuracy against actual generation.

The application uses **Elexon BMRS data only**: WINDFOR forecasts and FUELHH actuals filtered to `fuelType = WIND` at the national level.

**Live App:** https://uk-wind-generation-forecast-pr4s.vercel.app
**GitHub Repository:** https://github.com/shawarma-bro/uk-wind-generation-forecast

**AI Tools:** This application was developed with the assistance of Claude by Anthropic.

## Files and Directories

* `backend/app.py` — Flask application, API routes, and static file serving.
* `backend/analysis.py` — Forecast selection and error metric calculations.
* `backend/prepare_data.py` — Converts the raw Elexon JSON export into `backend/data/wind.json`.
* `backend/data/wind.json` — Processed January 2026 actuals and forecasts used by the application.
* `api/index.py` — Entry point for Vercel serverless deployment.
* `frontend/` — React and Vite frontend; `frontend/src/App.jsx` contains the dashboard.
* `Dockerfile` and `docker-compose.yml` — Container configuration for building and running the application.
* `vercel.json` and `heroku.yml` — Deployment configuration.
* `requirements.txt` — Python dependencies.

## Features

* Interactive forecast-versus-actual generation chart.
* Adjustable day-ahead decision cutoff from 06:00 to 12:00 UTC.
* Forecast error metrics and uncertainty band.
* Error breakdowns by hour of day, delivery day, and forecast horizon.
* Summary statistics to help interpret forecast performance for procurement planning.

## Start the Application

### Using Docker

From the repository root:

```bash
docker compose up --build
```

Open http://localhost:5000 in your browser.

### Without Docker

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Build the frontend:

```bash
cd frontend
npm install
npm run build
cd ..
```

Start the Flask application from the repository root:

```bash
python -m flask --app backend.app run --port 5000
```

Open http://localhost:5000.

### Frontend Development

Start the Flask backend on port 5000, then open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server proxies `/api` requests to the backend on port 5000.

## Methodology

### Decision Time and Forecast Selection

Decisions are made on the day before delivery. For each delivery hour, the application selects the latest eligible WINDFOR forecast published before the configured decision cutoff on the preceding day.

The default cutoff is **09:00 UTC**, adjustable from 06:00 to 12:00 UTC.

The forecast selection respects the decision-time constraint to avoid look-ahead bias. UK local time is GMT (UTC+0) during January.

### Analysis Period

The analysis covers delivery days **2–31 January 2026**. Forecast decisions for these delivery days occur on the preceding calendar days, from 1–30 January 2026.

### Actual Generation

FUELHH actual generation is provided at half-hourly resolution, while WINDFOR forecasts are hourly. The two half-hourly actual generation values are averaged to obtain hourly actuals for comparison with the forecasts.

### Accuracy Metrics

The dashboard reports:

* **MAE:** Mean Absolute Error.
* **RMSE:** Root Mean Squared Error.
* **Bias:** Mean forecast error, calculated as forecast minus actual.
* **MAPE:** Mean Absolute Percentage Error.
* **Normalised MAE:** MAE expressed as a percentage of mean actual generation.
* **P50, P90 and P95 absolute error:** Percentiles of the absolute forecast errors.

Errors are also analysed by hour of day, delivery day, and forecast horizon.

### Forecast Uncertainty Band

The day-level chart displays a band created by shifting the forecast by the 10th and 90th percentiles of the January forecast errors. This provides an empirical range based on historical errors in the evaluated period; it is not a guaranteed prediction interval.

### Interpretation

At the default 09:00 UTC cutoff, the dashboard reports:

| Metric             |    Result |
| ------------------ | --------: |
| MAE                |  2,073 MW |
| RMSE               |  2,539 MW |
| Bias               | +1,773 MW |
| MAPE               |     22.2% |
| Normalised MAE     |     18.1% |
| P90 absolute error |  4,167 MW |
| P95 absolute error |  5,295 MW |

The positive bias indicates that forecast generation was higher than actual generation on average during the evaluated period.

These metrics describe historical forecast performance. They should not be treated as guaranteed thermal generation requirements, which depend on forecast-error direction and wider system conditions.

## API Endpoints

| Endpoint                                | Description                                             |
| --------------------------------------- | ------------------------------------------------------- |
| `GET /api/meta`                         | Returns dashboard metadata.                             |
| `GET /api/day?date=YYYY-MM-DD&cutoff=9` | Returns forecast and actual data for a delivery day.    |
| `GET /api/metrics?cutoff=9`             | Returns forecast accuracy metrics and error breakdowns. |
| `GET /api/horizon`                      | Returns forecast error analysis by horizon.             |

The `cutoff` parameter is expressed as an hour in UTC.

## Deployment

### Vercel

Import the GitHub repository into Vercel. The repository's `vercel.json` defines the build, output, and API routing configuration.

**Live deployment:** https://uk-wind-generation-forecast-pr4s.vercel.app

### Heroku

The repository also includes a `heroku.yml` deployment configuration for container-based deployment.

```bash
heroku stack:set container
git push heroku main
```

## Data Source

All forecast and actual generation data used in the analysis comes from Elexon BMRS:

* **WINDFOR:** Wind generation forecasts.
* **FUELHH:** Half-hourly generation by fuel type, filtered to wind.

The analysis uses the processed dataset included in `backend/data/wind.json`.

## Limitations

* The evaluation covers one month and may not represent forecast performance in other seasons.
* Results depend on the selected decision cutoff and delivery period.
* Historical error percentiles do not guarantee future forecast accuracy.
* Forecast errors alone do not determine the optimal electricity purchasing strategy or required thermal generation.
