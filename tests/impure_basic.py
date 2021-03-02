global_x = 0


# write global var
def foo1():
    global global_x
    global_x = 1


# write global var on first call
def foo2(n):
    if n is True:
        global global_x
        global_x = 1


def main():
    foo1()
    foo2(True)
    foo2(False)
