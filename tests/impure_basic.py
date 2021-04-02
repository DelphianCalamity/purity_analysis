import sys

from purity_analysis import Tracer

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)

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


main()

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
