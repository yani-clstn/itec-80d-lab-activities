import tkinter as tk
import math

# Initialize the main application window
root = tk.Tk()
root.title("BMI Calculator - Modern HCI")
root.geometry("440x820")
root.config(bg="#f8f9fa")

# --- State Variables ---
current_system = tk.StringVar(value="Standard")  # "Standard" or "Metric"
age_group_var = tk.StringVar(value="Adult")

# --- Main Container Frame ---
main_frame = tk.Frame(root, bg="#f8f9fa")
main_frame.pack(fill="both", expand=True, padx=25, pady=20)

# Title Section
title_label = tk.Label(main_frame, text="Body Mass Index Calculator", font=("Segoe UI", 16, "bold"), bg="#f8f9fa", fg="#1a365d")
title_label.pack(pady=(0, 15))

# --- Unit Toggle Buttons (Standard / Metric) ---
toggle_frame = tk.Frame(main_frame, bg="#f8f9fa")
toggle_frame.pack(pady=(0, 15))

def switch_units(system):
    current_system.set(system)
    if system == "Standard":
        std_btn.config(bg="#1d4ed8", fg="#ffffff", relief="flat")
        met_btn.config(bg="#ffffff", fg="#1a202c", relief="solid", bd=1)
        height_sub_label.config(text="Feet & Inches")
        weight_sub_label.config(text="Pounds (lbs)")
        metric_height_frame.pack_forget()
        standard_height_frame.pack(fill="x")
    else:
        met_btn.config(bg="#1d4ed8", fg="#ffffff", relief="flat")
        std_btn.config(bg="#ffffff", fg="#1a202c", relief="solid", bd=1)
        height_sub_label.config(text="Centimeters (cm)")
        weight_sub_label.config(text="Kilograms (kg)")
        standard_height_frame.pack_forget()
        metric_height_frame.pack(fill="x")
    reset_result()

std_btn = tk.Button(toggle_frame, text="Standard", font=("Segoe UI", 10, "bold"), width=10, pady=6, command=lambda: switch_units("Standard"))
std_btn.pack(side="left")

met_btn = tk.Button(toggle_frame, text="Metric", font=("Segoe UI", 10, "bold"), width=10, pady=6, command=lambda: switch_units("Metric"))
met_btn.pack(side="left", padx=5)

# --- Target Group Section ---
target_container = tk.Frame(main_frame, bg="#f8f9fa")
target_container.pack(fill="x", pady=(0, 10))

target_label = tk.Label(target_container, text="Target Group:", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#2d3748")
target_label.pack(side="left", padx=(0, 10))

target_menu = tk.OptionMenu(target_container, age_group_var, "Adult", "Child (2-19 yrs)", command=lambda _: reset_result())
target_menu.config(font=("Segoe UI", 10), bg="#e2e8f0", relief="flat", highlightthickness=0, width=12)
target_menu.pack(side="left")

# --- Height Section ---
height_label = tk.Label(main_frame, text="Height", font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg="#1a202c")
height_label.pack(anchor="w", pady=(5, 0))

height_sub_label = tk.Label(main_frame, text="Feet & Inches", font=("Segoe UI", 8, "italic"), bg="#f8f9fa", fg="#718096")
height_sub_label.pack(anchor="w", pady=(0, 2))

# Dedicated Height Container Wrapper
height_wrapper = tk.Frame(main_frame, bg="#f8f9fa")
height_wrapper.pack(fill="x", pady=(2, 5))

# Standard Height Frame (Feet & Inches)
standard_height_frame = tk.Frame(height_wrapper, bg="#f8f9fa")
ft_entry = tk.Entry(standard_height_frame, font=("Segoe UI", 11), relief="solid", bd=1, width=10)
ft_entry.pack(side="left", fill="x", expand=True, ipady=4)
tk.Label(standard_height_frame, text="ft", font=("Segoe UI", 10), bg="#f8f9fa").pack(side="left", padx=6)

in_entry = tk.Entry(standard_height_frame, font=("Segoe UI", 11), relief="solid", bd=1, width=10)
in_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(5, 0))
tk.Label(standard_height_frame, text="in", font=("Segoe UI", 10), bg="#f8f9fa").pack(side="left", padx=6)

# Metric Height Frame (Centimeters)
metric_height_frame = tk.Frame(height_wrapper, bg="#f8f9fa")
cm_entry = tk.Entry(metric_height_frame, font=("Segoe UI", 11), relief="solid", bd=1)
cm_entry.pack(fill="x", ipady=4)

