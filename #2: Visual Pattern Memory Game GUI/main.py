import tkinter as tk
from gui import VisualPatternMemoryGame

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualPatternMemoryGame(root)
    root.mainloop()