import sys

from purity_analysis import Tracer

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)

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


main()

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
