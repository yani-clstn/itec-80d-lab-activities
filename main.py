import tkinter as tk
import math

# Initialize the main application window
root = tk.Tk()
root.title("BMI Calculator - Modern HCI")
root.geometry("460x860")
root.config(bg="#f4f6f9")  # Clean, modern light background

# --- State Variables ---
current_system = tk.StringVar(value="Metric")  # "Metric" or "Imperial"
age_group_var = tk.StringVar(value="Adult")      # "Adult" or "Child"

# --- Top Header Section ---
header_frame = tk.Frame(root, bg="#f4f6f9")
header_frame.pack(fill="x", padx=25, pady=(15, 10))

title_label = tk.Label(header_frame, text="BMI Calculator", font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#1a202c")
title_label.pack(anchor="w")

subtitle_label = tk.Label(header_frame, text="Check your Body Mass Index and what it means.", font=("Segoe UI", 10), bg="#f4f6f9", fg="#4a5568")
subtitle_label.pack(anchor="w", pady=(2, 0))


# --- Main Input Card Container ---
card_frame = tk.Frame(root, bg="#ffffff", highlightbackground="#cbd5e0", highlightthickness=1)
card_frame.pack(fill="x", padx=25, pady=5, ipadx=10, ipady=10)

# 1. Measurement Units Selection (Radio Buttons)
units_label = tk.Label(card_frame, text="Measurement Units", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2d3748")
units_label.pack(anchor="w", padx=15, pady=(10, 5))

radio_frame = tk.Frame(card_frame, bg="#ffffff")
radio_frame.pack(anchor="w", padx=15, pady=2)

def switch_system():
    system = current_system.get()
    if system == "Metric":
        metric_height_frame.pack(fill="x")
        imperial_height_frame.pack_forget()
        height_title_label.config(text="Height (cm):")
        weight_title_label.config(text="Weight (kg):")
    else:
        metric_height_frame.pack_forget()
        imperial_height_frame.pack(fill="x")
        height_title_label.config(text="Height (ft / in):")
        weight_title_label.config(text="Weight (lbs):")
    calculate_bmi()

metric_rb = tk.Radiobutton(radio_frame, text="Metric (cm / kg)", variable=current_system, value="Metric", 
                           font=("Segoe UI", 10), bg="#ffffff", activebackground="#ffffff", command=switch_system)
metric_rb.pack(side="left", padx=(0, 15))

imperial_rb = tk.Radiobutton(radio_frame, text="Imperial (in / lb)", variable=current_system, value="Imperial", 
                             font=("Segoe UI", 10), bg="#ffffff", activebackground="#ffffff", command=switch_system)
imperial_rb.pack(side="left")


# 2. Target Group Selection
target_label = tk.Label(card_frame, text="Target Group:", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2d3748")
target_label.pack(anchor="w", padx=15, pady=(12, 2))

target_frame = tk.Frame(card_frame, bg="#ffffff")
target_frame.pack(fill="x", padx=15, pady=2)
target_menu = tk.OptionMenu(target_frame, age_group_var, "Adult", "Child (2-19 yrs)", command=lambda _: calculate_bmi())
target_menu.config(font=("Segoe UI", 10), bg="#e2e8f0", relief="flat", highlightthickness=0, anchor="w")
target_menu.pack(fill="x", ipady=2)


# 3. Height Section (Strictly above weight)
height_title_label = tk.Label(card_frame, text="Height (cm):", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2d3748")
height_title_label.pack(anchor="w", padx=15, pady=(12, 2))

# Dedicated Height Wrapper Frame
height_wrapper = tk.Frame(card_frame, bg="#ffffff")
height_wrapper.pack(fill="x", padx=15, pady=2)

# Metric Height Input Frame
metric_height_frame = tk.Frame(height_wrapper, bg="#ffffff")
metric_height_frame.pack(fill="x")
cm_entry = tk.Entry(metric_height_frame, font=("Segoe UI", 11), relief="solid", bd=1, highlightthickness=0)
cm_entry.pack(fill="x", ipady=4)

# Imperial Height Input Frame (Feet & Inches) - Hidden by default
imperial_height_frame = tk.Frame(height_wrapper, bg="#ffffff")
ft_entry = tk.Entry(imperial_height_frame, font=("Segoe UI", 11), relief="solid", bd=1, width=8)
ft_entry.pack(side="left", fill="x", expand=True, ipady=4)
tk.Label(imperial_height_frame, text="ft", font=("Segoe UI", 10), bg="#ffffff").pack(side="left", padx=5)
in_entry = tk.Entry(imperial_height_frame, font=("Segoe UI", 11), relief="solid", bd=1, width=8)
in_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(5, 0))
tk.Label(imperial_height_frame, text="in", font=("Segoe UI", 10), bg="#ffffff").pack(side="left", padx=5)


# 4. Weight Section (Strictly below height inputs)
weight_title_label = tk.Label(card_frame, text="Weight (kg):", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2d3748")
weight_title_label.pack(anchor="w", padx=15, pady=(12, 2))

weight_frame = tk.Frame(card_frame, bg="#ffffff")
weight_frame.pack(fill="x", padx=15, pady=(2, 10))
weight_entry = tk.Entry(weight_frame, font=("Segoe UI", 11), relief="solid", bd=1)
weight_entry.pack(fill="x", ipady=4)


# --- Bottom Visual Gauge & Result Card ---
result_card = tk.Frame(root, bg="#ffffff", highlightbackground="#cbd5e0", highlightthickness=1)
result_card.pack(fill="x", padx=25, pady=5, ipadx=10, ipady=10)

canvas_frame = tk.Frame(result_card, bg="#ffffff")
canvas_frame.pack(pady=2)

gauge_canvas = tk.Canvas(canvas_frame, width=240, height=110, bg="#ffffff", highlightthickness=0)
gauge_canvas.pack()

def draw_gauge(bmi_val=0):
    """Draws an accurate interactive gauge arc matching needle angles to BMI ranges."""
    gauge_canvas.delete("all")
    colors = ["#3182ce", "#38a169", "#d69e2e", "#e53e3e"]  # Blue (Under), Green (Normal), Yellow (Over), Red (Obese)
    extent_angle = 180 / len(colors)
    
    for i, color in enumerate(colors):
        gauge_canvas.create_arc(15, 15, 225, 225, start=i * extent_angle, extent=extent_angle, fill=color, outline="white", width=2)
        
    gauge_canvas.create_oval(60, 60, 180, 180, fill="#ffffff", outline="#ffffff")
    
    if bmi_val > 0:
        capped_bmi = max(10, min(45, bmi_val))
        # Corrected angle calculation mapping low BMI to right (0°) and high BMI to left (180°)
        angle = ((capped_bmi - 10) / 35) * 180
        rad = math.radians(angle)
        cx, cy, length = 120, 120, 55
        nx = cx + length * math.cos(rad)
        ny = cy - length * math.sin(rad)
        gauge_canvas.create_line(cx, cy, nx, ny, fill="#1a202c", width=3, arrow=tk.LAST)
        gauge_canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill="#1a202c")

draw_gauge(0)

bmi_value_label = tk.Label(result_card, text="Enter values above", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#4a5568")
bmi_value_label.pack(pady=(2, 0))

bmi_category_label = tk.Label(result_card, text="", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#38a169")
bmi_category_label.pack(pady=(0, 5))


# --- Action Buttons Container ---
btn_frame = tk.Frame(root, bg="#f4f6f9")
btn_frame.pack(fill="x", padx=25, pady=8)

clear_btn = tk.Button(
    btn_frame, text="Reset Form", font=("Segoe UI", 10), 
    bg="#ffffff", fg="#2d3748", activebackground="#edf2f7", activeforeground="#1a202c",
    relief="solid", bd=1, cursor="hand2", padx=20, pady=6, command=lambda: clear_all()
)
clear_btn.pack(fill="x", expand=True)


# --- Core Logic & Real-Time Calculation ---
def calculate_bmi(event=None):
    try:
        system = current_system.get()
        
        # Height parsing
        if system == "Metric":
            cm_str = cm_entry.get().strip()
            if not cm_str:
                reset_result()
                return
            cm_val = float(cm_str)
            if cm_val <= 0:
                reset_result()
                return
            height_m = cm_val / 100
        else:
            ft_str = ft_entry.get().strip()
            in_str = in_entry.get().strip()
            if not ft_str and not in_str:
                reset_result()
                return
            ft_val = float(ft_str or 0)
            in_val = float(in_str or 0)
            total_inches = (ft_val * 12) + in_val
            if total_inches <= 0:
                reset_result()
                return
            height_m = total_inches * 0.0254

        # Weight parsing
        weight_str = weight_entry.get().strip()
        if not weight_str:
            reset_result()
            return
        weight_val = float(weight_str)
        if weight_val <= 0:
            reset_result()
            return
            
        if system == "Metric":
            weight_kg = weight_val
        else:
            weight_kg = weight_val * 0.45359237

        # BMI Calculation
        bmi = weight_kg / (height_m ** 2)

        # Categorization
        is_child = "Child" in age_group_var.get()
        if bmi < 18.5:
            category, color = "Underweight", "#3182ce"
        elif 18.5 <= bmi < 25:
            category, color = "Normal weight", "#38a169"
        elif 25 <= bmi < 30:
            category, color = "Overweight", "#d69e2e"
        else:
            category, color = "Obese", "#e53e3e"

        if is_child:
            category += " (Child Est.)"

        bmi_value_label.config(text=f"BMI: {bmi:.2f}", fg="#1a202c")
        bmi_category_label.config(text=category, fg=color)
        draw_gauge(bmi)

    except ValueError:
        reset_result()

def reset_result():
    bmi_value_label.config(text="Enter values above", fg="#4a5568")
    bmi_category_label.config(text="")
    draw_gauge(0)

def clear_all():
    cm_entry.delete(0, tk.END)
    ft_entry.delete(0, tk.END)
    in_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    reset_result()

# --- Key Bindings for Real-Time Reactivity ---
cm_entry.bind("<KeyRelease>", calculate_bmi)
ft_entry.bind("<KeyRelease>", calculate_bmi)
in_entry.bind("<KeyRelease>", calculate_bmi)
weight_entry.bind("<KeyRelease>", calculate_bmi)

root.mainloop()