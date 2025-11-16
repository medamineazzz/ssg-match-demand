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

# Display Catapult logo (make sure PNG exists in repo root)
st.image("CAT_horizontal_logo_lockup_white.png", width=180)

# --------------------------- Global CSS ---------------------------
st.markdown(
    """
    <style>
      body { background-color: #0b1120; }  /* dark navy background */
      .ssg-card { border:1px solid #1f2937; border-radius:16px; padding:18px; background:#020617; }
      .ssg-kpi { border:1px solid #111827; border-radius:14px; padding:12px; text-align:center; background:#020617; }
      .ssg-kpi .label { font-size:12px; color:#9ca3af; }
      .ssg-kpi .value { font-size:20px; font-weight:700; color:#f9fafb; }
      .ssg-pill { display:flex; align-items:center; justify-content:space-between; gap:10px; border:1px solid #111827; border-radius:12px; padding:8px 10px; background:#020617; }
      .ssg-pill .l { font-size:12px; color:#9ca3af; }
      .ssg-pill .r { font-size:13px; font-weight:700; border-radius:8px; padding:2px 8px; }
      .ssg-chip { display:flex; flex-direction:column; align-items:center; justify-content:center; border-radius:12px; padding:10px 12px; text-align:center; min-height:68px; background:#020617; }
      .ssg-chip .t { font-size:11px; opacity:.7; color:#9ca3af; }
      .ssg-chip .v { font-weight:800; font-size:16px; color:#f9fafb; }
      .ssg-shadow { box-shadow:0 1px 2px rgba(0,0,0,0.4), 0 6px 18px rgba(0,0,0,0.7); }
      .stTabs [role="tab"] { background:#020617; color:#9ca3af; border-radius:999px; padding:6px 16px; }
      .stTabs [role="tab"][aria-selected="true"] { background:#111827; color:#f9fafb; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- Palette Helpers ---------------------------
DEFAULT_COLORS = {
    "under": "#F97373",      # light red
    "under_text": "#FEE2E2",
    "on": "#22C55E",         # green
    "on_text": "#DCFCE7",
    "over": "#F97316",       # orange
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

# --------------------------- Logic ---------------------------
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
        accent = st.color_picker("Accent", "#F97316")  # Catapult orange

    colors = {
        "under": under,
        "under_text": DEFAULT_COLORS["under_text"],
        "on": on,
        "on_text": DEFAULT_COLORS["on_text"],
        "over": over,
        "over_text": DEFAULT_COLORS["over_text"],
        "accent": accent,
    }

# --------------------------- Catapult-style Header ---------------------------
st.markdown(
    """
<div style="
    background:#020617;
    border-radius:14px;
    padding:14px 20px;
    margin-top:10px;
    margin-bottom:10px;
    border:1px solid #111827;">
  <div style="font-size:26px;font-weight:800;color:#F9FAFB;display:flex;align-items:center;gap:8px;">
    <span>SSG vs Match Demand</span>
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
    st.subheader("Planner", anchor="planner")

    # ---- Inputs ----
    colA, colB, colC = st.columns(3)
    with colA:
        _date = st.date_input("Date", value=date.today())
        format_ = st.selectbox("Format", ["4v4", "6v6", "7v7", "8v8", "10v10"])
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
    app = area / players if players else 0.0
    total_work = sets * work
    total_rest = (sets * rest) / 60
    total_session = total_work + total_rest

    # ---- KPI Cards ----
    k1, k2, k3, k4, k5 = st.columns(5)
    labels = [
        "Pitch Area (m²)",
        "Area/Player (m²)",
        "Total Work (min)",
        "Total Rest (min)",
        "Session (min)",
    ]
    values = [
        f"{area:.0f}",
        f"{app:.1f}",
        f"{total_work:.0f}",
        f"{total_rest:.0f}",
        f"{total_session:.0f}",
    ]
    for col, label, value in zip([k1, k2, k3, k4, k5], labels, values):
        with col:
            st.markdown(
                f"""
                <div class='ssg-kpi'>
                  <div class='label'>{label}</div>
                  <div class='value'>{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---- Expected Demand ----
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("**Expected Demand (from APP)**")
    exp = expected_demand(app)

    t1, t2, t3, t4, t5, t6 = st.columns(6)
    tags = [
        ("TD", exp["TD"]),
        ("HSR", exp["HSR"]),
        ("Sprints", exp["SPRINT"]),
        ("ACC", exp["ACC"]),
        ("DEC", exp["DEC"]),
        ("PL/min", exp["PL"]),
    ]
    for (label, val), col in zip(tags, [t1, t2, t3, t4, t5, t6]):
        if val == "HIGH":
            tone = f"background:{colors['over']};color:#111827;"
        elif val == "MED":
            tone = "background:#111827;color:#E5E7EB;"
        elif val == "LOW":
            tone = "background:#1D4ED8;color:#DBEAFE;"
        else:
            tone = "background:#111827;color:#6B7280;"

        with col:
            st.markdown(
                f"""
                <div class='ssg-pill'>
                  <span class='l'>{label}</span>
                  <span class='r' style="{tone}">{val}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.caption("APP guide: Small <85 → higher ACC/DEC & PL · Medium 85–120 → balanced · Large >120 → more HSR & sprints")

    # ---- Session Summary ----
    summary = (
        f"{format_} | {length}×{width}m | {players} players | "
        f"{sets}×{work}′ work / {rest}s rest | APP {app:.0f} m² | "
        f"Expected → TD: {exp['TD']} · HSR: {exp['HSR']} · ACC: {exp['ACC']}"
    )
    st.text_area("Copy summary", summary, height=70)

    # ---- Pitch Visualization (small green pitch) ----
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("🏟️ Pitch Visualization")

    fig_ratio = (width / length) if length else 1.0
    fig_w = 2.5
    fig_h = max(1.4, fig_w * fig_ratio)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # Pitch constants (approximate full-size ref, scaled to user dims)
    pen_depth = 16.5
    pen_width = 40.32
    goal_depth = 5.5
    goal_width = 18.32
    spot_dist = 11
    center_circle_r = 9.15
    corner_r = 1.0

    # Green background
    ax.add_patch(
        Rectangle(
            (0, 0),
            length,
            width,
            facecolor="#059669",
            edgecolor="#ffffff",
            lw=2,
        )
    )

    # Halfway line
    ax.plot(
        [length / 2, length / 2],
        [0, width],
        color="#ffffff",
        lw=1.5,
    )

    # Center circle + spot
    cc_r = min(center_circle_r, length / 3, width / 3)
    ax.add_patch(
        Circle(
            (length / 2, width / 2),
            cc_r,
            fill=False,
            lw=1.2,
            color="#ffffff",
        )
    )
    ax.scatter(length / 2, width / 2, s=12, color="#ffffff")

    # Penalty + 6-yard areas (scaled within pitch)
    effective_pen_width = min(pen_width, width * 0.9)
    effective_goal_width = min(goal_width, width * 0.6)
    pen_y0 = (width - effective_pen_width) / 2
    goal_y0 = (width - effective_goal_width) / 2

    ax.add_patch(
        Rectangle(
            (0, pen_y0),
            pen_depth,
            effective_pen_width,
            fill=False,
            lw=1.2,
            edgecolor="#ffffff",
        )
    )
    ax.add_patch(
        Rectangle(
            (length - pen_depth, pen_y0),
            pen_depth,
            effective_pen_width,
            fill=False,
            lw=1.2,
            edgecolor="#ffffff",
        )
    )

    ax.add_patch(
        Rectangle(
            (0, goal_y0),
            goal_depth,
            effective_goal_width,
            fill=False,
            lw=1.0,
            edgecolor="#ffffff",
        )
    )
    ax.add_patch(
        Rectangle(
            (length - goal_depth, goal_y0),
            goal_depth,
            effective_goal_width,
            fill=False,
            lw=1.0,
            edgecolor="#ffffff",
        )
    )

    # Penalty spots
    ax.scatter(spot_dist, width / 2, s=20, color="#ffffff")
    ax.scatter(length - spot_dist, width / 2, s=20, color="#ffffff")

    # Corner arcs
    for (cx, cy) in [(0, 0), (0, width), (length, 0), (length, width)]:
        ax.add_patch(
            Arc(
                (cx, cy),
                2 * corner_r,
                2 * corner_r,
                angle=0,
                theta1=0,
                theta2=90,
                lw=0.8,
                color="#ffffff",
            )
        )

    # Players auto-layout
    n_players = int(players)
    if n_players >= 1:
        per_row = min(6, max(2, int(np.ceil(n_players / 2))))
        rows = int(np.ceil(n_players / per_row))
        xs = np.linspace(length * 0.1, length * 0.9, per_row)
        ys = np.linspace(width * 0.2, width * 0.8, rows)
        pts = np.array([(x, y) for y in ys for x in xs])[:n_players]

        half = n_players // 2
        ax.scatter(pts[:half, 0], pts[:half, 1], s=140, color="#0F172A")
        ax.scatter(pts[half:, 0], pts[half:, 1], s=140, color="#F97316")

        for i, (x, y) in enumerate(pts, start=1):
            ax.text(
                x,
                y,
                str(i),
                color="white",
                fontsize=8,
                ha="center",
                va="center",
                weight="bold",
            )

    # Final layout
    ax.set_xlim(0, length)
    ax.set_ylim(0, width)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        f"{length}m × {width}m · {players} players · APP {app:.0f}",
        fontsize=11,
        color="#E5E7EB",
    )

    st.pyplot(fig)
    st.caption("Smaller green match-style pitch. Players auto-distributed & numbered.")

    st.markdown("</div>", unsafe_allow_html=True)

# ========================== QUICK %MDP TAB ==========================
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
        ("TD", pct(ssg_td, mdp_td)),
        ("HMLD", pct(ssg_hmld, mdp_hmld)),
        ("ACC", pct(ssg_acc, mdp_acc)),
        ("DEC", pct(ssg_dec, mdp_dec)),
        ("HSR", pct(ssg_hsr, mdp_hsr)),
        ("PL", pct(ssg_pl, mdp_pl)),
    ]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for (label, val), col in zip(metrics, [c1, c2, c3, c4, c5, c6]):
        style = style_for_pct(val, colors)
        with col:
            col.markdown(
                f"""
                <div class='ssg-chip ssg-shadow' style="{style}">
                  <div class='t'>{label} %MDP</div>
                  <div class='v'>{fmt_pct(val)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            prog = 0.0
            if val is not None:
                prog = max(0.0, min(1.2, val))
            col.progress(min(1.0, prog))

    st.caption("Legend: Under <80% · On-target 80–100% · Overload >100%")
    st.markdown("</div>", unsafe_allow_html=True)
