from src.common.observer import Subject

class CalculatorModel(Subject):
    """
    The Model in the MVC pattern for the calculator.
    It manages the calculator's state and performs all arithmetic operations.
    It notifies its observers (the View) when its state changes.
    """
    def __init__(self):
        super().__init__()
        self._current_input = "0"  # The number currently being entered or displayed
        self._stored_value = 0.0   # The first operand in an operation
        self._operator = None      # The pending operation (+, -, *, /)
        self._new_input = True     # True if the next digit pressed starts a new number
        self._last_result = None   # Stores the last calculated result

    def _reset_state(self):
        """
        Resets the calculator to its initial state.
        """
        self._current_input = "0"
        self._stored_value = 0.0
        self._operator = None
        self._new_input = True
        self._last_result = None

    def input_digit(self, digit: str):
        """
        Appends a digit to the current input string or starts a new input.
        Handles decimal points and prevents multiple leading zeros or multiple decimal points.
        :param digit: The digit (0-9) or decimal point (".") to input.
        """
        if self._current_input == "Error": # Clear error state on new input
            self._current_input = "0"
            self._new_input = True

        if self._new_input:
            if digit == ".":
                self._current_input = "0."
            else:
                self._current_input = digit
            self._new_input = False
        elif digit == ".":
            if "." not in self._current_input:
                self._current_input += digit
        elif self._current_input == "0" and digit == "0":
            pass # Do nothing, avoid "00"
        elif self._current_input == "0":
            self._current_input = digit # Replace single '0' with new digit
        else:
            self._current_input += digit

        self.notify_observers(self.get_display_value())

    def set_operator(self, op: str):
        """
        Sets the pending arithmetic operator.
        If an operator is already pending, it calculates the intermediate result.
        :param op: The operator string (+, -, *, /).
        """
        if self._current_input == "Error":
            return # Do not set operator if in error state

        if not self._new_input and self._operator:
            # If there's a stored operator and new input has been made, calculate intermediate result
            self.calculate_result() # This will update _current_input and notify observers

        self._stored_value = float(self._current_input)
        self._operator = op
        self._new_input = True # Next digit will start a new number
        self.notify_observers(self.get_display_value()) # Update view to show current value/operator implied

    def calculate_result(self):
        """
        Performs the pending arithmetic operation using the stored value and current input.
        Handles division by zero errors.
        """
        if self._current_input == "Error":
            return # Do not calculate if in error state

        if self._operator is None:
            # If no operator, just update display to current input and reset for new operation
            self._stored_value = float(self._current_input)
            self._last_result = float(self._current_input)
            self._new_input = True
            self.notify_observers(self.get_display_value())
            return

        try:
            second_operand = float(self._current_input)
            result = 0.0
            if self._operator == '+':
                result = self._stored_value + second_operand
            elif self._operator == '-':
                result = self._stored_value - second_operand
            elif self._operator == '*':
                result = self._stored_value * second_operand
            elif self._operator == '/':
                if second_operand == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                result = self._stored_value / second_operand
            
            # Basic precision: round to a reasonable number of decimal places
            # or convert to int if it's a whole number
            if result == int(result):
                self._current_input = str(int(result))
            else:
                self._current_input = f"{result:.8f}".rstrip('0').rstrip('.')

            self._last_result = result
            self._stored_value = result
            self._operator = None
            self._new_input = True

        except ZeroDivisionError:
            self._current_input = "Error"
            self._stored_value = 0.0
            self._operator = None
            self._new_input = True
        except ValueError:
            # This shouldn't typically happen with button-based input, but good for robustness
            self._current_input = "Error"
            self._stored_value = 0.0
            self._operator = None
            self._new_input = True
        finally:
            self.notify_observers(self.get_display_value())

    def clear_all(self):
        """
        Clears all calculator state, effectively resetting it.
        """
        self._reset_state()
        self.notify_observers(self.get_display_value())

    def get_display_value(self) -> str:
        """
        Returns the string that should be displayed on the calculator screen.
        """
        return self._current_input
