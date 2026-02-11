import unittest
from unittest.mock import Mock, call
from src.controller.calculator_controller import CalculatorController
from src.model.calculator_model import CalculatorModel # For type hinting and constructor
from src.view.calculator_view import CalculatorView # For type hinting and constructor

class TestCalculatorController(unittest.TestCase):

    def setUp(self):
        """Set up mock model and view, and a new controller before each test."""
        self.mock_model = Mock(spec=CalculatorModel)
        self.mock_view = Mock(spec=CalculatorView)
        self.controller = CalculatorController(self.mock_model, self.mock_view)

    def test_handle_digit_input(self):
        self.controller.handle_digit_input("7")
        self.mock_model.input_digit.assert_called_once_with("7")

    def test_handle_operator_input(self):
        self.controller.handle_operator_input("+")
        self.mock_model.set_operator.assert_called_once_with("+")

    def test_handle_equals(self):
        self.controller.handle_equals()
        self.mock_model.calculate_result.assert_called_once()

    def test_handle_clear(self):
        self.controller.handle_clear()
        self.mock_model.clear_all.assert_called_once()

    # Test that controller doesn't directly update view, model does via observer
    def test_controller_does_not_directly_update_view(self):
        self.controller.handle_digit_input("1")
        self.mock_model.input_digit.assert_called_once_with("1")
        # The view's update_display method should NOT be called by the controller
        # but rather by the model via the observer pattern.
        self.mock_view.update_display.assert_not_called()

        # Verify the model *would* call notify_observers
        self.mock_model.input_digit.reset_mock()
        # When handle_digit_input is called, model.input_digit is called.
        # model.input_digit internally calls notify_observers.
        # Our mock_model is a plain mock, so it won't actually call notify_observers.
        # This test ensures the controller itself doesn't call view.update_display.
        self.controller.handle_digit_input("2")
        self.mock_view.update_display.assert_not_called()

if __name__ == '__main__':
    unittest.main()
