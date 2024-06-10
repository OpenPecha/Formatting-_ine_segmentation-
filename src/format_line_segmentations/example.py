def add(a, b):
    result = a + b
    return result

def subtract(a, b):
    result = a - b
    return result

def process_numbers(numbers):
    for i, number in enumerate(numbers):
        sum_result = add(i, number)
        diff_result = subtract(i, number)
        print(f"Processing index {i} with number {number}: sum is {sum_result}, difference is {diff_result}")

numbers = [10, 20, 30, 40, 50]
process_numbers(numbers)
