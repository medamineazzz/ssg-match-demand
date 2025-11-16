    # ---- Pitch Visualization ----
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("🏟️ Pitch Visualization (real field markings)")

    # Figure proportions (avoid division by zero)
    fig_ratio = (width / length) if length else 1
    fig_w = 8
    fig_h = max(4, fig_w * fig_ratio)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # ====== Pitch constants (in meters) ======
    pen_depth = 16.5
    pen_width = 40.32
    goal_depth = 5.5
    goal_width = 18.32
    spot_dist = 11
    center_circle_r = 9.15
    corner_r = 1.0

    # ====== Basic frame ======
    # Outer pitch
    ax.add_patch(Rectangle((0, 0), length, width, fill=False, lw=2, color="#111827"))

    # Halfway line
    ax.plot([length / 2, length / 2], [0, width], color="#9ca3af", linestyle="--", lw=1)

    # ====== Center circle & spot ======
    center_x, center_y = length / 2, width / 2
    # Clip radius so it fits on very small fields
    cc_r = min(center_circle_r, length / 3, width / 3)
    ax.add_patch(Circle((center_x, center_y), cc_r, fill=False, lw=1, color="#9ca3af"))
    ax.scatter(center_x, center_y, s=15, color="#9ca3af")

    # ====== Penalty & goal areas (left + right) ======
    effective_pen_width = min(pen_width, width * 0.9)
    effective_goal_width = min(goal_width, width * 0.6)
    pen_y0 = (width - effective_pen_width) / 2
    goal_y0 = (width - effective_goal_width) / 2

    # Left penalty box
    ax.add_patch(
        Rectangle((0, pen_y0), pen_depth, effective_pen_width, fill=False, lw=1.5, color="#111827")
    )
    # Right penalty box
    ax.add_patch(
        Rectangle((length - pen_depth, pen_y0), pen_depth, effective_pen_width, fill=False, lw=1.5, color="#111827")
    )

    # Left 6-yard box
    ax.add_patch(
        Rectangle((0, goal_y0), goal_depth, effective_goal_width, fill=False, lw=1.3, color="#111827")
    )
    # Right 6-yard box
    ax.add_patch(
        Rectangle((length - goal_depth, goal_y0), goal_depth, effective_goal_width, fill=False, lw=1.3, color="#111827")
    )

    # Penalty spots
    ax.scatter(spot_dist, center_y, s=20, color="#111827")
    ax.scatter(length - spot_dist, center_y, s=20, color="#111827")

    # Penalty arcs (clipped radius if small pitch)
    arc_r = min(center_circle_r, length / 3, width / 3)
    ax.add_patch(
        Arc(
            (spot_dist, center_y),
            2 * arc_r,
            2 * arc_r,
            angle=0,
            theta1=310,
            theta2=50,
            lw=1,
            color="#9ca3af",
        )
    )
    ax.add_patch(
        Arc(
            (length - spot_dist, center_y),
            2 * arc_r,
            2 * arc_r,
            angle=180,
            theta1=310,
            theta2=50,
            lw=1,
            color="#9ca3af",
        )
    )

    # Goals (simple small rectangles outside pitch)
    goal_post_y0 = center_y - effective_goal_width / 2
    ax.add_patch(
        Rectangle((-1.5, goal_post_y0), 1.5, effective_goal_width, fill=False, lw=1, color="#111827")
    )
    ax.add_patch(
        Rectangle((length, goal_post_y0), 1.5, effective_goal_width, fill=False, lw=1, color="#111827")
    )

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
                lw=0.7,
                color="#9ca3af",
            )
        )

    # Optional 5m grid (background)
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
            ax.text(x, y, str(i), color="white", ha="center", va="center", fontsize=9, weight="bold")

        ax.legend(loc="upper right", fontsize=8, frameon=False)

    # ====== Final layout ======
    ax.set_xlim(0, length)
    ax.set_ylim(0, width)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        f"{int(length)}m × {int(width)}m | {n_players} players | APP: {app:.0f} m²/player",
        fontsize=12,
        pad=12,
    )

    st.pyplot(fig)
    st.caption("Real football pitch markings scaled to your SSG dimensions. Players are auto-placed and numbered.")
