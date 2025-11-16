# app.py
# -------------------------------------------------------------
# SSG vs Match Demand — Streamlined Coach Tool (NO pitch viz)
# Catapult-style dark theme + Planner + Expected Demand + Quick %MDP
# -------------------------------------------------------------

from typing import Optional, Dict
import streamlit as st
from datetime import date

# --------------------------- Page Setup ---------------------------
st.set_page_config(page_title="SSG vs Match Demand", page_icon="⚽", layout="wide")

# Display Catapult logo
st.image("CAT_horizontal_logo_lockup_white.png", width=180)

# --------------------------- Global CSS ---------------------------
st.markdown(
    """
    <style>
      body { background-color: #0b1120; }
      .ssg-card { border:1px solid #1f2937; border-radius:16px; padding:18px; background:#020617; }
      .ssg-kpi { border:1px solid #111827; border-radius:14px; padding:12px; text-align:center; background:#020617; }
      .ssg-kpi .label { font-size:12px; color:#9ca3af; }
      .ssg-kpi .value { font-size:20px; font-weight:700; color:#f9fafb; }
      .ssg-pill { display:flex; align-items:center; justify-content:space-between; gap:10px; border:1px solid #111827; border-radius:12px; padding:8px 10px; background:#020617; }
      .ssg-pill .l { font-size:12px; color:#9ca3af; }
      .ssg-pill .r { font-size:13px; font-weight:700; border-radius:8px; padding:2px 8px; }
      .ssg-chip { display:flex; flex-direction:column; align-items:center; justify-content:center; border-radius:12px; padding:10px 12px; min-height:68px; background:#020617; }
      .ssg-chip .t { font-size:11px; opacity:.7; color:#9ca3af; }
      .ssg-chip .v { font-weight:800; font-size:16px; color:#f9fafb; }
      .stTabs [role="tab"] { background:#020617; color:#9ca3af; border-radius:999px; padding:6px 16px; }
      .stTabs [role="tab"][aria-selected="true"] { background:#111827; color:#f9fafb; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- Color Logic ---------------------------
DEFAULT_COLORS = {
    "under": "#F97373",
    "under_text": "#FEE2E2",
    "on": "#22C55E",
    "on_text": "#DCFCE7",
    "over": "#F97316",
    "over_text": "#FFEDD5",
}

def style_for_pct(v: Optional[float], colors: dict) -> str:
    if v is None:
        return "background:#111827;color:#6b7280;"
    if v < 0.8:
        return f"background:{colors['under']};color:#111827;"
    if v <= 1.0:
        return f"background:{colors['on']};color:#022c22;"
    return f"background:{colors['over']};color:#7c2d12;"

# --------------------------- Expected Demand Logic ---------------------------
def expected_demand(app: Optional[float]) -> Dict[str, str]:
    if not app:
        return {k: "" for k in ["TD", "HSR", "SPRINT", "ACC", "DEC", "PL"]}

    if app < 85:
        return {"TD":"MED","HSR":"LOW","SPRINT":"LOW","ACC":"HIGH","DEC":"HIGH","PL":"HIGH"}
    elif app <= 120:
        return {"TD":"MED","HSR":"MED","SPRINT":"MED","ACC":"MED","DEC":"MED","PL":"MED"}
    else:
        return {"TD":"HIGH","HSR":"HIGH","SPRINT":"HIGH","ACC":"LOW","DEC":"LOW","PL":"LOW"}

def fmt_pct(v):
    if v is None: return "-"
    return f"{v*100:.0f}%"

# --------------------------- Sidebar ---------------------------
with st.sidebar:
    st.header("⚙️ Appearance")
    col1, col2 = st.columns(2)
    with col1:
        under = st.color_picker("Under <80%", DEFAULT_COLORS["under"])
        on = st.color_picker("On 80–100%", DEFAULT_COLORS["on"])
    with col2:
        over = st.color_picker("Over >100%", DEFAULT_COLORS["over"])
        accent = st.color_picker("Accent", "#F97316")  # Catapult orange

    colors = {
        "under": under,
        "on": on,
        "over": over,
        "under_text": DEFAULT_COLORS["under_text"],
        "on_text": DEFAULT_COLORS["on_text"],
        "over_text": DEFAULT_COLORS["over_text"],
        "accent": accent,
    }

# --------------------------- Header ---------------------------
st.markdown(
    """
<div style="
    background:#020617;
    border-radius:14px;
    padding:14px 20px;
    margin-top:10px;
    margin-bottom:10px;
    border:1px solid #111827;">
  <div style="font-size:26px;font-weight:800;color:#F9FAFB;">
    SSG vs Match Demand
  </div>
  <div style="color:#9CA3AF;margin-top:4px;font-size:13px;">
    Catapult-style SSG planner to link training design with match demands.
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

    # Inputs
    colA, colB, colC = st.columns(3)
    with colA:
        _date = st.date_input("Date", value=date.today())
        format_ = st.selectbox("Format", ["4v4","6v6","7v7","8v8","10v10"])
        players = st.number_input("Players", 2, 22, 8)
    with colB:
        length = st.number_input("Length (m)", 10, 120, 30)
        width = st.number_input("Width (m)", 10, 90, 40)
        sets = st.number_input("Sets", 1, 12, 3)
    with colC:
        work = st.number_input("Work per set (min)", 1, 30, 3)
        rest = st.number_input("Rest (sec)", 15, 300, 90)

    # Calculations
    area = length * width
    app = area / players
    total_work = sets * work
    total_rest = (sets * rest) / 60
    total_time = total_work + total_rest

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    labels = ["Area (m²)", "APP (m²)", "Work (min)", "Rest (min)", "Total (min)"]
    values = [f"{area:.0f}", f"{app:.0f}", f"{total_work:.0f}", f"{total_rest:.0f}", f"{total_time:.0f}"]

    for col, label, val in zip([k1,k2,k3,k4,k5], labels, values):
        col.markdown(
            f"""
            <div class='ssg-kpi'>
              <div class='label'>{label}</div>
              <div class='value'>{val}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Expected Demand
    st.markdown("### Expected Demand")
    exp = expected_demand(app)

    t1,t2,t3,t4,t5,t6 = st.columns(6)
    tags = [
        ("TD",exp["TD"]),
        ("HSR",exp["HSR"]),
        ("Sprint",exp["SPRINT"]),
        ("ACC",exp["ACC"]),
        ("DEC",exp["DEC"]),
        ("PL",exp["PL"])
    ]

    for (label,val),col in zip(tags,[t1,t2,t3,t4,t5,t6]):
        col.markdown(
            f"""
            <div class='ssg-pill'>
                <span class='l'>{label}</span>
                <span class='r'>{val}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Summary
    summary = (
        f"{format_} | {length}×{width}m | {players} players | "
        f"{sets}×{work}′ / {rest}s | APP {app:.0f} m² | "
        f"TD {exp['TD']} · HSR {exp['HSR']} · ACC {exp['ACC']}"
    )
    st.text_area("Copy summary", summary, height=70)

    st.markdown("</div>", unsafe_allow_html=True)

# ========================== QUICK %MDP TAB ==========================
with quick_tab:
    st.markdown("<div class='ssg-card ssg-shadow'>", unsafe_allow_html=True)
    st.subheader("Quick % of Match")

    left, right = st.columns(2)
    with left:
        st.markdown("**Match MDP (per min)**")
        mdp_td = st.number_input("TD/min", 0.0, 400.0, 180.0)
        mdp_hmld = st.number_input("HMLD/min", 0.0, 100.0, 30.0)
        mdp_acc = st.number_input("ACC/min", 0.0, 5.0, 0.9)
        mdp_dec = st.number_input("DEC/min", 0.0, 5.0, 0.8)
        mdp_hsr = st.number_input("HSR/min", 0.0, 20.0, 3.5)
        mdp_pl = st.number_input("PL/min", 0.0, 30.0, 12.0)

    with right:
        st.markdown("**SSG Block (per min)**")
        ssg_td = st.number_input("TD/min ", value=165.0)
        ssg_hmld = st.number_input("HMLD/min ", value=28.0)
        ssg_acc = st.number_input("ACC/min ", value=1.1)
        ssg_dec = st.number_input("DEC/min ", value=1.0)
        ssg_hsr = st.number_input("HSR/min ", value=1.8)
        ssg_pl = st.number_input("PL/min ", value=13.0)

    def pct(num, den):
        try:
            return num / den if den else None
        except:
            return None

    metrics = [
        ("TD", pct(ssg_td, mdp_td)),
        ("HMLD", pct(ssg_hmld, mdp_hmld)),
        ("ACC", pct(ssg_acc, mdp_acc)),
        ("DEC", pct(ssg_dec, mdp_dec)),
        ("HSR", pct(ssg_hsr, mdp_hsr)),
        ("PL", pct(ssg_pl, mdp_pl)),
    ]

    cols = st.columns(6)
    for (label, val), col in zip(metrics, cols):
        style = style_for_pct(val, colors)
        col.markdown(
            f"""
            <div class='ssg-chip ssg-shadow' style="{style}">
              <div class='t'>{label}</div>
              <div class='v'>{fmt_pct(val)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col.progress(min(1.0, max(0.0, val if val else 0.0)))

    st.caption("Legend: <80% Under · 80–100% On Target · >100% Overload")
    st.markdown("</div>", unsafe_allow_html=True)
