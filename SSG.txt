# app.py
# -------------------------------------------------------------
# SSG vs Match Demand — Simple Coach Tool (Streamlit)
# Two tabs only:
# 1) Planner → APP + Expected Demand chips (coach-ready)
# 2) Quick %MDP → Paste one player's per-minute Match MDP and SSG block → % of match chips
# -------------------------------------------------------------

import json
from typing import Optional, Dict
import streamlit as st

# --------------------------- Utilities ---------------------------

def fmt_pct(v: Optional[float]) -> str:
    if v is None:
        return "-"
    try:
        return f"{v * 100:.0f}%"
    except Exception:
        return "-"

def class_for_pct(v: Optional[float]) -> str:
    if v is None:
        return "opacity-50"
    if v < 0.8:
        return "bg-red-100 text-red-800"
    if v <= 1.0:
        return "bg-green-100 text-green-800"
    return "bg-orange-100 text-orange-800"

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

# --------------------------- Streamlit App ---------------------------

st.set_page_config(page_title="SSG vs Match Demand", page_icon="⚽", layout="centered")
st.title("SSG vs Match Demand — Simple Coach Tool")

planner_tab, quick_tab = st.tabs(["Planner", "Quick %MDP"])

# ---------- PLANNER ----------
with planner_tab:
    st.subheader("Planner")

    colA, colB, colC = st.columns(3)
    with colA:
        date = st.date_input("Date")
        format_ = st.selectbox("Format", ["4v4", "6v6", "7v7", "8v8", "10v10"])
        players = st.number_input("Players on Pitch (exclude GK)", min_value=2, max_value=22, value=8)
    with colB:
        length = st.number_input("Pitch Length (m)", min_value=10, max_value=120, value=30)
        width = st.number_input("Pitch Width (m)", min_value=10, max_value=90, value=40)
        sets = st.number_input("Sets", min_value=1, max_value=12, value=3)
    with colC:
        work = st.number_input("Work per Set (min)", min_value=1, max_value=30, value=3)
        rest = st.number_input("Rest between Sets (sec)", min_value=15, max_value=300, value=90)

    area = length * width
    app = (area / players) if players else 0
    total_work = sets * work
    total_rest = (sets * rest) / 60
    total_session = total_work + total_rest

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Pitch Area (m²)", f"{area:.0f}")
    k2.metric("Area/Player (m²)", f"{app:.1f}" if app else "-")
    k3.metric("Total Work (min)", f"{total_work:.0f}")
    k4.metric("Total Rest (min)", f"{total_rest:.0f}")
    k5.metric("Session (min)", f"{total_session:.0f}")

    st.markdown("**Expected Demand (from APP)**")
    exp = expected_demand(app)

    t1, t2, t3, t4, t5, t6 = st.columns(6)
    for (label, val, col) in zip(["TD", "HSR", "SPRINT", "ACC", "DEC", "PL"], [exp['TD'], exp['HSR'], exp['SPRINT'], exp['ACC'], exp['DEC'], exp['PL']], [t1, t2, t3, t4, t5, t6]):
        with col:
            st.markdown(f"<div style='border:1px solid #ddd;border-radius:10px;padding:6px;text-align:center'><b>{label}</b><br>{val}</div>", unsafe_allow_html=True)

    st.caption("APP guide: Small <85 → high ACC/DEC & PL · Medium 85–120 → balanced · Large >120 → more HSR & sprints")

# ---------- QUICK %MDP ----------
with quick_tab:
    st.subheader("Quick % of Match (single player / block)")

    left, right = st.columns(2)
    with left:
        st.markdown("**Match MDP — per minute**")
        mdp_td = st.number_input("TD/min (m)", value=180.0)
        mdp_hmld = st.number_input("HMLD/min (m)", value=30.0)
        mdp_acc = st.number_input("ACC/min (count)", value=0.9)
        mdp_dec = st.number_input("DEC/min (count)", value=0.8)
        mdp_hsr = st.number_input("HSR/min (m)", value=3.5)
        mdp_pl = st.number_input("PlayerLoad/min", value=12.0)
    with right:
        st.markdown("**SSG Block — per minute**")
        ssg_td = st.number_input("TD/min (m) ", value=165.0)
        ssg_hmld = st.number_input("HMLD/min (m) ", value=28.0)
        ssg_acc = st.number_input("ACC/min (count) ", value=1.1)
        ssg_dec = st.number_input("DEC/min (count) ", value=1.0)
        ssg_hsr = st.number_input("HSR/min (m) ", value=1.8)
        ssg_pl = st.number_input("PlayerLoad/min ", value=13.0)

    def pct(num, den):
        try:
            return num / den if den else None
        except Exception:
            return None

    td_pct, hmld_pct, acc_pct, dec_pct, hsr_pct, pl_pct = [pct(ssg_td, mdp_td), pct(ssg_hmld, mdp_hmld), pct(ssg_acc, mdp_acc), pct(ssg_dec, mdp_dec), pct(ssg_hsr, mdp_hsr), pct(ssg_pl, mdp_pl)]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for (label, val, col) in zip(["TD", "HMLD", "ACC", "DEC", "HSR", "PL"], [td_pct, hmld_pct, acc_pct, dec_pct, hsr_pct, pl_pct], [c1, c2, c3, c4, c5, c6]):
        with col:
            color = class_for_pct(val)
            st.markdown(f"<div class='{color}' style='border-radius:10px;padding:6px;text-align:center'><b>{label}</b><br>{fmt_pct(val)}</div>", unsafe_allow_html=True)

    st.caption("Legend: Under <80% · On-Target 80–100% · Over >100%")

pip install streamlit
streamlit run app.py