# --- Weight Section ---
weight_title_label = tk.Label(main_frame, text="Weight", font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg="#1a202c")
weight_title_label.pack(anchor="w", pady=(10, 0))

weight_sub_label = tk.Label(main_frame, text="Pounds (lbs)", font=("Segoe UI", 8, "italic"), bg="#f8f9fa", fg="#718096")
weight_sub_label.pack(anchor="w", pady=(0, 2))

weight_entry = tk.Entry(main_frame, font=("Segoe UI", 11), relief="solid", bd=1)
weight_entry.pack(fill="x", pady=(2, 10), ipady=4)

# --- Gauge & Result Canvas ---
canvas_frame = tk.Frame(main_frame, bg="#f8f9fa")
canvas_frame.pack(pady=2)

gauge_canvas = tk.Canvas(canvas_frame, width=220, height=100, bg="#f8f9fa", highlightthickness=0)
gauge_canvas.pack()

def draw_gauge(bmi_val=0):
    gauge_canvas.delete("all")
    colors = ["#3182ce", "#38a169", "#d69e2e", "#e53e3e"]
    extent_angle = 180 / len(colors)
    
    for i, color in enumerate(colors):
        start_deg = 180 - ((i + 1) * extent_angle)
        gauge_canvas.create_arc(10, 10, 210, 210, start=start_deg, extent=extent_angle, fill=color, outline="white", width=2)
        
    gauge_canvas.create_oval(55, 55, 165, 165, fill="#f8f9fa", outline="#f8f9fa")
    
    if bmi_val > 0:
        capped_bmi = max(10, min(45, bmi_val))
        angle = 180 - ((capped_bmi - 10) / 35) * 180
        rad = math.radians(angle)
        cx, cy, length = 110, 110, 45
        nx = cx + length * math.cos(rad)
        ny = cy - length * math.sin(rad)
        gauge_canvas.create_line(cx, cy, nx, ny, fill="#1a202c", width=2.5, arrow=tk.LAST)
        gauge_canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#1a202c")

draw_gauge(0)

# Single-line feedback label
feedback_label = tk.Label(main_frame, text="Enter values and click Calculate", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#4a5568")
feedback_label.pack(pady=(2, 8))

# --- Action Buttons Container ---
btn_container = tk.Frame(main_frame, bg="#f8f9fa")
btn_container.pack(fill="x", pady=2)

calc_btn = tk.Button(
    btn_container, text="Calculate BMI", font=("Segoe UI", 10, "bold"), 
    bg="#1d4ed8", fg="#ffffff", activebackground="#1e40af", activeforeground="#ffffff",
    relief="flat", cursor="hand2", pady=6, command=lambda: calculate_bmi()
)
calc_btn.pack(fill="x", pady=(0, 5))

clear_btn = tk.Button(
    btn_container, text="Reset Form", font=("Segoe UI", 9), 
    bg="#e9ecef", fg="#495057", activebackground="#ced4da", activeforeground="#1a202c",
    relief="flat", cursor="hand2", pady=5, command=lambda: clear_all()
)
clear_btn.pack(fill="x")


# --- Calculation Logic with Validation ---
def calculate_bmi():
    try:
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

        weight_kg = weight_val if system == "Metric" else weight_val * 0.45359237
        bmi = weight_kg / (height_m ** 2)

        if bmi < 10 or bmi > 100:
            show_error("Invalid input result.")
            return

        if bmi < 18.5:
            category, color = "Underweight", "#3182ce"
        elif 18.5 <= bmi < 25:
            category, color = "Normal weight", "#38a169"
        elif 25 <= bmi < 30:
            category, color = "Overweight", "#d69e2e"
        else:
            category, color = "Obese", "#e53e3e"

        if "Child" in age_group_var.get():
            category += " (Child Est.)"

        feedback_label.config(text=f"BMI: {bmi:.2f} — {category}", fg=color)
        draw_gauge(bmi)

    except ValueError:
        show_error("Invalid input! Numbers only.")

def show_error(message):
    feedback_label.config(text=message, fg="#e53e3e")
    draw_gauge(0)

def reset_result():
    feedback_label.config(text="Enter values and click Calculate", fg="#4a5568")
    draw_gauge(0)

def clear_all():
    ft_entry.delete(0, tk.END)
    in_entry.delete(0, tk.END)
    cm_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    reset_result()

# Set initial active button appearance
switch_units("Standard")

root.mainloop()