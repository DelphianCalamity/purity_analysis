import sys

from purity_analysis import Tracer

tracer = Tracer(['Person'])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)


class Person:
    def __init__(self):
        self.name = None


# callee has no side effects
def foo1():
    bar1()


def bar1():
    return


# callee mutate caller's arg
def foo2():
    person1 = Person()
    bar2(person1)


def bar2(person2):
    person2.name = 'anna'


def main():
    foo1()
    foo2()


main()

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
