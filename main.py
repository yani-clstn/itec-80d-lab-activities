import datetime
import tkinter as tk
from tkinter import messagebox

from gauge import draw_gauge
from history_window import open_history_window
from storage import load_preferences, save_history_record, save_preferences

# --- Themes ---
THEMES = {
    "light": {
        "bg": "#FDFBF7",
        "card": "#F5EFE6",
        "fg": "#2D2B2A",
        "subtext": "#6E6A66",
        "accent": "#4A6FA5",
        "accent_hover": "#3B5984",
        "entry_bg": "#FFFFFF",
        "entry_fg": "#2D2B2A",
        "entry_border": "#D8D0C5",
        "btn_sec": "#E6DFD5",
        "btn_sec_fg": "#4A4643",
        "toggle_bg": "#E6DFD5",
        "disclaimer": "#7C7772",
        "underweight": "#2B6CB0",
        "normal": "#276749",
        "overweight": "#C05621",
        "obese": "#C53030",
        "gauge_colors": ["#90CDF4", "#9AE6B4", "#FBD38D", "#FEB2B2"],
    },
    "dark": {
        "bg": "#0F172A",
        "card": "#1E293B",
        "fg": "#F8FAFC",
        "subtext": "#94A3B8",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "entry_bg": "#334155",
        "entry_fg": "#F8FAFC",
        "entry_border": "#475569",
        "btn_sec": "#334155",
        "btn_sec_fg": "#F8FAFC",
        "toggle_bg": "#334155",
        "disclaimer": "#94A3B8",
        "underweight": "#60A5FA",
        "normal": "#4ADE80",
        "overweight": "#FBBF24",
        "obese": "#F87171",
        "gauge_colors": ["#60A5FA", "#4ADE80", "#FBBF24", "#F87171"],
    },
}

prefs = load_preferences()
current_theme = prefs.get("theme", "light")
font_delta = prefs.get("font_delta", 0)

root = tk.Tk()
root.title("Body Mass Index Calculator")
root.geometry("420x800")
root.resizable(False, False)

current_system = tk.StringVar(value=prefs.get("system", "Standard"))
age_group_var = tk.StringVar(value="Adult")
input_history_stack = []

# --- Top Bar ---
top_bar = tk.Frame(root, bg=THEMES[current_theme]["bg"])
top_bar.pack(fill="x", padx=20, pady=(12, 0))

font_frame = tk.Frame(top_bar, bg=THEMES[current_theme]["bg"])
font_frame.pack(side="left")

font_label = tk.Label(font_frame, text="Font:", font=("Segoe UI", 8, "bold"))
font_label.pack(side="left", padx=(0, 2))


def update_preferences():
    save_preferences(
        {
            "theme": current_theme,
            "system": current_system.get(),
            "font_delta": font_delta,
        }
    )


def adjust_font(amount):
    global font_delta
    if -2 <= font_delta + amount <= 4:
        font_delta += amount
        apply_theme()
        update_preferences()


btn_font_minus = tk.Button(
    font_frame,
    text="A-",
    font=("Segoe UI", 8, "bold"),
    bd=0,
    padx=4,
    command=lambda: adjust_font(-1),
)
btn_font_minus.pack(side="left", padx=1)
btn_font_plus = tk.Button(
    font_frame,
    text="A+",
    font=("Segoe UI", 8, "bold"),
    bd=0,
    padx=4,
    command=lambda: adjust_font(1),
)
btn_font_plus.pack(side="left", padx=1)

history_btn = tk.Button(
    top_bar,
    text="📜 History",
    font=("Segoe UI", 8, "bold"),
    bd=0,
    padx=8,
    pady=3,
    cursor="hand2",
    command=lambda: open_history_window(root, THEMES[current_theme]),
)
history_btn.pack(side="right", padx=(5, 0))

theme_btn = tk.Button(
    top_bar,
    text="🌙 Dark",
    font=("Segoe UI", 8, "bold"),
    bd=0,
    padx=8,
    pady=3,
    cursor="hand2",
    command=lambda: toggle_theme(),
)
theme_btn.pack(side="right")

