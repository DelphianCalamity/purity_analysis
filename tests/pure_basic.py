global_x = 0


# read param
def foo1(x):
    y = x


# reassign param
def foo2(x):
    x = 1


# read global var
def foo3():
    y = global_x


# name local var same as global var
def foo4():
    global_x = 1


def main():
    foo1(0)
    foo2(0)
    foo3()
    foo4()
