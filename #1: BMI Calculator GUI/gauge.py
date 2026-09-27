import math
import tkinter as tk


def draw_gauge(canvas, theme, bmi_val=0):
    canvas.delete("all")
    colors = theme["gauge_colors"]

    canvas.config(bg=theme["card"])
    sections = [
        {"color": colors[0], "span": 8.5},
        {"color": colors[1], "span": 6.5},
        {"color": colors[2], "span": 5.0},
        {"color": colors[3], "span": 15.0},
    ]

    current_start = 180
    for sec in sections:
        extent_angle = (sec["span"] / 35.0) * 180.0
        start_deg = current_start - extent_angle
        canvas.create_arc(
            10,
            10,
            180,
            180,
            start=start_deg,
            extent=extent_angle,
            fill=sec["color"],
            outline=theme["card"],
            width=2,
        )
        current_start -= extent_angle

    canvas.create_oval(
        48, 48, 142, 142, fill=theme["card"], outline=theme["card"]
    )

    if bmi_val > 0:
        capped_bmi = max(10, min(45, bmi_val))
        angle = 180 - ((capped_bmi - 10) / 35) * 180
        rad = math.radians(angle)
        cx, cy, length = 95, 95, 38
        nx = cx + length * math.cos(rad)
        ny = cy - length * math.sin(rad)
        canvas.create_line(
            cx, cy, nx, ny, fill=theme["fg"], width=2.5, arrow=tk.LAST
        )
        canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=theme["fg"])