# DeliveryIQ — Judge / Reviewer Guide

## 30-second code map

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard flow, filters, tabs, presentation |
| `src/analytics.py` | All Pandas calculations: loading, cleaning, required Q1-Q3, business and bonus analytics |
| `src/ai_service.py` | Groq API call only; receives calculated results and explains them |
| `src/styles.py` | UI styling only |
| `data/food_delivery_dataset.csv` | Official dataset |
| `docs/RUBRIC_AUDIT.md` | Requirement checklist |

## Core architecture

```text
CSV
 ↓
src/analytics.py
 Load → Clean → Analyze → Bonus Operations Analytics
 ↓
app.py
 Visualize → Interpret → Present
 ↓
src/ai_service.py
 Explain calculated results with Groq
```

## Important integrity points

1. **Q1, Q2 and Q3 are not hard-coded.** They are calculated in `src/analytics.py` with Pandas.
2. **Groq does not perform the primary analysis.** It receives an already-calculated payload.
3. **No machine-learning model is trained.** The optional risk score is a transparent deterministic business rule.
4. **API keys are not committed.** Use `GROQ_API_KEY` through environment variables or Streamlit Secrets.
5. **Cleaning is auditable.** The Data Audit tab shows missing values before/after, rows removed, values filled and reasons.

## Required competition functions

- `competition_q1()` — average delivery time grouped by road traffic density.
- `competition_q2()` — distance bands plus Pearson distance/time correlation.
- `competition_q3()` — average time grouped by weather + traffic combination.

## Bonus functions

- `peak_hour_analysis()`
- `festival_analysis()`
- `delay_kpis()`
- `risk_analysis()`
- `decision_summary()`

These functions are separated from the required answers so bonus assumptions do not contaminate the competition results.
