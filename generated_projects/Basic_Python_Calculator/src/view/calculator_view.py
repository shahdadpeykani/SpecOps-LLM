import tkinter as tk
from tkinter import ttk
from src.common.observer import Observer

class CalculatorView(tk.Frame, Observer):
    """
    The View in the MVC pattern for the calculator.
    It creates and manages the graphical user interface using Tkinter.
    It observes the CalculatorModel for state changes and updates its display accordingly.
    """

    # Dark mode theme colors
    DARK_THEME = {
        "bg_primary": "#2E2E2E",    # Main background
        "bg_secondary": "#3C3C3C", # Button background (numbers)
        "bg_tertiary": "#555555",   # Operator button background
        "fg_primary": "#FFFFFF",    # Text color (display, numbers)
        "fg_secondary": "#DDDDDD",  # Text color (operators)
        "border": "#1E1E1E",       # Widget border
        "active_bg": "#666666",    # Button active background
        "display_bg": "#1A1A1A"    # Display background
    }

    def __init__(self, master):
        """
        Initializes the CalculatorView.
        :param master: The root Tkinter window.
        """
        super().__init__(master)
        self.master = master
        self.controller = None
        self.pack(expand=True, fill='both')
        self._apply_dark_theme()
        self._create_widgets()

    def _apply_dark_theme(self):
        """
        Applies the dark mode theme to the Tkinter window and widgets.
        """
        self.master.config(bg=self.DARK_THEME["bg_primary"])
        # Configure ttk styles for consistency
        style = ttk.Style()
        style.theme_use('clam') # 'clam' theme is easier to customize than 'default'

        style.configure('TFrame', background=self.DARK_THEME["bg_primary"])
        style.configure('TButton', 
                        background=self.DARK_THEME["bg_secondary"],
                        foreground=self.DARK_THEME["fg_primary"],
                        font=('Arial', 18),
                        relief='flat',
                        borderwidth=0,
                        padding=(10, 5))
        style.map('TButton', 
                  background=[('active', self.DARK_THEME["active_bg"])],
                  foreground=[('active', self.DARK_THEME["fg_primary"])])

        style.configure('Operator.TButton', 
                        background=self.DARK_THEME["bg_tertiary"],
                        foreground=self.DARK_THEME["fg_secondary"])
        style.map('Operator.TButton', 
                  background=[('active', self.DARK_THEME["active_bg"])],
                  foreground=[('active', self.DARK_THEME["fg_primary"])])

        style.configure('Display.TEntry', 
                        fieldbackground=self.DARK_THEME["display_bg"],
                        foreground=self.DARK_THEME["fg_primary"],
                        font=('Arial', 28, 'bold'),
                        borderwidth=0,
                        relief='flat',
                        padding=(5, 5))
        
        # Fallback for Entry (if not using ttk.Entry directly, or for other widgets)
        self.master.option_add('*Entry.Background', self.DARK_THEME["display_bg"])
        self.master.option_add('*Entry.Foreground', self.DARK_THEME["fg_primary"])
        self.master.option_add('*Entry.Font', ('Arial', 28, 'bold'))
        self.master.option_add('*Entry.InsertBackground', self.DARK_THEME["fg_primary"])
        self.master.option_add('*Entry.Borderwidth', 0)
        self.master.option_add('*Entry.Relief', 'flat')


    def _create_widgets(self):
        """
        Creates all the UI widgets (display, buttons) and lays them out.
        """
        # Display for results and input
        self.display = ttk.Entry(self, textvariable=tk.StringVar(), 
                                 justify='right', state='readonly', 
                                 style='Display.TEntry')
        self.display.grid(row=0, column=0, columnspan=4, sticky='nsew', pady=5, padx=5)

        # Calculator button layout
        buttons = [
            ('C', 1, 0, 'Operator.TButton'), ('/', 1, 3, 'Operator.TButton'),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3, 'Operator.TButton'),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3, 'Operator.TButton'),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3, 'Operator.TButton'),
            ('0', 5, 0, None, 2), ('.', 5, 2), ('=', 5, 3, 'Operator.TButton')
        ]

        # Create buttons and bind commands
        button_specs = [
            (b[0], b[1], b[2], b[3] if len(b) > 3 else None, b[4] if len(b) > 4 else 1) 
            for b in buttons
        ]
        for (text, row, col, style_name, columnspan) in button_specs:
            
            btn = ttk.Button(self, text=text, style=style_name if style_name else 'TButton')
            btn.grid(row=row, column=col, columnspan=columnspan, sticky='nsew', padx=2, pady=2)

            if text == 'C':
                btn.config(command=self._on_clear_click)
            elif text in '0123456789.':
                btn.config(command=lambda t=text: self._on_digit_click(t))
            elif text in '+-*/':
                btn.config(command=lambda t=text: self._on_operator_click(t))
            elif text == '=':
                btn.config(command=self._on_equals_click)

        # Configure grid weights to make buttons expand proportionally
        for i in range(6): # 0 for display, 1-5 for buttons
            self.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

    def set_controller(self, controller):
        """
        Sets the controller for the view, allowing button commands to trigger controller actions.
        :param controller: An instance of CalculatorController.
        """
        self.controller = controller

    def update(self, display_value: str):
        """
        Observer's update method. Called by the Model when its state changes.
        Updates the display Entry widget with the new value.
        :param display_value: The string value to display.
        """
        self.update_display(display_value)

    def update_display(self, value: str):
        """
        Directly updates the text in the display entry.
        """
        self.display.config(state='normal') # Make editable to update
        self.display.delete(0, tk.END)
        self.display.insert(0, value)
        self.display.config(state='readonly') # Set back to read-only

    # --- Button Command Handlers (delegated to controller) ---

    def _on_digit_click(self, digit: str):
        """
        Handles digit button clicks, delegating to the controller.
        :param digit: The digit or decimal point clicked.
        """
        if self.controller:
            self.controller.handle_digit_input(digit)

    def _on_operator_click(self, operator: str):
        """
        Handles operator button clicks, delegating to the controller.
        :param operator: The operator clicked (+, -, *, /).
        """
        if self.controller:
            self.controller.handle_operator_input(operator)

    def _on_equals_click(self):
        """
        Handles the equals button click, delegating to the controller.
        """
        if self.controller:
            self.controller.handle_equals()

    def _on_clear_click(self):
        """
        Handles the clear button click, delegating to the controller.
        """
        if self.controller:
            self.controller.handle_clear()
