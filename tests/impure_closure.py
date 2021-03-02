global_x = global_y = 0


# closure write global var
def foo():
    def bar():
        global global_x, global_y
        global_x = global_y = 1

    bar()


def main():
    foo()

main()
