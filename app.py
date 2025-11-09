# app.py
# -------------------------------------------------------------
# SSG vs Match Demand — Simple Coach Tool (Streamlit)
# Design-focused edition + Catapult Logo integration
# Tabs:
# 1) Planner → APP + Expected Demand (pills)
# 2) Quick %MDP → % of match with colored chips + progress bars
# -------------------------------------------------------------

from typing import Optional, Dict
import streamlit as st
from datetime import date

# --------------------------- Page Setup ---------------------------
st.set_page_config(page_title="SSG vs Match Demand", page_icon="⚽", layout="wide")

# Display Catapult logo at the top (make sure 'catapult_logo.png' is in your repo)
st.image("catapult_logo.png", width=180)

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
st.markdown(f"""
<div class='ssg-card ssg-shadow' style='margin-top:10px;'>
  <div style='font-size:28px;font-weight:800;color:{colors['accent']}'>SSG vs Match Demand</div>
  <div style='color:#6b7280;margin-top:4px'>Plan SSGs, estimate expected demand, and compare against match peaks.</div>
</div>
""", unsafe_allow_html=True)

# --------------------------- Tabs ---------------------------
planner_tab, quick_tab = st.tabs(["🗺️ Planner", "⚡ Quick %MDP"])

# ---------- PLANNER ----------
with planner_tab:
    st.markdown("<div class='ssg-card ssg-shadow'>", unsafe_allow_html=True)
    st.subheader("Planner")

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

    area = length * width
    app = (area / players) if players else 0
    total_work = sets * work
    total_rest = (sets * rest) / 60
    total_session = total_work + total_rest

    k1, k2, k3, k4, k5 = st.columns(5)
    for (label, value) in zip(
        ["Pitch Area (m²)", "Area/Player (m²)", "Total Work (min)", "Total Rest (min)", "Session (min)"],
        [f"{area:.0f}", f"{app:.1f}", f"{total_work:.0f}", f"{total_rest:.0f}", f"{total_session:.0f}"]):
        with eval(f"k{[1,2,3,4,5][["Pitch Area (m²)", "Area/Player (m²)", "Total Work (min)", "Total Rest (min)", "Session (min)"].index(label)]}"):
            st.markdown(f"<div class='ssg-kpi'><div class='label'>{label}</div><div class='value'>{value}</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("**Expected Demand (from APP)**")
    exp = expected_demand(app)

    t1, t2, t3, t4, t5, t6 = st.columns(6)
    tags = [("TD", exp["TD"]), ("HSR", exp["HSR"]), ("Sprints", exp["SPRINT"]), ("ACC", exp["ACC"]), ("DEC", exp["DEC"]), ("PL/min", exp["PL"])]
    for (label, val), col in zip(tags, [t1, t2, t3, t4, t5, t6]):
        tone = "background:#E5E7EB;color:#111827;" if val == "MED" else (f"background:{DEFAULT_COLORS['over']};color:{DEFAULT_COLORS['over_text']};" if val == "HIGH" else f"background:#DBEAFE;color:#1E40AF;")
        with col:
            st.markdown(f"<div class='ssg-pill'><span class='l'>{label}</span><span class='r' style='{tone}'>{val or ''}</span></div>", unsafe_allow_html=True)

    st.caption("APP guide: Small <85 → high ACC/DEC & PL · Medium 85–120 → balanced · Large >120 → more HSR & sprints")
    summary = f"{format_} | {length}×{width}m | {players} players | {sets}×{work}′ work / {rest}s rest | APP {app:.0f} m² | Expected: TD {exp['TD']} · HSR {exp['HSR']} · ACC {exp['ACC']}"
    st.text_area("Copy summary", summary, height=80)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- QUICK %MDP ----------
with quick_tab:
    st.markdown("<div class='ssg-card ssg-shadow'>", unsafe_allow_html=True)
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

    metrics = [
        ("TD", pct(ssg_td, mdp_td)), ("HMLD", pct(ssg_hmld, mdp_hmld)), ("ACC", pct(ssg_acc, mdp_acc)),
        ("DEC", pct(ssg_dec, mdp_dec)), ("HSR", pct(ssg_hsr, mdp_hsr)), ("PL", pct(ssg_pl, mdp_pl))
    ]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for (label, val), col in zip(metrics, [c1, c2, c3, c4, c5, c6]):
        style = style_for_pct(val, colors)
        with col:
            st.markdown(f"<div class='ssg-chip ssg-shadow' style='{style}'><div class='t'>{label} %MDP</div><div class='v'>{fmt_pct(val)}</div></div>", unsafe_allow_html=True)
            prog = 0 if val is None else max(0, min(1.2, val))
            st.progress(min(1.0, prog))

    st.caption("Legend: Under <80% · On-Target 80–100% · Over >100%")
    st.markdown("</div>", unsafe_allow_html=True)
