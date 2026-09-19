Application Name: BMI Calculator
Developer: Kabigting, Althea Nicole C.
Framework Used: Tkinter
Python Version: Python 3.x (tested on 3.12)
How to Run:
    1. Make sure Python 3 is installed with Tkinter (included by default
       on Windows/macOS installers; on Linux install "python3-tk" if needed).
    2. Open a terminal in the folder containing the file.
    3. Run: python main.py

Brief Description:
    A BMI (Body Mass Index) Calculator built with Tkinter. The user enters
    height and weight in either Metric (cm/kg) or Imperial (in/lb) units,
    chooses a classification reference (Standard WHO or Asian cut-offs),
    and clicks Calculate to see their BMI value and category. The app
    validates input (numeric, positive, realistic ranges), gives clear
    success/error feedback, includes a Clear/Reset button, and offers two
    challenge features: a Dark/Light theme toggle and keyboard shortcuts
    (Enter = Calculate, Esc = Clear).

HCI Usability Principles Applied:
    - Visibility: theme toggle, buttons, and current result are always
      visible; feedback appears immediately below the buttons.
    - Consistency: consistent fonts, spacing, colors, and terminology
      throughout (e.g., "Calculate", "Clear" used consistently).
    - Simplicity: only controls that serve the task are shown; no
      decorative or unnecessary elements.
    - User Control: user can freely switch units, switch classification
      standard, and reset the form at any time.
    - Error Prevention: numeric-only validation with realistic min/max
      ranges per unit system, checked before any calculation runs.
    - Error Recovery: clear, specific error messages (e.g., "Height must
      be a valid number (e.g., 165).") that tell the user exactly what to
      fix; the form is never locked after an error.
    - Match the Real World: field labels change to match the selected
      unit system (cm/kg vs in/lb) so terminology matches user input.
    - Recognition Rather Than Recall: keyboard shortcuts are printed
      directly on the buttons ("Calculate (Enter)") instead of requiring
      the user to remember them.
    - Affordance: buttons are clearly clickable (cursor changes, flat
      button styling); radio buttons and dropdown look and behave like
      standard OS controls.
    - Accessibility: high-contrast color choices in both themes, readable
      font sizes, and a dark mode option for users sensitive to bright
      screens.