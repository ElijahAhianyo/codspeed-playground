import time
def first_func():
    time.sleep(5)
    return second_func()

def second_func():
    time.sleep(3)
    return third_func()

def third_func():
    time.sleep(2)