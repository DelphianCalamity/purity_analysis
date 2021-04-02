import sys

from purity_analysis import Tracer

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)

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

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
