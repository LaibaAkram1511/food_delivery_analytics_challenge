# DeliveryIQ — Food Delivery Analytics Hackathon

A deployment-ready Python/Pandas analytics dashboard for the **Food Delivery Analytics Challenge**.

## Why this version is built to score highly

The judging rubric awards marks for loading/understanding, cleaning, Pandas analysis, accuracy, visualizations, business insights, AI integration, code organization, and presentation. This project explicitly covers every category and adds optional bonus features: Streamlit, filters, extra comparisons, Plotly charts, downloads, an AI executive brief, and a risk-matrix visualization.

## Competition answers from the provided dataset

These are calculated by Python/Pandas, not hard-coded:

- **Q1 — Traffic impact:** Jam traffic has the highest average delivery time.
- **Q2 — Distance impact:** Distance and delivery time are positively related. The dashboard reports the live correlation and distance-band averages.
- **Q3 — Combined conditions:** The dashboard calculates the weather + traffic combination with the highest average time.

Run the app to see exact values and filtered results.

## Project structure

The project is intentionally organized so a judge can understand it in seconds:

```text
DeliveryIQ_Hackathon_FINAL_CLEAN/
├── app.py                      # Streamlit UI and dashboard flow
├── requirements.txt            # Python dependencies
├── README.md                   # Setup, methodology, deployment, demo guide
├── .env.example                # Safe Groq environment-variable example
├── .gitignore                  # Prevents secrets/cache from being committed
├── .streamlit/
│   └── config.toml             # Streamlit theme/configuration
├── src/
│   ├── __init__.py
│   ├── analytics.py            # Loading, cleaning, Q1-Q3, bonus analytics
│   ├── ai_service.py           # Groq explanation layer only
│   └── styles.py               # Dashboard CSS/presentation styling
├── data/
│   └── food_delivery_dataset.csv   # Official competition dataset
├── assets/
│   └── charts/                 # Required exported chart images
├── reports/
│   ├── analysis_results.json   # Verified result snapshot
│   ├── cleaning_summary.json   # Cleaning audit snapshot
│   └── ultimate_validation.json# Bonus-feature validation snapshot
└── docs/
    ├── RUBRIC_AUDIT.md         # Requirement-by-requirement checklist
    └── JUDGE_GUIDE.md          # Quick code/map guide for evaluation
```

### Where to look first

- **Want to run the project?** Start with `app.py`.
- **Want to verify the calculations?** Open `src/analytics.py`.
- **Want to inspect AI usage?** Open `src/ai_service.py`. The LLM does not calculate Q1-Q3.
- **Want to review cleaning decisions?** See the Data Audit tab and `README.md`.
- **Want to verify rubric coverage?** Open `docs/RUBRIC_AUDIT.md`.

## Cleaning decisions

The project uses a mixed cleaning strategy instead of treating every missing value the same way:

1. **`Time_Orderd` missing values → remove those rows.**  
   An order timestamp is an exact event and cannot be reliably guessed. Filling it with a mean/median time could create false time-of-day patterns.

2. **`Delivery_person_Age` missing values → fill.**  
   First use the median age for the same `Delivery_person_ID`; if that rider has no valid age history, use the overall dataset median. Age is a rider attribute, so deleting an entire delivery because age is missing would waste useful order-performance data.

3. **`Delivery_person_Ratings` missing values → fill.**  
   First use the same rider's median rating; if unavailable, use the overall median. Median is preferred because it is robust to outliers.

4. **Missing traffic/weather/distance/delivery-time values → remove affected rows.**  
   These variables directly determine the competition questions. Fabricating them would bias the required answers.

5. **Invalid age/rating values → treat as missing and fill using the same rider-median/fallback-median rule.**

6. **Non-positive distance or delivery time → remove affected rows.**  
   These values are not physically meaningful for this analysis and should not be invented.

7. **Exact duplicate rows → remove.**

8. Add `delivery_speed_kmh = distance_km / (delivery_minutes / 60)` for the required numeric average-speed analysis.

The **Data Audit** tab shows missing values before cleaning, treatment counts, reasons, missing values after cleaning, duplicate/invalid checks, and a cleaned-data preview.

## Run locally

```bash
python -m venv .venv
```

Windows (standard):

```bash
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If a school/work PC blocks virtual-environment executables with Device Guard, use system Python instead:

```bash
py -m pip install --user -r requirements.txt
py -m streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## AI integration

