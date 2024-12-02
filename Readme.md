# Memory Usage Logger

This Python program provides a decorator `memory_logger` that can be used to log the memory usage of a function on a per-line basis. It tracks both CPU and GPU memory usage (if available) and outputs the memory consumption for each line of code executed within the decorated function.

## Features

- Logs CPU memory usage per line of code
- Logs GPU memory usage per line of code (if available)
- Tracks memory usage differences between consecutive lines
- Outputs memory usage information for each line of code executed

## Requirements

- Python 3.x
- `psutil` library for CPU memory monitoring
- `pynvml` library for GPU memory monitoring (optional)

## Installation

1. Clone the repository or download the source code.

2. Install the required dependencies:
   ```
   pip install psutil pynvml
   ```

## Usage

1. Import the `memory_logger` decorator in your Python script:
   ```python
   from memory_logger import memory_logger
   ```

2. Decorate the function you want to monitor with `@memory_logger`:
   ```python
   @memory_logger
   def your_function():
       # Your function code here
   ```

3. Run your Python script. The memory usage information will be logged and displayed in the console output.

## Example

```python
@memory_logger
def example_function():
    a = [1, 2, 3]
    b = [4, 5, 6]
    c = a + b
    return c

example_function()
```

Output:
```
Function 'example_function' memory usage per line:
Line 2: CPU 15.23 MB (+0.01 MB), GPU 2.45 MB (+0.00 MB) | a = [1, 2, 3]
Line 3: CPU 15.24 MB (+0.01 MB), GPU 2.45 MB (+0.00 MB) | b = [4, 5, 6]
Line 4: CPU 15.25 MB (+0.01 MB), GPU 2.45 MB (+0.00 MB) | c = a + b
Line 5: CPU 15.25 MB (+0.00 MB), GPU 2.45 MB (+0.00 MB) | return c
```