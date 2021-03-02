import unittest
from bytecodes_analysis import analyze


class TestBytecodesAnalysis(unittest.TestCase):
    def test_pure_basic(self):
        # read param
        source = """
def foo(x):
    y = x

foo(1)
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # reassign param
        source = """
def foo(x):
    x = 1

foo(0)
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # read global var
        source = """
def foo():
    y = x

x = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # name local var same as global var
        source = """
def foo():
    x = 1

x = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_basic(self):
        # write global var
        source = """
def foo():
    global x
    x = 1

x = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'x'}},
        }
        self.assertEqual(received_out, expected_out)

        # write global var on first call
        source = """
def foo(n):
    if n is True:
        global x
        x = 1

x = 0
foo(True)
foo(False)
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'x'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_obj(self):
        # read obj prop
        source = """
class Person:
    def __init__(self):
        self.name = None

def foo(person):
    x = person.name

foo(Person())
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # call non-mutating obj method
        source = """
class Person:
    def __init__(self):
        self.name = None

    def get_name(self):
        return self.name

def foo(person):
    x = person.get_name()

foo(Person())
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # read list content
        source = """
def foo(nums):
    x = nums[0]

foo([1, 2, 3])
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_obj(self):
        # mutate obj prop directly
        source = """
class Person:
    def __init__(self):
        self.name = None

def foo(person):
    person.name = 'anna'

foo(Person())
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'person'}},
        }
        self.assertEqual(received_out, expected_out)

        # mutate obj prop indirectly
        source = """
class Person:
    def __init__(self):
        self.name = None

    def set_name(self, name):
        self.name = name

def foo(person):
    person.set_name('anna')

foo(Person())
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'person'}},
        }
        self.assertEqual(received_out, expected_out)

        # mutate list content
        source = """
def foo(nums):
    nums[0] = 0

foo([1, 2, 3])
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'nums'}},
        }
        self.assertEqual(received_out, expected_out)

        # mutate list size
        source = """
def foo(nums):
    nums.append(0)

foo([1, 2, 3])
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'nums'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_call(self):
        # callee has no side effects
        source = """
def foo():
    bar()
        
def bar():
    return

foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
            'bar': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # callee mutate caller's arg
        source = """
class Person:
    def __init__(self):
        self.name = None
        
def foo():
    person1 = Person()
    bar(person1)

def bar(person2):
    person2.name = 'anna'

foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
            'bar': {'pure': False, 'mutated_objects': {'person2'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_call(self):
        # callee func has no side effects but caller does
        source = """
def foo():
    global x
    x = 1
    bar()

def bar():
    return

x = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'x'}},
            'bar': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # callee write global var
        source = """
def foo():
    bar()

def bar():
    global x
    x = 1

x = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'x'}},
            'bar': {'pure': False, 'mutated_objects': {'x'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_recursive_call(self):
        # all iterations no side effects
        source = """
def foo(n):
    if n <= 0:
        return
    else:
        foo(n - 1)

foo(5)
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_recursive_call(self):
        # base case has side effect
        source = """
def foo(n):
    if n <= 0:
        global x
        x = 1
    else:
        foo(n - 1)

x = 0
foo(5)
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'x'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_closure(self):
        # closure reads global vars
        source = """
def foo():
    def bar():  
        z = x + y  

    bar()

x = y = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
            'bar': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # closure reads parent's local vars
        source = """
def foo():
    def bar():  
        z = x + y  
        
    x = y = 0
    bar()
        
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
            'bar': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

        # closure writes parent's local vars
        source = """
def foo():
    def bar():  
        nonlocal x, y
        x = y = 1 

    x = y = 0
    bar()

foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
            'bar': {'pure': False, 'mutated_objects': {'x', 'y'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_closure(self):
        # closure write global var
        source = """
def foo():
    def bar():  
        global x, y
        x = y = 1 

    bar()

x = y = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'x', 'y'}},
            'bar': {'pure': False, 'mutated_objects': {'x', 'y'}},
        }
        self.assertEqual(received_out, expected_out)


if __name__ == '__main__':
    unittest.main()
