# app.py
# -------------------------------------------------------------
# SSG vs Match Demand — Simple Coach Tool (Streamlit)
# Design-focused edition + Catapult Logo + Pitch Visualization
# Tabs:
# 1) Planner → APP + Expected Demand (pills) + Pitch viz
# 2) Quick %MDP → % of match with colored chips + progress bars
# -------------------------------------------------------------

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import numpy as np

from typing import Optional, Dict
import streamlit as st
from datetime import date

# --------------------------- Page Setup ---------------------------
st.set_page_config(page_title="SSG vs Match Demand", page_icon="⚽", layout="wide")

# Display Catapult logo at the top (make sure this file is in your repo)
st.image("CAT_horizontal_logo_lockup_white.png", width=180)

# Global CSS (clean cards, pills, chips)
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
    if v is None:
        return "background:#f4f4f5;color:#6b7280;"
    if v < 0.8:
        return f"background:{colors['under']};color:{colors['under_text']};"
    if v <= 1.0:
        return f"background:{colors['on']};color:{colors['on_text']};"
    return f"background:{colors['over']};color:{colors['over_text']};"

# --------------------------- Business Logic ---------------------------

def fmt_pct(v: Optional[float]) -> str:
    if v is None:
        return "-"
    try:
        return f"{v * 100:.0f}%"
    except Exception:
        return "-"

def expected_demand(app: Optional[float]) -> Dict[str, str]:
    if not app:
        return {k: "" for k in ["TD", "HSR", "SPRINT", "ACC", "DEC", "PL"]}
    small = app < 85
    medium = 85 <= app <= 120
    return {
        "TD": "MED" if (small or medium) else "HIGH",
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
        "under": under, "under_text": DEFAULT_COLORS["under_text"],
        "on": on, "on_text": DEFAULT_COLORS["on_text"],
        "over": over, "over_text": DEFAULT_COLORS["over_text"],
        "accent": accent,
    }

# --------------------------- Header ---------------------------
st.markdown(
    f"""
<div class='ssg-card ssg-shadow' style='margin-top:10px;'>
  <div style='font-size:28px;font-weight:800;color:{colors['accent']}'>SSG vs Match Demand</div>
  <div style='color:#6b7280;margin-top:4px'>
    Plan SSGs, estimate expected demand, and compare against match peaks.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# --------------------------- Tabs ---------------------------
planner_tab, quick_tab = st.tabs(["🗺️ Planner", "⚡ Quick %MDP"])

# ========================== PLANNER TAB ==========================
with planner_tab:
    st.markdown("<div class='ssg-card ssg-shadow'>", unsafe_allow_html=True)
    st.subheader("Planner")

    # ---- Inputs ----
    colA, colB, colC = st.columns(3)
    with colA:
        _date = st.date_input("Date", value=date.today())
        format_ = st.selectbox("Format", ["4v4", "6v6", "7v7", "8v8", "10v10"], index=0)
        players = st.number_input("Players on Pitch (exclude GK)", min_value=2, max_value=22, value=8)
    with colB:
        length = st.number_input("Pitch Length (m)", min_value=10, max_value=120, value=30)
        width = st.number_input("Pitch Width (m)", min_value=10, max_value=90, value=40)
        sets = st.number_input("Sets", min_value=1, max_value=12, value=3)
    with colC:
        work = st.number_input("Work per Set (min)", min_value=1, max_value=30, value=3)
        rest = st.number_input("Rest between Sets (sec)", min_value=15, max_value=300, value=90)

    # ---- Calculations ----
    area = length * width
    app = (area / players) if players else 0
    total_work = sets * work
    total_rest = (sets * rest) / 60
    total_session = total_work + total_rest

    # ---- KPI Cards ----
    k1, k2, k3, k4, k5 = st.columns(5)
    labels = ["Pitch Area (m²)", "Area/Player (m²)", "Total Work (min)", "Total Rest (min)", "Session (min)"]
    values = [f"{area:.0f}", f"{app:.1f}", f"{total_work:.0f}", f"{total_rest:.0f}", f"{total_session:.0f}"]
    for col, label, value in zip([k1, k2, k3, k4, k5], labels, values):
        with col:
