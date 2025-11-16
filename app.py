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
ax.plot([length/2, length/2], [0, width], color="#9ca3af", linestyle="--", lw=1)

# ====== Center circle ======
cc_r = min(center_circle_r, length/3, width/3)
ax.add_patch(Circle((length/2, width/2), cc_r, fill=False, lw=1, color="#9ca3af"))
ax.scatter(length/2, width/2, s=15, color="#9ca3af")

# ====== Penalty + 6-yard areas ======
effective_pen_width = min(pen_width, width*0.9)
effective_goal_width = min(goal_width, width*0.6)
pen_y0 = (width - effective_pen_width) / 2
goal_y0 = (width - effective_goal_width) / 2

# Penalty areas (left + right)
ax.add_patch(Rectangle((0, pen_y0), pen_depth, effective_pen_width, fill=False, lw=1.5, color="#111827"))
ax.add_patch(Rectangle((length - pen_depth, pen_y0), pen_depth, effective_pen_width, fill=False, lw=1.5, color="#111827"))

# 6-yard areas
ax.add_patch(Rectangle((0, goal_y0), goal_depth, effective_goal_width, fill=False, lw=1.3, color="#111827"))
ax.add_patch(Rectangle((length - goal_depth, goal_y0), goal_depth, effective_goal_width, fill=False, lw=1.3, color="#111827"))

# Penalty spots
ax.scatter(spot_dist, width/2_
