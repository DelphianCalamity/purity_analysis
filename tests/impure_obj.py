class Person:
    def __init__(self):
        self.name = None

    def set_name(self, name):
        self.name = name


# mutate obj prop directly
def foo1(person):
    person.name = 'anna'


# mutate obj prop indirectly
def foo2(person):
    person.set_name('anna')


# mutate list content
def foo3(nums):
    nums[0] = 0


# mutate list size
def foo4(nums):
    nums.append(0)


def main():
    foo1(Person())
    foo2(Person())
    foo3([1, 2, 3])
    foo4([1, 2, 3])

main()
