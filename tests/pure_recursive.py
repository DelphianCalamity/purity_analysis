import sys

from purity_analysis import Tracer

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)


# all iterations no side effects
def foo(n):
    if n <= 0:
        return
    else:
        foo(n - 1)


def main():
    foo(5)


main()

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
