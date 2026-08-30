"""Core data pipeline and analytics for DeliveryIQ.

This module owns all calculations used by the dashboard. Competition answers are
computed with Pandas; no result is hard-coded and no machine-learning model is used.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


TRAFFIC_ORDER = ["Low", "Medium", "High", "Jam"]


# -----------------------------------------------------------------------------
# Data loading and cleaning
# -----------------------------------------------------------------------------


def load_data(path_or_buffer) -> pd.DataFrame:
    """Load the provided CSV file without modifying the source."""
    return pd.read_csv(path_or_buffer)


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the dataset using explicit, auditable rules.

    Missing-value policy:
    - Time_Orderd: DROP rows when missing. Exact order time cannot be inferred reliably,
      and only a small share of records are affected.
    - Delivery_person_Age: FILL using that rider's median age when available;
      otherwise use the dataset median.
    - Delivery_person_Ratings: FILL using that rider's median rating when available;
      otherwise use the dataset median.
    - Critical analysis fields (traffic, weather, distance, delivery time): DROP rows
      if missing because these fields are required to answer the competition questions.

    Invalid-value policy:
    - Invalid age/rating values are treated as missing and imputed using the same rules.
    - Non-positive distance or delivery time cannot be defensibly estimated, so those
      rows are removed.
    - Exact duplicates are removed.

    The function returns both the cleaned dataframe and a detailed cleaning report for
    the Data Audit tab.
    """
    data = df.copy()
    rows_before = len(data)

    # Capture missing values exactly as received.
    missing_before = data.isna().sum().to_dict()

    # Normalize strings.
    text_cols = data.select_dtypes(include="object").columns
    for col in text_cols:
        data[col] = data[col].astype("string").str.strip()

    # Safe numeric conversion.
    numeric_cols = [
        "Delivery_person_Age",
        "Delivery_person_Ratings",
        "Restaurant_latitude",
        "Restaurant_longitude",
        "Delivery_location_latitude",
        "Delivery_location_longitude",
        "Vehicle_condition",
        "multiple_deliveries",
        "Time_taken (min)",
        "distance_km",
    ]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    if "Order_Date" in data.columns:
        data["Order_Date"] = pd.to_datetime(
            data["Order_Date"], errors="coerce", dayfirst=True
        )

    # Remove exact duplicates.
    duplicates_before = int(data.duplicated().sum())
    data = data.drop_duplicates().copy()

    # Count invalid values before handling them.
    invalid_counts = {
        "invalid_age": int(
            (~data["Delivery_person_Age"].between(18, 70)
             & data["Delivery_person_Age"].notna()).sum()
        ) if "Delivery_person_Age" in data else 0,
        "invalid_rating": int(
            (~data["Delivery_person_Ratings"].between(0, 5)
             & data["Delivery_person_Ratings"].notna()).sum()
        ) if "Delivery_person_Ratings" in data else 0,
        "non_positive_distance": int(
            ((data["distance_km"] <= 0) & data["distance_km"].notna()).sum()
        ) if "distance_km" in data else 0,
        "non_positive_time": int(
            ((data["Time_taken (min)"] <= 0)
             & data["Time_taken (min)"].notna()).sum()
        ) if "Time_taken (min)" in data else 0,
    }

    # Invalid age/rating -> missing, then impute below.
    if "Delivery_person_Age" in data.columns:
        data.loc[
            data["Delivery_person_Age"].notna()
            & ~data["Delivery_person_Age"].between(18, 70),
            "Delivery_person_Age",
        ] = np.nan

    if "Delivery_person_Ratings" in data.columns:
        data.loc[
            data["Delivery_person_Ratings"].notna()
            & ~data["Delivery_person_Ratings"].between(0, 5),
            "Delivery_person_Ratings",
        ] = np.nan

    cleaning_actions = []

    # Remove rows with missing order time because exact timestamps should not be guessed.
    removed_missing_order_time = 0
    if "Time_Orderd" in data.columns:
        removed_missing_order_time = int(data["Time_Orderd"].isna().sum())
        if removed_missing_order_time:
            data = data.dropna(subset=["Time_Orderd"]).copy()
        cleaning_actions.append({
            "column": "Time_Orderd",
            "issue": f"{removed_missing_order_time} missing",
            "action": "Removed rows",
            "affected_rows": removed_missing_order_time,
            "reason": (
                "Order time is a precise event timestamp. Filling it with an average or "
                "made-up time could create false timing patterns, so affected rows are removed."
            ),
        })

    # Remove missing/invalid critical competition fields rather than fabricate outcomes.
    critical_cols = [
        "Road_traffic_density",
        "Weather_conditions",
        "distance_km",
        "Time_taken (min)",
    ]
    present_critical = [c for c in critical_cols if c in data.columns]

    # First remove non-positive distance/time.
    invalid_core_mask = pd.Series(False, index=data.index)
    if "distance_km" in data.columns:
        invalid_core_mask |= data["distance_km"].notna() & (data["distance_km"] <= 0)
    if "Time_taken (min)" in data.columns:
        invalid_core_mask |= (
            data["Time_taken (min)"].notna() & (data["Time_taken (min)"] <= 0)
        )
    removed_invalid_core = int(invalid_core_mask.sum())
    if removed_invalid_core:
        data = data.loc[~invalid_core_mask].copy()

    # Then remove rows missing the fields needed for Q1/Q2/Q3.
    missing_critical_mask = (
        data[present_critical].isna().any(axis=1)
        if present_critical else pd.Series(False, index=data.index)
    )
    removed_missing_critical = int(missing_critical_mask.sum())
    if removed_missing_critical:
        data = data.loc[~missing_critical_mask].copy()

    cleaning_actions.append({
        "column": "Competition-critical fields",
        "issue": (
            f"{removed_missing_critical} missing-field rows; "
            f"{removed_invalid_core} invalid distance/time rows"
        ),
        "action": "Removed rows",
        "affected_rows": removed_missing_critical + removed_invalid_core,
        "reason": (
            "Traffic, weather, distance and delivery time directly determine the required "
            "competition answers. Inventing these values would bias Q1–Q3."
        ),
    })

    # Impute age and rating after row-removal so only retained records are filled.
    fill_report = {}

    for col, label in [
        ("Delivery_person_Age", "Delivery person age"),
        ("Delivery_person_Ratings", "Delivery person rating"),
    ]:
        if col not in data.columns:
            continue

        missing_at_fill = int(data[col].isna().sum())
        rider_filled = 0
        fallback_filled = 0
        fallback_value = None

        if missing_at_fill:
            if "Delivery_person_ID" in data.columns:
                rider_median = data.groupby("Delivery_person_ID")[col].transform("median")
                can_fill_from_rider = data[col].isna() & rider_median.notna()
                rider_filled = int(can_fill_from_rider.sum())
                data.loc[can_fill_from_rider, col] = rider_median[can_fill_from_rider]

            remaining = int(data[col].isna().sum())
            if remaining:
                fallback_value = float(data[col].median())
                fallback_filled = remaining
                data[col] = data[col].fillna(fallback_value)

        fill_report[col] = {
            "missing_before_fill": missing_at_fill,
            "filled_from_rider_median": rider_filled,
            "filled_from_dataset_median": fallback_filled,
            "dataset_median": fallback_value,
        }

        reason = (
            f"{label} is a rider attribute, so the same rider's median is the most "
            "context-aware estimate. If that rider has no valid history, the overall "
            "median is used because it is robust to outliers and preserves the delivery record."
        )
        cleaning_actions.append({
            "column": col,
            "issue": f"{missing_at_fill} missing after row-removal",
            "action": "Filled values",
            "affected_rows": missing_at_fill,
            "reason": reason,
        })

    # Numeric speed required by the task.
    data["delivery_speed_kmh"] = (
        data["distance_km"] / (data["Time_taken (min)"] / 60)
    )

    missing_after = data.isna().sum().to_dict()

    report = {
        "rows_before": rows_before,
        "rows_after": len(data),
        "rows_removed_total": rows_before - len(data),
        "duplicates_removed": duplicates_before,
        "removed_missing_order_time": removed_missing_order_time,
        "removed_missing_critical": removed_missing_critical,
        "removed_invalid_core": removed_invalid_core,
        "invalid_counts": invalid_counts,
        "missing_before": missing_before,
        "missing_after": missing_after,
        "fill_report": fill_report,
        "cleaning_actions": cleaning_actions,
    }
    return data, report



