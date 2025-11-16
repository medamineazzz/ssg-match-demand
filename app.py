# app.py
# -------------------------------------------------------------
# SSG vs Match Demand — Simple Coach Tool (Streamlit)
# Design-focused edition + Catapult Logo + Pitch Visualization
# Tabs:
# 1) Planner → APP + Expected Demand (pills) + Pitch viz
# 2) Quick %MDP → % of match with colored chips + progress bars
# -------------------------------------------------------------

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
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
            st.markdown(
                f"<div class='ssg-kpi'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    # ---- Expected Demand ----
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
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
        tone = (
            "background:#E5E7EB;color:#111827;" if val == "MED"
            else (f"background:{DEFAULT_COLORS['over']};color:{DEFAULT_COLORS['over_text']};"
                  if val == "HIGH"
                  else f"background:#DBEAFE;color:#1E40AF;")
        )
        with col:
            st.markdown(
                f"<div class='ssg-pill'><span class='l'>{label}</span>"
                f"<span class='r' style='{tone}'>{val or ''}</span></div>",
                unsafe_allow_html=True,
            )

    st.caption("APP guide: Small <85 → high ACC/DEC & PL · Medium 85–120 → balanced · Large >120 → more HSR & sprints")

    # ---- Session Summary ----
    summary = (
        f"{format_} | {length}×{width}m | {players} players | "
        f"{sets}×{work}′ work / {rest}s rest | APP {app:.0f} m² | "
        f"Expected: TD {exp['TD']} · HSR {exp['HSR']} · ACC {exp['ACC']}"
    )
    st.text_area("Copy summary", summary, height=80)

    # ---- Pitch Visualization ----
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("🏟️ Pitch Visualization (real field markings)")

    # Figure proportions
    fig_ratio = (width / length) if length else 1
    fig_w = 8
    fig_h = max(4, fig_w * fig_ratio)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # ====== Pitch constants ======
    pen_depth = 16.5
    pen_width = 40.32
    goal_depth = 5.5
    goal_width = 18.32
    spot_dist = 11
    center_circle_r = 9.15
    corner_r = 1.0

    # ====== Outer frame ======
    ax.add_patch(Rectangle((0, 0), length, width, fill=False, lw=2, color="#111827"))
    ax.plot([length / 2, length / 2], [0, width], color="#9ca3af", linestyle="--", lw=1)

    # ====== Center circle ======
    cc_r = min(center_circle_r, length / 3, width / 3)
    ax.add_patch(Circle((length / 2, width / 2), cc_r, fill=False, lw=1, color="#9ca3af"))
    ax.scatter(length / 2, width / 2, s=15, color="#9ca3af")

    # ====== Penalty + 6-yard areas ======
    effective_pen_width = min(pen_width, width * 0.9)
    effective_goal_width = min(goal_width, width * 0.6)
    pen_y0 = (width - effective_pen_width) / 2
    goal_y0 = (width - effective_goal_width) / 2

    # Penalty areas
    ax.add_patch(Rectangle((0, pen_y0), pen_depth, effective_pen_width, fill=False, lw=1.5, color="#111827"))
    ax.add_patch(Rectangle((length - pen_depth, pen_y0), pen_depth, effective_pen_width, fill=False, lw=1.5, color="#111827"))

    # 6-yard areas
    ax.add_patch(Rectangle((0, goal_y0), goal_depth, effective_goal_width, fill=False, lw=1.3, color="#111827"))
    ax.add_patch(Rectangle((length - goal_depth, goal_y0), goal_depth, effective_goal_width, fill=False, lw=1.3, color="#111827"))

    # Penalty spots
    ax.scatter(spot_dist, width / 2, s=20, color="#111827")
    ax.scatter(length - spot_dist, width / 2, s=20, color="#111827")

    # Penalty arcs
    arc_r = min(center_circle_r, length / 3, width / 3)
    ax.add_patch(
        Arc((spot_dist, width / 2), 2 * arc_r, 2 * arc_r, angle=0, theta1=310, theta2=50, lw=1, color="#9ca3af")
    )
    ax.add_patch(
        Arc((length - spot_dist, width / 2), 2 * arc_r, 2 * arc_r, angle=180, theta1=310, theta2=50, lw=1, color="#9ca3af")
    )

    # Goals
    goal_post_y0 = width / 2 - effective_goal_width / 2
    ax.add_patch(Rectangle((-1.5, goal_post_y0), 1.5, effective_goal_width, fill=False, lw=1, color="#111827"))
    ax.add_patch(Rectangle((length, goal_post_y0), 1.5, effective_goal_width, fill=False, lw=1, color="#111827"))

    # Corner arcs
    for (cx, cy) in [(0, 0), (0, width), (length, 0), (length, width)]:
        ax.add_patch(
            Arc((cx, cy), 2 * corner_r, 2 * corner_r, angle=0, theta1=0, theta2=90, lw=0.7, color="#9ca3af")
        )

    # 5m grid (background)
    for x in range(5, int(length), 5):
        ax.plot([x, x], [0, width], color="#e5e7eb", lw=0.5)
    for y in range(5, int(width), 5):
        ax.plot([0, length], [y, y], color="#e5e7eb", lw=0.5)

    # ====== Players (auto layout, numbered) ======
    n_players = int(players)
    if n_players >= 2:
        per_row = min(6, max(2, int(np.ceil(n_players / 2))))
        rows = int(np.ceil(n_players / per_row))
        xs = np.linspace(length * 0.1, length * 0.9, per_row)
        ys = np.linspace(width * 0.2, width * 0.8, rows)
        pts = np.array([(x, y) for y in ys for x in xs])[:n_players]

        half = n_players // 2
        ax.scatter(pts[:half, 0], pts[:half, 1], s=200, color="#111827", label="Team A", zorder=3)
        ax.scatter(pts[half:, 0], pts[half:, 1], s=200, color="#FF8A00", label="Team B", zorder=3)

        for i, (x, y) in enumerate(pts, start=1):
            ax.text(x, y, str(i), color="white", fontsize=9, weight="bold", ha="center", va="center")

        ax.legend(loc="upper right", fontsize=8, frameon=False)

    # ====== Final layout ======
    ax.set_xlim(0, length)
    ax.set_ylim(0, width)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"{length}m × {width}m | {players} players | APP: {app:.0f}", fontsize=12)

    st.pyplot(fig)
    st.caption("Real football pitch markings scaled to your SSG shape. Players are auto-placed.")

    st.markdown("</div>", unsafe_allow_html=True)  # close card

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
            st.markdown(
                f"<div class='ssg-chip ssg-shadow' style='{style}'>"
                f"<div class='t'>{label} %MDP</div><div class='v'>{fmt_pct(val)}</div></div>",
                unsafe_allow_html=True,
            )
            prog = 0 if val is None else max(0, min(1.2, val))
            st.progress(min(1.0, prog))

    st.caption("Legend: Under <80% · On-Target 80–100% · Over >100%")
    st.markdown("</div>", unsafe_allow_html=True)