# --- Main Card ---
card = tk.Frame(root, bd=0)
card.pack(fill="both", expand=True, padx=20, pady=12)

title_label = tk.Label(
    card, text="Body Mass Index Calculator", font=("Segoe UI", 15, "bold")
)
title_label.pack(pady=(15, 8))

toggle_frame = tk.Frame(card)
toggle_frame.pack(pady=(0, 8))

std_btn = tk.Button(
    toggle_frame,
    text="Standard",
    font=("Segoe UI", 9, "bold"),
    width=10,
    pady=4,
    bd=0,
    cursor="hand2",
    command=lambda: switch_units("Standard"),
)
std_btn.pack(side="left", padx=2)

met_btn = tk.Button(
    toggle_frame,
    text="Metric",
    font=("Segoe UI", 9, "bold"),
    width=10,
    pady=4,
    bd=0,
    cursor="hand2",
    command=lambda: switch_units("Metric"),
)
met_btn.pack(side="left", padx=2)

target_container = tk.Frame(card)
target_container.pack(pady=(0, 8))

target_label = tk.Label(
    target_container, text="Target:", font=("Segoe UI", 9, "bold")
)
target_label.pack(side="left", padx=(0, 6))

target_menu = tk.OptionMenu(
    target_container,
    age_group_var,
    "Adult",
    "Child (2-19 yrs)",
    command=lambda _: reset_result(),
)
target_menu.config(
    font=("Segoe UI", 9), relief="flat", highlightthickness=0, bd=0
)
target_menu.pack(side="left")

height_label = tk.Label(card, text="Height", font=("Segoe UI", 9, "bold"))
height_label.pack(anchor="w", padx=30, pady=(2, 0))

height_sub_label = tk.Label(
    card, text="Feet & Inches", font=("Segoe UI", 8, "italic")
)
height_sub_label.pack(anchor="w", padx=30, pady=(0, 2))

height_wrapper = tk.Frame(card)
height_wrapper.pack(fill="x", padx=30, pady=(2, 6))

standard_height_frame = tk.Frame(height_wrapper)
ft_entry = tk.Entry(
    standard_height_frame,
    font=("Segoe UI", 10),
    relief="flat",
    justify="center",
    width=8,
)
ft_entry.pack(side="left", ipady=4, expand=True, fill="x")
ft_unit_lbl = tk.Label(
    standard_height_frame, text="ft", font=("Segoe UI", 8, "bold")
)
ft_unit_lbl.pack(side="left", padx=4)

in_entry = tk.Entry(
    standard_height_frame,
    font=("Segoe UI", 10),
    relief="flat",
    justify="center",
    width=8,
)
in_entry.pack(side="left", ipady=4, expand=True, fill="x", padx=(5, 0))
in_unit_lbl = tk.Label(
    standard_height_frame, text="in", font=("Segoe UI", 8, "bold")
)
in_unit_lbl.pack(side="left", padx=4)

metric_height_frame = tk.Frame(height_wrapper)
cm_entry = tk.Entry(
    metric_height_frame,
    font=("Segoe UI", 10),
    relief="flat",
    justify="center",
)
cm_entry.pack(fill="x", ipady=4)

weight_title_label = tk.Label(card, text="Weight", font=("Segoe UI", 9, "bold"))
weight_title_label.pack(anchor="w", padx=30, pady=(2, 0))

weight_sub_label = tk.Label(
    card, text="Pounds (lbs)", font=("Segoe UI", 8, "italic")
)
weight_sub_label.pack(anchor="w", padx=30, pady=(0, 2))

weight_entry = tk.Entry(
    card, font=("Segoe UI", 10), relief="flat", justify="center"
)
weight_entry.pack(fill="x", padx=30, pady=(2, 8), ipady=4)

canvas_frame = tk.Frame(card)
canvas_frame.pack(pady=2)

gauge_canvas = tk.Canvas(
    canvas_frame, width=190, height=90, highlightthickness=0
)
gauge_canvas.pack()

