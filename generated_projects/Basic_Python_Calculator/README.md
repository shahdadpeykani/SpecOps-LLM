# Basic Python Calculator

## Introduction

The **Basic Python Calculator** is a robust and user-friendly standalone application developed entirely in Python. Designed for simplicity and efficiency, it provides core arithmetic functionalities (addition, subtraction, multiplication, and division) within an intuitive dark mode user interface. This project emphasizes reliability by incorporating comprehensive error handling to gracefully manage invalid inputs and operations, ensuring a smooth and predictable user experience.

## Installation

To get started with the Basic Python Calculator, follow these steps:

1.  **Prerequisites:**
    Ensure you have Python 3.x installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2.  **Clone the Repository:**
    Open your terminal or command prompt and clone the project repository using Git:

    ```bash
    git clone https://github.com/your-username/basic-python-calculator.git
    cd basic-python-calculator
    ```
    *(Note: Replace `https://github.com/your-username/basic-python-calculator.git` with the actual repository URL.)*

3.  **Create a Virtual Environment (Recommended):**
    It's good practice to work within a virtual environment to manage dependencies.

    ```bash
    python -m venv venv
    ```

4.  **Activate the Virtual Environment:**

    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

5.  **Install Dependencies (if any):**
    If the project uses any external libraries (e.g., for GUI frameworks like Tkinter if it's not purely standard library), install them using pip:

    ```bash
    pip install -r requirements.txt
    ```
    *(Note: For a basic Python calculator using only standard libraries, `requirements.txt` might not be present or necessary.)*

## Usage

Once installed, you can run the calculator application:

1.  **Activate your virtual environment** (if you created one):
    ```bash
    source venv/bin/activate # macOS/Linux
    .\venv\Scripts\activate # Windows
    ```

2.  **Run the main script:**
    ```bash
    python main.py
    ```
    *(Assuming `main.py` is the entry point for the calculator application.)*

Upon launching, the calculator will present its dark mode user interface. You can input numbers and select arithmetic operations using the provided buttons or keyboard inputs. The display will show the current input and the result of operations. The application is designed to handle common errors, such as division by zero or invalid input formats, displaying appropriate error messages to guide the user.

**Example Workflow:**

1.  Enter the first number (e.g., `10`).
2.  Click an operation button (e.g., `+`).
3.  Enter the second number (e.g., `5`).
4.  Click the equals button (`=`).
5.  The result (`15`) will be displayed.

## Testing

The project includes unit tests to ensure the correctness of arithmetic operations and robust error handling. To run these tests:

1.  **Activate your virtual environment** (if you created one).

2.  **Install `pytest`** (if not already in `requirements.txt`):
    ```bash
    pip install pytest
    ```

3.  **Execute the tests:**
    Navigate to the project's root directory in your terminal and run:
    ```bash
    pytest
    ```
    This command will discover and run all test cases, providing a report on their pass/fail status.