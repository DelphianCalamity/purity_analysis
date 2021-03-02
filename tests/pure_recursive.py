# all iterations no side effects
def foo(n):
    if n <= 0:
        return
    else:
        foo(n - 1)


def main():
    foo(5)
