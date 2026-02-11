import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from src.model.calculator_model import CalculatorModel
from src.view.calculator_view import CalculatorView
from src.controller.calculator_controller import CalculatorController

def main():
    """
    Main entry point for the Basic Python Calculator application.
    Initializes the MVC components and starts the Tkinter event loop.
    """
    root = tk.Tk()
    root.title("Basic Python Calculator")

    # Model initialization
    model = CalculatorModel()

    # View initialization
    view = CalculatorView(root)

    # Controller initialization
    controller = CalculatorController(model, view)

    # Connect View to Controller and Model
    view.set_controller(controller)
    model.add_observer(view) # View observes Model for state changes

    # Initial display update
    view.update_display(model.get_display_value())

    root.mainloop()

if __name__ == "__main__":
    main()