feedback_label = tk.Label(
    card, text="Enter values and press Enter", font=("Segoe UI", 9, "bold")
)
feedback_label.pack(pady=(4, 6))

btn_container = tk.Frame(card)
btn_container.pack(fill="x", padx=30, pady=2)

calc_btn = tk.Button(
    btn_container,
    text="Calculate BMI",
    font=("Segoe UI", 9, "bold"),
    relief="flat",
    cursor="hand2",
    pady=5,
    command=lambda: calculate_bmi(),
)
calc_btn.pack(fill="x", pady=(0, 4))

secondary_btn_frame = tk.Frame(btn_container)
secondary_btn_frame.pack(fill="x")

undo_btn = tk.Button(
    secondary_btn_frame,
    text="Undo",
    font=("Segoe UI", 8),
    relief="flat",
    cursor="hand2",
    pady=3,
    command=lambda: undo_last_input(),
)
undo_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))

clear_btn = tk.Button(
    secondary_btn_frame,
    text="Reset Form",
    font=("Segoe UI", 8),
    relief="flat",
    cursor="hand2",
    pady=3,
    command=lambda: confirm_and_clear(),
)
clear_btn.pack(side="right", expand=True, fill="x", padx=(2, 0))

disclaimer_label = tk.Label(
    card,
    text="Disclaimer: BMI is a screening metric and not a medical diagnosis.",
    font=("Segoe UI", 8, "italic"),
    wraplength=280,
    justify="center",
)
disclaimer_label.pack(side="bottom", pady=(5, 10))


# --- Business Logic & Navigation ---
def push_input_state():
    input_history_stack.append({
        "ft": ft_entry.get(),
        "in": in_entry.get(),
        "cm": cm_entry.get(),
        "weight": weight_entry.get(),
        "system": current_system.get(),
    })


def undo_last_input():
    if not input_history_stack:
        messagebox.showinfo("Undo", "No previous state to undo.")
        return
    last_state = input_history_stack.pop()
    switch_units(last_state["system"])
    ft_entry.delete(0, tk.END)
    ft_entry.insert(0, last_state["ft"])
    in_entry.delete(0, tk.END)
    in_entry.insert(0, last_state["in"])
    cm_entry.delete(0, tk.END)
    cm_entry.insert(0, last_state["cm"])
    weight_entry.delete(0, tk.END)
    weight_entry.insert(0, last_state["weight"])
    reset_result()


def confirm_and_clear():
    if messagebox.askyesno(
        "Confirm Reset", "Are you sure you want to clear all fields?"
    ):
        push_input_state()
        clear_all()


