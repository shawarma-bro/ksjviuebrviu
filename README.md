# UK Wind Generation: Day-Ahead Forecast Portal

A full-stack analytics dashboard for evaluating day-ahead wind generation forecasts against actual generation in Great Britain. The project focuses on forecast accuracy, decision-time forecast selection, and identifying forecasting errors that may affect energy procurement planning.

## Live Application

**Dashboard:** https://uk-wind-generation-forecast-pr4s-9uto3xenu.vercel.app/

**GitHub Repository:** https://github.com/shawarma-bro/ksjviuebrviu

## 1. Project Overview

Wind generation varies with weather conditions, making accurate forecasting important for electricity procurement and planning.

This project compares historical wind generation forecasts with actual generation to help users understand forecasting performance and potential risks.

The analysis covers **January 2–31, 2026**, using data from Elexon BMRS.

### Key Features

* Interactive forecast-versus-actual visualisation.
* Configurable day-ahead forecast decision cutoff.
* Forecast selection based on publication time to avoid look-ahead bias.
* Evaluation using MAE, RMSE, forecast bias, MAPE, and percentile-based absolute errors.
* Error analysis by hour, delivery day, and forecast horizon.
* Flask API for serving analysis results.
* React-based interactive dashboard.
* Docker configuration for containerised execution.
* Vercel deployment.

## 2. Technology Stack

| Component              | Technology                   |
| ---------------------- | ---------------------------- |
| Frontend               | React, Vite, JavaScript      |
| Backend                | Python, Flask                |
| Data source            | Elexon BMRS                  |
| Visualisation          | Interactive dashboard charts |
| Deployment             | Vercel                       |
| Containerisation       | Docker, Docker Compose       |
| Development assistance | ChatGPT and Claude           |

## 3. Repository Structure

```text
.
├── api/
│   └── index.py
├── backend/
│   ├── app.py
│   ├── analysis.py
│   ├── prepare_data.py
│   └── data/
│       └── wind.json
├── frontend/
│   ├── src/
│   │   └── App.jsx
│   ├── package.json
│   └── ...
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── vercel.json
└── README.md
```

### Main Files and Directories

* **`api/index.py`** — Entry point for the Vercel serverless API.
* **`backend/app.py`** — Flask application and API routes.
* **`backend/analysis.py`** — Forecast selection, data comparison, and evaluation metrics.
* **`backend/prepare_data.py`** — Prepares and transforms the source data into the application's required format.
* **`backend/data/wind.json`** — Prepared wind forecast and actual generation data.
* **`frontend/src/App.jsx`** — Main React dashboard interface.
* **`frontend/package.json`** — Frontend dependencies and scripts.
* **`requirements.txt`** — Python dependencies.
* **`Dockerfile`** — Defines the application container image.
* **`docker-compose.yml`** — Configures containerised execution.
* **`vercel.json`** — Configures the Vercel build and routing.
* **`README.md`** — Project documentation and setup instructions.

## 4. Data Sources

The project uses two datasets from Elexon BMRS:

### WINDFOR

Provides wind generation forecasts.

### FUELHH

Provides half-hourly actual generation data. The dataset is filtered to include only records where `fuelType = WIND`.

The analysis focuses on national-level Great Britain wind generation for January 2–31, 2026.

**Data source:** https://www.elexon.co.uk/

## 5. Analysis Methodology

### 5.1 Forecast Selection

For each delivery day, the application selects the latest eligible forecast published before the configured day-ahead decision cutoff.

The default cutoff is **09:00 UTC**, and users can adjust it.

This prevents forecasts published after the simulated decision time from being used in the evaluation, avoiding look-ahead bias.

### 5.2 Data Alignment

Actual generation is provided at half-hourly intervals, while the forecasts are hourly.

The half-hourly actual generation values are aggregated into hourly averages and aligned with their corresponding forecast delivery periods.

This ensures that forecast and actual values are compared over matching time intervals.

### 5.3 Evaluation Metrics

The dashboard uses several metrics to evaluate forecasting performance.

