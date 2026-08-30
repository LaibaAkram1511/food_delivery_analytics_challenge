# Hackathon Task A — Rubric Audit

## A. Load & Understand — COMPLETE
- CSV loaded with Pandas.
- Dashboard explicitly displays row count and column count.
- First 10 rows displayed.
- All column names displayed.
- All data types displayed.
- Missing values and missing percentages displayed.
- Duplicate count and duplicate-record investigation displayed.
- Descriptive dataset summary displayed.

## B. Clean the Data — COMPLETE
- Text whitespace stripped.
- Numeric types converted safely.
- Order_Date parsed to datetime.
- Exact duplicates removed.
- Invalid age, rating, non-positive distance, and non-positive time checked.
- Invalid counts are reported before cleaning.
- Genuine missing values are preserved rather than fabricated.
- Cleaning decisions documented in README.md and dashboard.

## C. Basic Analysis — COMPLETE
- Total deliveries.
- Average/minimum/maximum delivery time.
- Average delivery distance.
- Numeric average delivery speed derived in km/h.
- Average rider rating.
- Average rider age.

## D. Competition Questions — COMPLETE / PROGRAMMATIC
- Q1 traffic impact via Pandas groupby.
- Q2 distance impact via distance bands + Pearson correlation.
- Q3 weather + traffic combination via Pandas groupby.
- No competition answer is hard-coded.

## E. Visualizations — COMPLETE
- Required traffic bar chart.
- Required distance-vs-time scatter plot.
- Weather x Traffic risk heatmap.
- City comparison.
- Vehicle comparison.
- Multiple-delivery impact chart.
- Rider-rating comparison.
- Order-date trend chart.

## F. Business Insights — COMPLETE
- Traffic bottleneck insight + action.
- Distance impact insight + action.
- Weather/traffic risk insight + action.
- Additional festival insight where applicable.

## G. AI-Powered Explanation — IMPLEMENTED
- Groq API integration.
- Python/Pandas calculates results first.
- Only calculated JSON payload is sent to the LLM.
- API key is read from environment/Streamlit Secrets and is not hard-coded.
- A real GROQ_API_KEY is required at runtime to generate the submitted AI explanation/screenshot.

## Bonus Features — IMPLEMENTED
- Streamlit dashboard.
- Interactive Plotly charts.
- Filters for city, weather, and vehicle.
- City/vehicle/weather comparisons.
- Download filtered clean data.
- AI-generated recommendations/executive brief.
- Deployment-ready Streamlit configuration.

## Still required from student before final submission
1. Add a real GROQ_API_KEY in local environment or Streamlit Cloud Secrets.
2. Click Generate Executive Brief and capture its output.
3. Deploy the Streamlit app.
4. Take screenshots of the working dashboard for submission.
5. Practice explaining the code and findings.


## Extra competitive polish

- [x] Judge Mode / 60-second executive story
- [x] Peak-hour analysis
- [x] Festival vs non-festival analysis
- [x] User-adjustable SLA delay KPI with assumption disclosure
- [x] Transparent non-ML risk score
- [x] Operations-priority recommendations