The primary analysis is always done by Python/Pandas. The LLM is used only to explain already-calculated results.

Never hard-code a key.

For local use:

```bash
set GROQ_API_KEY=your_key_here
```

On macOS/Linux:

```bash
export GROQ_API_KEY=your_key_here
```

You can also copy `.env.example` as a reference, but do not commit a real key.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload the project files to the repository root.
3. Go to Streamlit Community Cloud and create a new app from the repo.
4. Choose `app.py` as the entry file.
5. Open **App settings → Secrets** and add:

```toml
GROQ_API_KEY = "your-real-key"
GROQ_MODEL = "openai/gpt-oss-20b"
```

6. Deploy.

Because `data/food_delivery_dataset.csv` is included in the repo, the app runs without asking a judge to upload anything.

## 60-second judge demo script

> “This dashboard analyzes all delivery records with Pandas. At the top, I show the operational KPIs. The first tab proves dataset loading/understanding; the second tab answers all three required competition questions programmatically. The second tab lets us explore city, vehicle, batching, ratings, and timing. The third tab converts those results into business actions. The fourth tab demonstrates responsible AI integration: Python calculates every number first, and the LLM only explains the calculated JSON payload. The final tab shows the cleaning audit, so every transformation is transparent and reproducible.”

## What to explain if judges ask

### Why no ML?
The challenge explicitly does not require it. For this task, descriptive analytics is more interpretable and directly tied to operations.

### Why keep some missing values?
Imputing values can fabricate evidence. Since the required metrics can be computed from valid observations, a conservative approach is easier to defend.

### Why derive numeric speed?
The provided `delivery_speed` column contains categories (`Fast`, `Average`, `Slow`). The task asks for average delivery speed, so a numeric km/h measure is derived from distance and time.

### Why a heatmap?
The third competition question is a two-variable interaction. A weather × traffic risk matrix communicates the interaction much faster than a table.

## Final submission checklist

- [x] Python project
- [x] Provided CSV
- [x] Dataset loading
- [x] Dataset rows, columns, names, dtypes, missing values & duplicate investigation
- [x] Missing-value investigation
- [x] Data cleaning
- [x] Basic statistics
- [x] Three required questions
- [x] Two+ visualizations
- [x] Three+ business insights
- [x] AI explanation
- [x] `requirements.txt`
- [x] `README.md`
- [x] Clean folder structure
- [x] Code comments
- [x] Deployment-ready
- [ ] Add screenshots after running the deployed app


## Reusable CSV upload

The dashboard keeps the CSV upload option. If no upload is provided, it automatically uses the official hackathon dataset.

For another CSV, the current version expects the same or a compatible food-delivery schema because the competition questions depend on specific columns such as `Road_traffic_density`, `Weather_conditions`, `distance_km`, and `Time_taken (min)`.

This is intentional: it keeps the project reusable without weakening the correctness of the hackathon-specific analysis.


## Groq Free-tier model
The app defaults to `openai/gpt-oss-20b`, which Groq lists under its Free Plan rate limits. If `GROQ_MODEL` was previously set to another model, change or remove that setting and restart Streamlit.


## Standout bonus features

This final version adds five demo-focused features without using machine learning:

1. **Judge Mode** — uses the full cleaned dataset and surfaces a concise 60-second executive story while hiding exploratory filters.
2. **Peak-hour analysis** — parses `Time_Orderd` and identifies the slowest order hours using Pandas.
3. **Festival impact** — compares delivery time and delay rate for festival vs non-festival records.
4. **Adjustable SLA / delay KPI** — defaults to 30 minutes, but is explicitly labelled as a user-selected analytical assumption rather than a dataset-provided rule.
5. **Transparent rule-based risk score** — combines traffic, difficult weather, distance, and multiple deliveries into Low/Medium/High operational risk. This is a deterministic business rule, **not ML**.

### Risk-score logic

- Jam traffic: +2
- High traffic: +1
- Fog, Stormy, or Sandstorms: +1
- Distance ≥ 10 km: +1
- Multiple deliveries ≥ 2: +1
- Score 0–1: Low
- Score 2: Medium
- Score 3+: High

The dashboard validates this rule against observed delivery time and the selected delay threshold. The score is intentionally simple so the student can explain every line to judges.
