Application Name: BMI Calculator
Developer: Kabigting, Althea Nicole C.
Framework Used: Tkinter
Python Version: Python 3.x (tested on 3.12)

Files Included:
    - main.py             : Main application entry point, layout, and event routing.
    - gauge.py            : Vector Canvas semi-circular gauge rendering logic.
    - history_window.py   : Secondary Toplevel window for calculation logs and search filtering.
    - storage.py          : File I/O module handling JSON persistence.
    - config.json         : Stores user preferences (Theme, Unit System, Font Size).
    - bmi_history.json    : Stores past BMI calculation logs.

How to Run:
    1. Make sure Python 3 is installed with Tkinter (included by default
       on Windows/macOS installers; on Linux install "python3-tk" if needed).
    2. Place all Python files (main.py, gauge.py, history_window.py, storage.py) 
       in the same directory.
    3. Open a terminal in the folder containing the files.
    4. Run: python main.py

Brief Description:
    A modern, modular BMI (Body Mass Index) Calculator built with Python and Tkinter.
    Users can calculate their Body Mass Index using either Standard (ft/in, lbs) or 
    Metric (cm, kg) measurement systems, select age group target references (Adult 
    vs. Child), and view real-time visual feedback via a custom semi-circular vector gauge. 
    The app validates inputs, prevents realistic range errors, and automatically saves 
    user preferences and calculation records across sessions.

Challenge Requirements Implemented:
    1. Dark/Light Interface Option: Dynamic theme switching with custom color palettes.
    2. Keyboard Shortcuts & Navigation: Enter to calculate/advance focus, Ctrl+Z to undo, 
       and arrow key/smart backspace focus transfer.
    3. Tooltips & Secondary Windows: Dedicated "Calculation History" secondary window (Toplevel).
    4. Search & Filter Functionality: Live query filtering in the History Log window.
    5. Confirmation Dialogs: Popup modal confirmation before resetting inputs.
    6. Undo Functionality: Reverts accidentally cleared inputs to their previous state.
    7. Persistent Data Storage: Automatically logs calculation history to JSON disk storage.
    8. User Preferences: Saves selected theme mode, measurement system, and font scaling.
    9. Accessibility Improvements: On-screen font size adjustment controls (A- / A+) 
       and high-contrast color choices.

HCI Usability Principles Applied:
    - Visibility: Color-coded semi-circular gauge and dynamic category text provide
      immediate visual feedback upon calculation.
    - Consistency: Standardized UI spacing, font hierarchies, button styling, and 
      modularized code architecture across light and dark themes.
    - Simplicity: Clear card-based layout hiding inactive unit inputs to minimize 
      visual clutter.
    - User Control: Complete freedom to toggle themes, adjust font scaling, switch unit 
      systems, undo input actions, and reset inputs with safety confirmations.
    - Error Prevention: Range and type validation on height/weight inputs preventing 
      non-numeric, negative, or physically unrealistic calculations.
    - Error Recovery: Explicit error status messages guiding the user without 
      locking or freezing the input controls.
    - Match the Real World: Labels and unit markers dynamically adapt to selected unit 
      systems (ft/in & lbs vs cm & kg).
    - Recognition Rather Than Recall: Direct visual controls for history viewing and 
      font scaling eliminate the need to memorize complex commands.
    - Accessibility: Large readable typography, customizable font scaling (A-/A+), and 
      high-contrast dark/light mode palettes for improved readability.