| Metric         | Description                                                                           |
| -------------- | ------------------------------------------------------------------------------------- |
| MAE            | Mean Absolute Error; average absolute forecast error in MW.                           |
| RMSE           | Root Mean Squared Error; penalises larger errors more heavily.                        |
| Bias           | Mean signed error, calculated as forecast minus actual.                               |
| MAPE           | Mean Absolute Percentage Error; expresses errors relative to actual generation.       |
| P50, P90, P95  | Percentiles of absolute forecast error, showing the distribution of error magnitudes. |
| Normalised MAE | MAE expressed relative to mean actual generation.                                     |

A positive forecast bias indicates that forecast generation exceeds actual generation on average. A negative bias indicates underforecasting.

MAPE can become unstable when actual generation is close to zero, so it should be interpreted alongside MAE, RMSE, and other metrics.

## 6. Key Results

At the default 09:00 UTC decision cutoff, the dashboard reports the following results for the selected historical period:

| Metric                                |    Result |
| ------------------------------------- | --------: |
| Mean Absolute Error (MAE)             |  2,073 MW |
| Root Mean Squared Error (RMSE)        |  2,539 MW |
| Forecast Bias                         | +1,773 MW |
| Mean Absolute Percentage Error (MAPE) |     22.2% |
| Normalised MAE                        |     18.1% |
| P90 Absolute Error                    |  4,167 MW |
| P95 Absolute Error                    |  5,295 MW |
| Hourly Comparisons                    |       720 |

These results describe the selected historical period and should not be interpreted as guaranteed future performance.

## 7. Getting Started

### Prerequisites

Install the following:

* Python 3.10 or a compatible version.
* Node.js and npm.
* Git.

Docker is optional if you prefer containerised execution.

### Step 1: Clone the Repository

```bash
git clone https://github.com/shawarma-bro/ksjviuebrviu.git
cd ksjviuebrviu
```

### Step 2: Install Python Dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 4: Build the Frontend

```bash
npm run build
```

Return to the repository root:

```bash
cd ..
```

### Step 5: Start the Flask Application

```bash
python -m flask --app backend.app run --port 5000
```

Open the following address in your browser:

http://127.0.0.1:5000

### Running the Frontend in Development Mode

Open a separate terminal and run:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in the terminal.

### Running with Docker

From the repository root:

```bash
docker compose up --build
```

Follow the terminal output for startup status and the application URL.

## 8. API Endpoints

The application exposes API endpoints for retrieving dashboard information and evaluation results.

| Endpoint                | Purpose                                             |
| ----------------------- | --------------------------------------------------- |
| `/api/meta`             | Returns dashboard metadata.                         |
| `/api/metrics?cutoff=9` | Returns evaluation metrics for the selected cutoff. |

The API implementation is available in the backend code.

## 9. Deployment

The application is deployed on Vercel.

The deployment configuration builds the React frontend and routes API requests to the Python serverless entry point.

**Live application:** https://uk-wind-generation-forecast-pr4s-9uto3xenu.vercel.app/

## 10. Use of AI-Assisted Development Tools

ChatGPT and Claude were used as development assistance tools during this project.

Their assistance supported activities such as:

* Exploring implementation approaches.
* Understanding technical concepts and data-processing methods.
* Troubleshooting development and deployment issues.
* Reviewing code structure and possible improvements.
* Refining project documentation.

AI-generated suggestions were treated as assistance and checked against the project requirements and implementation. The tools supported the development workflow rather than replacing the project's data sources, analytical methodology, or validation.

## 11. Limitations

* The analysis covers one historical month and may not represent performance across other seasons.
* Forecast accuracy does not guarantee future wind generation or procurement outcomes.
* MAPE can be unstable when actual generation is close to zero.
* Historical forecast evaluation alone does not determine optimal electricity procurement decisions.
* The dashboard provides analytical insights rather than automated purchasing recommendations.

## 12. Future Improvements

Potential improvements include:

* Extending the analysis to additional months and seasons.
* Comparing forecast performance across different decision cutoffs.
* Adding further forecasting-error and operational-risk indicators.
* Automating periodic data updates and evaluation.
* Incorporating additional historical periods to assess seasonal variation.

## 13. Conclusion

This project combines historical electricity data, forecast-selection logic, statistical evaluation, and interactive visualisation in a full-stack application.

Its primary focus is evaluating wind generation forecast accuracy using only information available before a defined day-ahead decision cutoff. This provides a more realistic assessment of historical forecast performance and supports informed energy procurement planning.
