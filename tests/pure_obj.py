class Person:
    def __init__(self):
        self.name = None

    # def get_name(self):
    #     return self.name

    def set_name(self, s):
        self.name = s


#
#
# #
# # # read obj prop
# # def foo1(person):
# #     x = person.name
# #
# #
# # # call non-mutating obj method
# # def foo2(person):
# #     x = person.get_name()
# #
# #
# # # read list content
# # def foo3(nums):
# #     x = nums[0]
#

def main():
    person = Person()
    person.name = "Boo"
    person.set_name("hello")
    # print(locals())
    # foo1(Person())
    # foo2(Person())
    # foo3([1, 2, 3])

main()
