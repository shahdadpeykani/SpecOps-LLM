from src.model.calculator_model import CalculatorModel
from src.view.calculator_view import CalculatorView # Imported for type hinting

class CalculatorController:
    """
    The Controller in the MVC pattern for the calculator.
    It acts as an intermediary between the Model and the View.
    It receives input events from the View and translates them into actions for the Model.
    It also ensures the View is updated when the Model changes (via the Observer pattern).
    """

    def __init__(self, model: CalculatorModel, view: CalculatorView):
        """
        Initializes the CalculatorController.
        :param model: An instance of CalculatorModel.
        :param view: An instance of CalculatorView.
        """
        self._model = model
        self._view = view # View is observed by the model, but controller holds ref for delegation

    def handle_digit_input(self, digit: str):
        """
        Handles a digit or decimal point input from the user (via the View).
        Instructs the model to process this input.
        :param digit: The digit ('0'-'9') or decimal point ('.') string.
        """
        self._model.input_digit(digit)

    def handle_operator_input(self, operator: str):
        """
        Handles an operator input from the user (via the View).
        Instructs the model to set the pending operator.
        :param operator: The operator string ('+', '-', '*', '/').
        """
        self._model.set_operator(operator)

    def handle_equals(self):
        """
        Handles the equals button press from the user (via the View).
        Instructs the model to calculate the result.
        """
        self._model.calculate_result()

    def handle_clear(self):
        """
        Handles the clear button press from the user (via the View).
        Instructs the model to clear its state.
        """
        self._model.clear_all()
