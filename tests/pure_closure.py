global_x = global_y = 0


# closure reads global vars
def foo1():
    def bar1():
        z = global_x + global_y

    bar1()


# closure reads parent's local vars
def foo2():
    def bar2():
        z = nonlocal_x + nonlocal_y

    nonlocal_x = nonlocal_y = 0
    bar2()


# closure writes parent's local vars
def foo3():
    def bar3():
        nonlocal nonlocal_x, nonlocal_y
        nonlocal_x = nonlocal_y = 1

    nonlocal_x = nonlocal_y = 0
    bar3()


def main():
    foo1()
    foo2()
    foo3()