def apply_theme():
    t = THEMES[current_theme]
    root.config(bg=t["bg"])
    top_bar.config(bg=t["bg"])
    font_frame.config(bg=t["bg"])
    font_label.config(bg=t["bg"], fg=t["fg"])
    card.config(bg=t["card"])

    f_title = ("Segoe UI", 15 + font_delta, "bold")
    f_body = ("Segoe UI", 9 + font_delta, "bold")
    f_sub = ("Segoe UI", 8 + font_delta, "italic")

    title_label.config(bg=t["card"], fg=t["fg"], font=f_title)
    theme_btn.config(
        bg=t["toggle_bg"],
        fg=t["fg"],
        activebackground=t["toggle_bg"],
        activeforeground=t["fg"],
        text="☀️ Light" if current_theme == "dark" else "🌙 Dark",
    )
    history_btn.config(bg=t["btn_sec"], fg=t["btn_sec_fg"])
    btn_font_minus.config(bg=t["btn_sec"], fg=t["btn_sec_fg"])
    btn_font_plus.config(bg=t["btn_sec"], fg=t["btn_sec_fg"])

    for w in [
        height_label,
        weight_title_label,
        target_label,
        ft_unit_lbl,
        in_unit_lbl,
    ]:
        w.config(bg=t["card"], fg=t["fg"], font=f_body)

    for w in [height_sub_label, weight_sub_label]:
        w.config(bg=t["card"], fg=t["subtext"], font=f_sub)

    disclaimer_label.config(bg=t["card"], fg=t["disclaimer"], font=f_sub)

    for f in [
        toggle_frame,
        target_container,
        height_wrapper,
        standard_height_frame,
        metric_height_frame,
        canvas_frame,
        btn_container,
        secondary_btn_frame,
    ]:
        f.config(bg=t["card"])

    for e in [ft_entry, in_entry, cm_entry, weight_entry]:
        e.config(
            bg=t["entry_bg"],
            fg=t["entry_fg"],
            insertbackground=t["entry_fg"],
            highlightthickness=1,
            highlightbackground=t["entry_border"],
            highlightcolor=t["accent"],
        )

    target_menu.config(
        bg=t["entry_bg"],
        fg=t["entry_fg"],
        activebackground=t["btn_sec"],
        activeforeground=t["entry_fg"],
    )
    target_menu["menu"].config(
        bg=t["entry_bg"], fg=t["entry_fg"], activebackground=t["accent"]
    )

    calc_btn.config(
        bg=t["accent"],
        fg="#ffffff",
        activebackground=t["accent_hover"],
        activeforeground="#ffffff",
        font=f_body,
    )
    undo_btn.config(
        bg=t["btn_sec"],
        fg=t["btn_sec_fg"],
        activebackground=t["entry_border"],
        activeforeground=t["fg"],
    )
    clear_btn.config(
        bg=t["btn_sec"],
        fg=t["btn_sec_fg"],
        activebackground=t["entry_border"],
        activeforeground=t["fg"],
    )

    switch_units(current_system.get())


def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()
    update_preferences()
    if weight_entry.get().strip() and (
        ft_entry.get().strip() or cm_entry.get().strip()
    ):
        calculate_bmi()
    else:
        reset_result()


def switch_units(system):
    current_system.set(system)
    update_preferences()
    t = THEMES[current_theme]
    if system == "Standard":
        std_btn.config(bg=t["accent"], fg="#ffffff")
        met_btn.config(bg=t["btn_sec"], fg=t["btn_sec_fg"])
        height_sub_label.config(text="Feet & Inches")
        weight_sub_label.config(text="Pounds (lbs)")
        metric_height_frame.pack_forget()
        standard_height_frame.pack(fill="x")
        ft_entry.focus_set()
    else:
        met_btn.config(bg=t["accent"], fg="#ffffff")
        std_btn.config(bg=t["btn_sec"], fg=t["btn_sec_fg"])
        height_sub_label.config(text="Centimeters (cm)")
        weight_sub_label.config(text="Kilograms (kg)")
        standard_height_frame.pack_forget()
        metric_height_frame.pack(fill="x")
        cm_entry.focus_set()
    reset_result()


def calculate_bmi(event=None):
    t = THEMES[current_theme]
    try:
        push_input_state()
        system = current_system.get()
        if system == "Standard":
            ft_str = ft_entry.get().strip()
            in_str = in_entry.get().strip()
            if not ft_str and not in_str:
                show_error("Please enter your height.")
                return
            ft_val = float(ft_str or 0)
            in_val = float(in_str or 0)
            total_inches = (ft_val * 12) + in_val
            if total_inches <= 0 or total_inches > 120:
                show_error("Invalid height input.")
                return
            height_m = total_inches * 0.0254
        else:
            cm_str = cm_entry.get().strip()
            if not cm_str:
                show_error("Please enter your height.")
                return
            cm_val = float(cm_str)
            if cm_val <= 0 or cm_val > 300:
                show_error("Invalid height input.")
                return
            height_m = cm_val / 100

        weight_str = weight_entry.get().strip()
        if not weight_str:
            show_error("Please enter your weight.")
            return
        weight_val = float(weight_str)
        if weight_val <= 0 or weight_val > 1000:
            show_error("Invalid weight input.")
            return

        weight_kg = (
            weight_val if system == "Metric" else weight_val * 0.45359237
        )
        bmi = weight_kg / (height_m**2)

        if bmi < 10 or bmi > 100:
            show_error("Invalid input result.")
            return

        if bmi < 18.5:
            category, color = "Underweight", t["underweight"]
        elif 18.5 <= bmi < 25:
            category, color = "Normal weight", t["normal"]
        elif 25 <= bmi < 30:
            category, color = "Overweight", t["overweight"]
        else:
            category, color = "Obese", t["obese"]

        if "Child" in age_group_var.get():
            category += " (Child Est.)"

        feedback_label.config(
            text=f"BMI: {bmi:.2f} — {category}", fg=color, bg=t["card"]
        )
        draw_gauge(gauge_canvas, t, bmi)

        save_history_record({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "bmi": round(bmi, 2),
            "category": category,
        })

    except ValueError:
        show_error("Invalid input! Numbers only.")


