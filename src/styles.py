"""Streamlit presentation styles for DeliveryIQ."""

import streamlit as st


APP_CSS = r'''
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }
    .hero {
        padding: 1.7rem 1.55rem 1.35rem 1.55rem;
        border-radius: 20px;
        background: linear-gradient(120deg, rgba(34,197,94,.14), rgba(59,130,246,.10));
        border: 1px solid rgba(125,125,125,.18);
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.05rem;
        line-height: 1.15;
    }
    .hero p {
        margin: .45rem 0 0 0;
        opacity: .76;
        font-size: 1rem;
    }
    .eyebrow {
        font-size: .78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        opacity: .62;
        font-weight: 700;
        margin-bottom: .35rem;
    }
    .finding-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .8rem;
        margin: .55rem 0 1rem 0;
    }
    .finding-card {
        border: 1px solid rgba(125,125,125,.18);
        border-radius: 16px;
        padding: 1rem 1.05rem;
        background: rgba(255,255,255,.68);
        min-height: 120px;
    }
    .finding-card .kicker {
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .05em;
        opacity: .58;
        font-weight: 700;
    }
    .finding-card .value {
        font-size: 1.55rem;
        font-weight: 800;
        margin: .2rem 0 .15rem 0;
    }
    .finding-card .desc {
        font-size: .9rem;
        opacity: .72;
        line-height: 1.35;
    }
    .section-card {
        border: 1px solid rgba(125,125,125,.18);
        border-radius: 16px;
        padding: 1rem 1.05rem;
        margin-bottom: .8rem;
    }
    .insight-card {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(125,125,125,.20);
        border-radius: 14px;
        margin-bottom: .75rem;
    }
    .small-muted {opacity:.7; font-size:.9rem;}
    .judge-banner {
        border-radius: 16px;
        padding: .9rem 1rem;
        border: 1px solid rgba(34,197,94,.25);
        background: rgba(34,197,94,.08);
        margin-bottom: .8rem;
    }
    .decision-card {
        border: 1px solid rgba(125,125,125,.18);
        border-radius: 15px;
        padding: .95rem 1rem;
        min-height: 155px;
        background: rgba(248,250,252,.75);
    }
    .decision-card b {font-size: 1.02rem;}
    
    .sidebar-note {
        font-size: .86rem;
        opacity: .72;
        line-height: 1.35;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    @media (max-width: 900px) {
        .finding-grid { grid-template-columns: 1fr; }
        .hero h1 { font-size: 1.6rem; }
    }
    
'''


def apply_app_styles() -> None:
    """Apply the dashboard CSS in one place."""
    st.markdown(f"<style>{APP_CSS}</style>", unsafe_allow_html=True)