# -----------------------------------------------------------------------------
# Required hackathon analysis
# -----------------------------------------------------------------------------

def basic_metrics(data: pd.DataFrame) -> dict:
    t = data["Time_taken (min)"]
    speed = data["delivery_speed_kmh"]
    return {
        "total_deliveries": int(len(data)),
        "avg_delivery_time": float(t.mean()),
        "min_delivery_time": float(t.min()),
        "max_delivery_time": float(t.max()),
        "avg_distance_km": float(data["distance_km"].mean()),
        "avg_speed_kmh": float(speed.mean()),
        "avg_rating": float(data["Delivery_person_Ratings"].mean()),
        "avg_age": float(data["Delivery_person_Age"].mean()),
    }


def competition_q1(data: pd.DataFrame) -> pd.DataFrame:
    result = (
        data.groupby("Road_traffic_density", dropna=False)["Time_taken (min)"]
        .agg(avg_delivery_time="mean", median_delivery_time="median", deliveries="size")
        .reset_index()
    )
    result["Road_traffic_density"] = pd.Categorical(
        result["Road_traffic_density"],
        categories=TRAFFIC_ORDER,
        ordered=True,
    )
    return result.sort_values("avg_delivery_time", ascending=False)


def competition_q2(data: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    bins = [0, 5, 10, 15, np.inf]
    labels = ["0–5 km", "5–10 km", "10–15 km", "15+ km"]
    temp = data.copy()
    temp["distance_band"] = pd.cut(
        temp["distance_km"], bins=bins, labels=labels, include_lowest=True
    )
    result = (
        temp.groupby("distance_band", observed=False)["Time_taken (min)"]
        .agg(avg_delivery_time="mean", median_delivery_time="median", deliveries="size")
        .reset_index()
    )
    correlation = float(
        data[["distance_km", "Time_taken (min)"]].corr().iloc[0, 1]
    )
    return result, correlation


def competition_q3(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby(["Weather_conditions", "Road_traffic_density"])["Time_taken (min)"]
        .agg(avg_delivery_time="mean", deliveries="size")
        .reset_index()
        .sort_values("avg_delivery_time", ascending=False)
    )



# -----------------------------------------------------------------------------
# Business interpretation
# -----------------------------------------------------------------------------

def business_insights(data: pd.DataFrame) -> list[dict]:
    q1 = competition_q1(data)
    q2, corr = competition_q2(data)
    q3 = competition_q3(data)

    worst_traffic = q1.iloc[0]
    best_traffic = q1.iloc[-1]
    worst_combo = q3.iloc[0]

    festival = (
        data.groupby("Festival")["Time_taken (min)"].mean().sort_values(ascending=False)
        if "Festival" in data.columns else pd.Series(dtype=float)
    )

    insights = [
        {
            "title": "Traffic is the clearest operational bottleneck",
            "finding": (
                f"{worst_traffic['Road_traffic_density']} traffic averages "
                f"{worst_traffic['avg_delivery_time']:.1f} min versus "
                f"{best_traffic['avg_delivery_time']:.1f} min in "
                f"{best_traffic['Road_traffic_density']} traffic."
            ),
            "action": (
                "Use traffic-aware batching, realistic ETAs, and extra rider capacity "
                "during jam periods instead of applying one SLA to every traffic condition."
            ),
        },
        {
            "title": "Distance materially increases delivery time",
            "finding": (
                f"The distance/time correlation is {corr:.2f}. "
                f"Average time rises from {q2.iloc[0]['avg_delivery_time']:.1f} min "
                f"for {q2.iloc[0]['distance_band']} to "
                f"{q2.iloc[-1]['avg_delivery_time']:.1f} min for {q2.iloc[-1]['distance_band']}."
            ),
            "action": (
                "Set delivery-zone thresholds, prioritize nearer riders, and adjust promised "
                "ETAs for longer-distance orders."
            ),
        },
        {
            "title": "Weather + traffic create a high-risk combination",
            "finding": (
                f"{worst_combo['Weather_conditions']} weather with "
                f"{worst_combo['Road_traffic_density']} traffic has the highest observed "
                f"average delivery time: {worst_combo['avg_delivery_time']:.1f} min."
            ),
            "action": (
                "Trigger surge staffing, reduce batching, widen ETA buffers, and proactively "
                "message customers when this combination occurs."
            ),
        },
    ]

    if len(festival) >= 2:
        slow = festival.index[0]
        fast = festival.index[-1]
        insights.append(
            {
                "title": "Festival periods deserve a separate operating playbook",
                "finding": (
                    f"Festival={slow} averages {festival.iloc[0]:.1f} min versus "
                    f"{festival.iloc[-1]:.1f} min for Festival={fast}."
                ),
                "action": (
                    "Forecast rider demand and restaurant preparation load separately for festival days."
                ),
            }
        )

    return insights




# -----------------------------------------------------------------------------
# Bonus operational analytics (transparent rules; no ML)
# -----------------------------------------------------------------------------

def add_operational_features(
    data: pd.DataFrame,
    delay_threshold: float = 30.0,
) -> pd.DataFrame:
    """
    Add transparent, non-ML operational features.

    - order_hour: parsed from Time_Orderd
    - is_delayed: delivery time > user-selected SLA threshold
    - risk_score: simple rules based on traffic, weather, distance and batching
    - risk_level: Low / Medium / High

    The risk score is intentionally rule-based, not a trained ML model.
    """
    temp = data.copy()

    if "Time_Orderd" in temp.columns:
        parsed_time = pd.to_datetime(
            temp["Time_Orderd"].astype("string"),
            format="%H:%M",
            errors="coerce",
        )
        temp["order_hour"] = parsed_time.dt.hour

    temp["is_delayed"] = temp["Time_taken (min)"] > float(delay_threshold)

    score = pd.Series(0, index=temp.index, dtype="int64")

    if "Road_traffic_density" in temp.columns:
        score += temp["Road_traffic_density"].map(
            {"Low": 0, "Medium": 0, "High": 1, "Jam": 2}
        ).fillna(0).astype(int)

    if "Weather_conditions" in temp.columns:
        difficult_weather = {"Stormy", "Fog", "Sandstorms"}
        score += temp["Weather_conditions"].isin(difficult_weather).astype(int)

    if "distance_km" in temp.columns:
        score += (temp["distance_km"] >= 10).astype(int)

    if "multiple_deliveries" in temp.columns:
        score += (temp["multiple_deliveries"] >= 2).astype(int)

    temp["risk_score"] = score
    temp["risk_level"] = pd.cut(
        score,
        bins=[-1, 1, 2, np.inf],
        labels=["Low", "Medium", "High"],
    ).astype("string")

    return temp


def peak_hour_analysis(
    data: pd.DataFrame,
    delay_threshold: float = 30.0,
) -> pd.DataFrame:
    temp = add_operational_features(data, delay_threshold)
    if "order_hour" not in temp.columns:
        return pd.DataFrame(
            columns=["order_hour", "avg_delivery_time", "deliveries", "delayed_pct"]
        )

    result = (
        temp.dropna(subset=["order_hour"])
        .groupby("order_hour")
        .agg(
            avg_delivery_time=("Time_taken (min)", "mean"),
            deliveries=("Time_taken (min)", "size"),
            delayed_pct=("is_delayed", lambda s: s.mean() * 100),
        )
        .reset_index()
        .sort_values("order_hour")
    )
    result["order_hour"] = result["order_hour"].astype(int)
    return result


def festival_analysis(
    data: pd.DataFrame,
    delay_threshold: float = 30.0,
) -> pd.DataFrame:
    temp = add_operational_features(data, delay_threshold)
    if "Festival" not in temp.columns:
        return pd.DataFrame(
            columns=["Festival", "avg_delivery_time", "deliveries", "delayed_pct"]
        )
    return (
        temp.groupby("Festival", dropna=False)
        .agg(
            avg_delivery_time=("Time_taken (min)", "mean"),
            deliveries=("Time_taken (min)", "size"),
            delayed_pct=("is_delayed", lambda s: s.mean() * 100),
        )
        .reset_index()
        .sort_values("avg_delivery_time", ascending=False)
    )


def delay_kpis(
    data: pd.DataFrame,
    delay_threshold: float = 30.0,
) -> dict:
    temp = add_operational_features(data, delay_threshold)
    delayed = temp["is_delayed"]
    delayed_count = int(delayed.sum())
    total = int(len(temp))
    on_time_count = total - delayed_count

    return {
        "threshold_min": float(delay_threshold),
        "total": total,
        "delayed_count": delayed_count,
        "on_time_count": on_time_count,
        "delayed_pct": float(delayed.mean() * 100) if total else 0.0,
        "on_time_pct": float((~delayed).mean() * 100) if total else 0.0,
        "avg_delayed_time": float(
            temp.loc[delayed, "Time_taken (min)"].mean()
        ) if delayed_count else 0.0,
    }


def risk_analysis(
    data: pd.DataFrame,
    delay_threshold: float = 30.0,
) -> pd.DataFrame:
    temp = add_operational_features(data, delay_threshold)
    order = ["Low", "Medium", "High"]
    result = (
        temp.groupby("risk_level", observed=False)
        .agg(
            deliveries=("Time_taken (min)", "size"),
            avg_delivery_time=("Time_taken (min)", "mean"),
            delayed_pct=("is_delayed", lambda s: s.mean() * 100),
            avg_distance_km=("distance_km", "mean"),
        )
        .reset_index()
    )
    result["risk_level"] = pd.Categorical(
        result["risk_level"], categories=order, ordered=True
    )
    return result.sort_values("risk_level")


def decision_summary(
    data: pd.DataFrame,
    delay_threshold: float = 30.0,
) -> dict:
    q1 = competition_q1(data)
    q2, corr = competition_q2(data)
    q3 = competition_q3(data)
    peak = peak_hour_analysis(data, delay_threshold)
    festival = festival_analysis(data, delay_threshold)
    delay = delay_kpis(data, delay_threshold)
    risk = risk_analysis(data, delay_threshold)

    worst_hour = None
    if not peak.empty:
        row = peak.sort_values("avg_delivery_time", ascending=False).iloc[0]
        worst_hour = {
            "hour": int(row["order_hour"]),
            "avg_delivery_time": float(row["avg_delivery_time"]),
            "delayed_pct": float(row["delayed_pct"]),
        }

    festival_impact = None
    if len(festival) >= 2:
        yes = festival[festival["Festival"].astype(str).str.lower() == "yes"]
        no = festival[festival["Festival"].astype(str).str.lower() == "no"]
        if not yes.empty and not no.empty:
            festival_impact = {
                "festival_avg": float(yes.iloc[0]["avg_delivery_time"]),
                "non_festival_avg": float(no.iloc[0]["avg_delivery_time"]),
                "difference_min": float(
                    yes.iloc[0]["avg_delivery_time"] - no.iloc[0]["avg_delivery_time"]
                ),
            }

    high_risk = None
    high = risk[risk["risk_level"].astype(str) == "High"]
    if not high.empty:
        high_risk = {
            "deliveries": int(high.iloc[0]["deliveries"]),
            "avg_delivery_time": float(high.iloc[0]["avg_delivery_time"]),
            "delayed_pct": float(high.iloc[0]["delayed_pct"]),
        }

    return {
        "worst_traffic": {
            "condition": str(q1.iloc[0]["Road_traffic_density"]),
            "avg_delivery_time": float(q1.iloc[0]["avg_delivery_time"]),
        },
        "distance_correlation": float(corr),
        "worst_weather_traffic": {
            "weather": str(q3.iloc[0]["Weather_conditions"]),
            "traffic": str(q3.iloc[0]["Road_traffic_density"]),
            "avg_delivery_time": float(q3.iloc[0]["avg_delivery_time"]),
        },
        "delay": delay,
        "worst_hour": worst_hour,
        "festival_impact": festival_impact,
        "high_risk": high_risk,
    }


# -----------------------------------------------------------------------------
# AI handoff payload: calculated results only
# -----------------------------------------------------------------------------

def ai_payload(
    data: pd.DataFrame,
    delay_threshold: float = 30.0,
) -> dict:
    metrics = basic_metrics(data)
    q1 = competition_q1(data)
    q2, corr = competition_q2(data)
    q3 = competition_q3(data)
    peak = peak_hour_analysis(data, delay_threshold)
    festival = festival_analysis(data, delay_threshold)
    risk = risk_analysis(data, delay_threshold)
    delay = delay_kpis(data, delay_threshold)

    return {
        "basic_metrics": metrics,
        "traffic_analysis": q1.to_dict(orient="records"),
        "distance_bands": q2.to_dict(orient="records"),
        "distance_time_correlation": corr,
        "weather_traffic_top5": q3.head(5).to_dict(orient="records"),
        "delay_sla_assumption": delay,
        "peak_hours_top5": (
            peak.sort_values("avg_delivery_time", ascending=False)
            .head(5)
            .to_dict(orient="records")
            if not peak.empty else []
        ),
        "festival_analysis": festival.to_dict(orient="records"),
        "rule_based_risk_analysis": risk.to_dict(orient="records"),
        "business_insights": business_insights(data),
    }