def show_error(message):
    t = THEMES[current_theme]
    feedback_label.config(text=message, fg=t["obese"], bg=t["card"])
    draw_gauge(gauge_canvas, t, 0)


def reset_result():
    t = THEMES[current_theme]
    feedback_label.config(
        text="Enter values and press Enter", fg=t["subtext"], bg=t["card"]
    )
    draw_gauge(gauge_canvas, t, 0)


def clear_all():
    ft_entry.delete(0, tk.END)
    in_entry.delete(0, tk.END)
    cm_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    reset_result()
    if current_system.get() == "Standard":
        ft_entry.focus_set()
    else:
        cm_entry.focus_set()


# Keyboard Navigation Logic
def focus_next_widget(current_widget, direction):
    if current_system.get() == "Standard":
        if current_widget == ft_entry and direction in ("right", "down"):
            in_entry.focus_set()
        elif current_widget == in_entry:
            if direction in ("left", "up", "backspace"):
                ft_entry.focus_set()
            elif direction in ("right", "down"):
                weight_entry.focus_set()
        elif current_widget == weight_entry and direction in (
            "left",
            "up",
            "backspace",
        ):
            in_entry.focus_set()
    else:
        if current_widget == cm_entry and direction in ("right", "down"):
            weight_entry.focus_set()
        elif current_widget == weight_entry and direction in (
            "left",
            "up",
            "backspace",
        ):
            cm_entry.focus_set()


def handle_backspace(event, current_widget):
    if len(current_widget.get()) == 0:
        focus_next_widget(current_widget, "backspace")


# Keybindings
ft_entry.bind("<Right>", lambda e: focus_next_widget(ft_entry, "right"))
ft_entry.bind("<Down>", lambda e: focus_next_widget(ft_entry, "down"))

in_entry.bind("<Left>", lambda e: focus_next_widget(in_entry, "left"))
in_entry.bind("<Up>", lambda e: focus_next_widget(in_entry, "up"))
in_entry.bind("<Right>", lambda e: focus_next_widget(in_entry, "right"))
in_entry.bind("<Down>", lambda e: focus_next_widget(in_entry, "down"))
in_entry.bind("<BackSpace>", lambda e: handle_backspace(e, in_entry))

cm_entry.bind("<Right>", lambda e: focus_next_widget(cm_entry, "right"))
cm_entry.bind("<Down>", lambda e: focus_next_widget(cm_entry, "down"))

weight_entry.bind("<Left>", lambda e: focus_next_widget(weight_entry, "left"))
weight_entry.bind("<Up>", lambda e: focus_next_widget(weight_entry, "up"))
weight_entry.bind("<BackSpace>", lambda e: handle_backspace(e, weight_entry))

ft_entry.bind("<Return>", lambda e: in_entry.focus_set())
in_entry.bind("<Return>", lambda e: weight_entry.focus_set())
cm_entry.bind("<Return>", lambda e: weight_entry.focus_set())
weight_entry.bind("<Return>", calculate_bmi)
root.bind("<Return>", calculate_bmi)
root.bind("<Control-z>", lambda e: undo_last_input())

apply_theme()
root.mainloop()