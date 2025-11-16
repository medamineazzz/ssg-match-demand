# app.py
# -------------------------------------------------------------
# SSG vs Match Demand — Simple Coach Tool (Streamlit)
# Design-focused edition + Catapult Logo + Green Pitch Visualization
# -------------------------------------------------------------

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
import numpy as np

from typing import Optional, Dict
import streamlit as st
from datetime import date

# --------------------------- Page Setup ---------------------------
st.set_page_config(page_title="SSG vs Match Demand", page_icon="⚽", layout="wide")

# Display Catapult logo (make sure PNG exists in repo)
st.image("CAT_horizontal_logo_lockup_white.png", width=180)

# --------------------------- Global CSS ---------------------------
st.markdown(
    """
    <style>
      body { background-color: #f9fafb; }
      .ssg-card { border:1px solid #e7e7e9; border-radius:16px; padding:18px; background:#fff; }
      .ssg-kpi { border:1px solid #f0f0f0; border-radius:14px; padding:12px; text-align:center; }
      .ssg-kpi .label { font-size:12px; color:#6b7280; }
      .ssg-kpi .value { font-size:20px; font-weight:700; }
      .ssg-pill { display:flex; align-items:center; justify-content:space-between; gap:10px; border:1px solid #ececec; border-radius:12px; padding:8px 10px; }
      .ssg-pill .l { font-size:12px; color:#6b7280; }
      .ssg-pill .r { font-size:13px; font-weight:700; border-radius:8px; padding:2px 8px; }
      .ssg-chip { display:flex; flex-direction:column; align-items:center; justify-content:center; border-radius:12px; padding:10px 12px; text-align:center; min-height:68px; }
      .ssg-chip .t { font-size:11px; opacity:.7; }
      .ssg-chip .v { font-weight:800; font-size:16px; }
      .ssg-shadow { box-shadow:0 1px 2px rgba(0,0,0,0.04), 0 4px 14px rgba(0,0,0,0.06); }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- Palette Helpers ---------------------------
DEFAULT_COLORS = {
    "under": "#FEE2E2",
    "under_text": "#991B1B",
    "on": "#D1FAE5",
    "on_text": "#065F46",
    "over": "#FFEDD5",
    "over_text": "#9A3412",
}

def style_for_pct(v: Optional[float], colors: dict) -> str:
    if v is None: return "background:#f4f4f5;color:#6b7280;"
    if v < 0.8: return f"background:{colors['under']};color:{colors['under_text']};"
    if v <= 1.0: return f"background:{colors['on']};color:{colors['on_text']};"
    return f"background:{colors['over']};color:{colors['over_text']};"

# --------------------------- Logic ---------------------------
def fmt_pct(v: Optional[float]) -> str:
    if v is None: return "-"
    try: return f"{v * 100:.0f}%"
    except: return "-"

def expected_demand(app: Optional[float]) -> Dict[str, str]:
    if not app: return {k: "" for k in ["TD","HSR","SPRINT","ACC","DEC","PL"]}
    small = app < 85
    medium = 85 <= app <= 120
    return {
        "TD": "MED" if small or medium else "HIGH",
        "HSR": "LOW" if small else ("MED" if medium else "HIGH"),
        "SPRINT": "LOW" if small else ("MED" if medium else "HIGH"),
        "ACC": "HIGH" if small else ("MED" if medium else "LOW"),
        "DEC": "HIGH" if small else ("MED" if medium else "LOW"),
        "PL": "HIGH" if small else ("MED" if medium else "LOW"),
    }

# --------------------------- Sidebar ---------------------------
with st.sidebar:
    st.header("⚙️ Appearance")
    col1, col2 = st.columns(2)
    with col1:
        under = st.color_picker("Under <80%", DEFAULT_COLORS["under"])
        on = st.color_picker("On 80–100%", DEFAULT_COLORS["on"])
    with col2:
        over = st.color_picker("Over >100%", DEFAULT_COLORS["over"])
        accent = st.color_picker("Accent", "#111827")

    colors = {
        "under": under, "on": on, "over": over,
        "under_text": DEFAULT_COLORS["under_text"],
        "on_text": DEFAULT_COLORS["on_text"],
        "over_text": DEFAULT_COLORS["over_text"],
        "accent": accent,
    }

# --------------------------- Header ---------------------------
st.markdown(
    f"""
<div class='ssg-card ssg-shadow' style='margin-top:10px;'>
  <div style='font-size:28px;font-weight:800;color:{colors['accent']}'>
    SSG vs Match Demand
  </div>
  <div style='color:#6b7280;margin-top:4px'>
    Plan
