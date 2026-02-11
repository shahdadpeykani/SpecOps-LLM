import unittest
from unittest.mock import Mock
from src.model.calculator_model import CalculatorModel

class TestCalculatorModel(unittest.TestCase):

    def setUp(self):
        """Set up a new CalculatorModel and a mock observer before each test."""
        self.model = CalculatorModel()
        self.mock_observer = Mock()
        self.model.add_observer(self.mock_observer)

    def tearDown(self):
        """Clean up observer after each test."""
        self.model.remove_observer(self.mock_observer)

    def test_initial_state(self):
        self.assertEqual(self.model.get_display_value(), "0")
        self.mock_observer.update.assert_not_called()

    def test_input_single_digit(self):
        self.model.input_digit("5")
        self.assertEqual(self.model.get_display_value(), "5")
        self.mock_observer.update.assert_called_once_with("5")
        self.mock_observer.reset_mock()

        self.model.input_digit("0") # Should replace 5 with 0 if it was new input
        # Wait, if new_input is false, it should append
        # Let's check the state first
        self.model.input_digit("1")
        self.assertEqual(self.model.get_display_value(), "1")
        self.model.input_digit("0")
        self.assertEqual(self.model.get_display_value(), "10")
        self.mock_observer.update.assert_called_with("10")

    def test_input_multiple_digits(self):
        self.model.input_digit("1")
        self.model.input_digit("2")
        self.model.input_digit("3")
        self.assertEqual(self.model.get_display_value(), "123")
        self.mock_observer.update.assert_called_with("123")

    def test_input_decimal(self):
        self.model.input_digit("1")
        self.model.input_digit(".")
        self.model.input_digit("2")
        self.assertEqual(self.model.get_display_value(), "1.2")

        # Ensure only one decimal point can be entered
        self.model.input_digit(".")
        self.assertEqual(self.model.get_display_value(), "1.2")

    def test_input_decimal_starts_with_dot(self):
        self.model.input_digit(".")
        self.assertEqual(self.model.get_display_value(), "0.")
        self.model.input_digit("5")
        self.assertEqual(self.model.get_display_value(), "0.5")

    def test_addition(self):
        self.model.input_digit("1")
        self.model.set_operator("+")
        self.mock_observer.reset_mock() # Operator setting also notifies
        self.model.input_digit("2")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "3")
        self.mock_observer.update.assert_called_with("3")

    def test_subtraction(self):
        self.model.input_digit("5")
        self.model.set_operator("-")
        self.mock_observer.reset_mock()
        self.model.input_digit("3")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "2")
        self.mock_observer.update.assert_called_with("2")

    def test_multiplication(self):
        self.model.input_digit("4")
        self.model.set_operator("*")
        self.mock_observer.reset_mock()
        self.model.input_digit("6")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "24")
        self.mock_observer.update.assert_called_with("24")

    def test_division(self):
        self.model.input_digit("10")
        self.model.set_operator("/")
        self.mock_observer.reset_mock()
        self.model.input_digit("2")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "5")
        self.mock_observer.update.assert_called_with("5")

    def test_division_by_zero(self):
        self.model.input_digit("10")
        self.model.set_operator("/")
        self.mock_observer.reset_mock()
        self.model.input_digit("0")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "Error")
        self.mock_observer.update.assert_called_with("Error")

        # Ensure subsequent operations are blocked
        self.model.input_digit("5")
        self.assertEqual(self.model.get_display_value(), "Error")
        self.mock_observer.update.assert_called_once_with("Error") # Still the same error update

        # Ensure C clears error
        self.model.clear_all()
        self.assertEqual(self.model.get_display_value(), "0")
        self.mock_observer.update.assert_called_with("0")


    def test_clear_all(self):
        self.model.input_digit("123")
        self.model.set_operator("+")
        self.model.input_digit("45")
        self.model.clear_all()
        self.assertEqual(self.model.get_display_value(), "0")
        # It should notify twice for clear_all (once to show current input state, once for final clear state)
        # The important thing is that the final state is '0'
        self.mock_observer.update.assert_called_with("0")

    def test_chain_operations(self):
        self.model.input_digit("10")
        self.model.set_operator("+")
        self.model.input_digit("5")
        self.model.set_operator("-") # Should calculate 10+5 = 15
        self.assertEqual(self.model.get_display_value(), "15")
        self.mock_observer.update.assert_called_with("15") # After 10+5 calculation
        self.mock_observer.reset_mock()

        self.model.input_digit("2")
        self.model.set_operator("*") # Should calculate 15-2 = 13
        self.assertEqual(self.model.get_display_value(), "13")
        self.mock_observer.update.assert_called_with("13") # After 15-2 calculation
        self.mock_observer.reset_mock()

        self.model.input_digit("3")
        self.model.calculate_result() # Should calculate 13*3 = 39
        self.assertEqual(self.model.get_display_value(), "39")
        self.mock_observer.update.assert_called_with("39")

    def test_precision_whole_number(self):
        self.model.input_digit("10")
        self.model.set_operator("/")
        self.model.input_digit("5")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "2")

    def test_precision_decimal_number(self):
        self.model.input_digit("10")
        self.model.set_operator("/")
        self.model.input_digit("3")
        self.model.calculate_result()
        self.assertIn(self.model.get_display_value(), ["3.33333333", "3.3333333"]) # Depending on how many 0s are stripped

        self.model.clear_all()
        self.model.input_digit("0.1")
        self.model.set_operator("+")
        self.model.input_digit("0.2")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "0.3")

    def test_repeated_equals(self):
        self.model.input_digit("5")
        self.model.set_operator("+")
        self.model.input_digit("2")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "7")
        self.model.calculate_result() # No effect without new operand/operator
        self.assertEqual(self.model.get_display_value(), "7")
        self.model.calculate_result() # Still no effect
        self.assertEqual(self.model.get_display_value(), "7")

        self.model.clear_all()
        self.model.input_digit("5")
        self.model.calculate_result() # should just display 5, no operation performed
        self.assertEqual(self.model.get_display_value(), "5")

    def test_operator_change(self):
        self.model.input_digit("10")
        self.model.set_operator("+")
        self.assertEqual(self.model._operator, "+")
        self.model.set_operator("-") # Change operator before second operand
        self.assertEqual(self.model._operator, "-")
        self.model.input_digit("5")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "5") # 10 - 5 = 5

    def test_operator_after_result(self):
        self.model.input_digit("10")
        self.model.set_operator("+")
        self.model.input_digit("2")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "12")
        self.mock_observer.reset_mock()

        self.model.set_operator("*") # Use 12 as first operand for new operation
        self.model.input_digit("3")
        self.model.calculate_result()
        self.assertEqual(self.model.get_display_value(), "36")
        self.mock_observer.update.assert_called_with("36")

if __name__ == '__main__':
    unittest.main()
