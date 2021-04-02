import sys

from purity_analysis import Tracer

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)

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

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
