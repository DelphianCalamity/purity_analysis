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
