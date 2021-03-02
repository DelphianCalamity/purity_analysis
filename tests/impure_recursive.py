global_x = 0


# base case has side effect
def foo(n):
    if n <= 0:
        global global_x
        global_x = 1
    else:
        foo(n - 1)


def main():
    foo(5)
