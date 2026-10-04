"""
A small, dependency-free bar chart drawn directly on a Tkinter Canvas.
No matplotlib needed — this keeps the app lightweight and easy to run
on any machine that already has Tkinter.
"""


def draw_round_chart(canvas, results, theme):
    """
    Draws one bar per completed round: height = accuracy (0-100%),
    color = green if the round had zero errors, orange otherwise.
    Reads the canvas's actual current size, so it stays correct
    when the window (and therefore the canvas) is resized.
    """
    canvas.delete("all")
    canvas.config(bg=theme["CARD_ALT"])

    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width <= 1 or height <= 1:
        return  # not yet laid out on screen

    if not results:
        canvas.create_text(
            width / 2, height / 2, text="Play a round to see the chart",
            fill=theme["TEXT_MUTED"], font=("Arial", 9),
        )
        return

    margin_x, margin_top, margin_bottom = 14, 10, 20
    plot_w = width - margin_x * 2
    plot_h = height - margin_top - margin_bottom
    n = len(results)
    gap = 6
    bar_w = max(4, (plot_w - gap * (n - 1)) / n)
    baseline_y = margin_top + plot_h

    canvas.create_line(
        margin_x, baseline_y, margin_x + plot_w, baseline_y, fill=theme["BORDER"]
    )

    for i, rec in enumerate(results):
        accuracy = max(0, min(100, rec["accuracy"]))
        bar_h = (accuracy / 100) * plot_h
        x0 = margin_x + i * (bar_w + gap)
        x1 = x0 + bar_w
        y0 = baseline_y - bar_h
        color = theme["COLOR_CORRECT"] if rec["total_errors"] == 0 else theme["COLOR_MISSED"]
        canvas.create_rectangle(x0, y0, x1, baseline_y, fill=color, width=0)
        canvas.create_text(
            (x0 + x1) / 2, baseline_y + 10, text=str(rec["round"]),
            fill=theme["TEXT_MUTED"], font=("Arial", 8),
        )