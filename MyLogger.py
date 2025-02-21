import os
import sys
import logging
from functools import wraps
from pprint import pprint

class CustomLogger:
    def __init__(self, log_dir='logs', log_name='custom_logger'):

        log_file = log_name + '.log'
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        # Configure logging
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.formatter)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_to_stdout_and_file(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.logger.info(f"Executing function: {func.__name__}")
                result = func(*args, **kwargs)
                pprint(result)
                self.logger.info(f"Result: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error in function {func.__name__}: {e}")
                raise
        return wrapper

# Example usage
if __name__ == "__main__":
    custom_logger = CustomLogger()

    @custom_logger.log_to_stdout_and_file
    def example_function(x, y):
        return {'sum': x + y, 'product': x * y}

    example_function(3, 5)