def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b


class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.history = []

    def calculate(self, operation: str, a: int, b: int) -> int:
        """Perform a calculation and store in history."""
        if operation == "add":
            result = add_numbers(a, b)
        elif operation == "multiply":
            result = multiply_numbers(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        self.history.append(f"{operation}({a}, {b}) = {result}")
        return result
