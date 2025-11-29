# python - Flashcards
Generated on 2025-11-25 19:57

Q1: What is a Python decorator?
A1: A function that takes another function as an argument, adds functionality, and returns the modified function.

Q2: Explain the difference between `==` and `is` in Python.
A2: `==` compares the values of two objects, while `is` checks if two variables point to the same object in memory.

Q3: What is the purpose of the `__init__` method in a Python class?
A3: It is the constructor method called when an object is created from the class; it initializes the object's attributes.

Q4: How does Python handle multiple inheritance?
A4: Python uses C3 linearization (also known as the MRO - Method Resolution Order) to determine the order in which base classes are searched for a method.

Q5: What is the Global Interpreter Lock (GIL) and its impact?
A5: The GIL is a mutex that allows only one thread to hold control of the Python interpreter at any one time. It limits true parallelism in CPU-bound tasks.

Q6: Explain the purpose of the `try...except` block in Python.
A6: It's used for exception handling; code within the `try` block is executed, and if an exception occurs, the code within the `except` block corresponding to the exception type is executed.

Q7: What are generators in Python and how are they different from lists?
A7: Generators are iterators created using functions and the `yield` keyword. They produce values on demand and use less memory than lists by not storing all elements at once.

Q8: Describe the difference between shallow copy and deep copy in Python.
A8: A shallow copy creates a new object but references the same nested objects. A deep copy creates a new object and recursively copies all nested objects, making independent copies.
