global_x = 0


# callee func has no side effects but caller does
def foo1():
    global global_x
    global_x = 1
    bar1()


def bar1():
    return


# callee write global var
def foo2():
    bar2()


def bar2():
    global global_x
    global_x = 1


def main():
    foo1()
    foo2()

main()
