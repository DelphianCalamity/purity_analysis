import sys

from purity_analysis import Tracer
tracer = Tracer(['Person'])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)


class Person:
    def __init__(self):
        self.name = None

    def get_name(self):
        return self.name


# read obj prop
def foo1(person):
    x = person.name


# call non-mutating obj method
def foo2(person):
    x = person.get_name()


# read list content
def foo3(nums):
    x = nums[0]


def main():
    foo1(Person())
    foo2(Person())
    foo3([1, 2, 3])


main()

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
