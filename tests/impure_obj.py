import sys

from purity_analysis import Tracer

tracer = Tracer(__file__)
sys.settrace(tracer.trace_calls)
# sys.setprofile(tracer.trace_c_calls)


# import ctracer
# ctracer.start()

class Person:
    def __init__(self):
        self.name = None

    def set_name(self, name):
        self.name = name

# mutate obj prop indirectly
def foo1(person):
    person.set_name('anna')
    return 1


class Boo:
    def __init__(self, b):
        self.a = b
        self.b = 3


outlist = [0]
y = 4


def main():
    # global y
    person = Person()
    person1 = person

    # outlist[0] = person
    # y = person
    b = Boo(person)
    p = [person, 0]
    m = {}
    m['0'] = person
    m['1'] = 1
    foo1(person) + foo1(person)


main()
# ctracer.stop()

sys.settrace(None)
# sys.setprofile(None)
# tracer.log_annotations(__file__)
tracer.store_summaries_and_mapping()
