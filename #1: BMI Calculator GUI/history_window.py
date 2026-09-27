import tkinter as tk
from storage import load_history


def open_history_window(root, theme):
    win = tk.Toplevel(root)
    win.title("Calculation History")
    win.geometry("380x420")
    win.config(bg=theme["bg"])

    top_f = tk.Frame(win, bg=theme["bg"])
    top_f.pack(fill="x", padx=10, pady=8)

    tk.Label(
        top_f,
        text="Search:",
        font=("Segoe UI", 9, "bold"),
        bg=theme["bg"],
        fg=theme["fg"],
    ).pack(side="left", padx=(0, 4))
    search_entry = tk.Entry(
        top_f,
        font=("Segoe UI", 9),
        relief="flat",
        bg=theme["entry_bg"],
        fg=theme["entry_fg"],
    )
    search_entry.pack(side="left", fill="x", expand=True)

    list_frame = tk.Frame(win, bg=theme["bg"])
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    history_listbox = tk.Listbox(
        list_frame,
        font=("Segoe UI", 9),
        yscrollcommand=scrollbar.set,
        bg=theme["entry_bg"],
        fg=theme["entry_fg"],
        relief="flat",
    )
    history_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=history_listbox.yview)

    def populate_history(query=""):
        history_listbox.delete(0, tk.END)
        records = load_history()
        for r in reversed(records):
            text = f"{r['date']} | BMI: {r['bmi']} ({r['category']})"
            if query.lower() in text.lower():
                history_listbox.insert(tk.END, text)

    search_entry.bind(
        "<KeyRelease>", lambda e: populate_history(search_entry.get().strip())
    )
    populate_history()