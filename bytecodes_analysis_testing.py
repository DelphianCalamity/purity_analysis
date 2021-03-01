import unittest
from bytecodes_analysis import analyze


# how do we know if foo is defined in g?
# how we do determine if nonlocal var is in parent func or outside?
class TestBytecodesAnalysis(unittest.TestCase):
    def test_pure_basic(self):
        source = """
def foo(x, y):
    z = x + y
    x = 3

x = 1
y = 4
foo(x, y)
"""
        received_out = analyze(source)
        expected_out = {'foo': {'pure': 1, 'mutated_objects': []}}
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
            'foo': {'pure': 1, 'mutated_objects': []},
            'bar': {'pure': 1, 'mutated_objects': []}
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
            'foo': {'pure': 1, 'mutated_objects': []},
            'bar': {'pure': 1, 'mutated_objects': []}
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
            'foo': {'pure': 1, 'mutated_objects': []},
            'bar': {'pure': 1, 'mutated_objects': []}
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_closure(self):
        # closure writes global vars
        source = """
def foo():
    def bar():  
        nonlocal x, y
        x = y = 1 

    bar()

x = y = 0
foo()
"""
        received_out = analyze(source)
        expected_out = {
            'foo': {'pure': 1, 'mutated_objects': []},
            'bar': {'pure': 1, 'mutated_objects': []}
        }
        self.assertEqual(received_out, expected_out)


if __name__ == '__main__':
    unittest.main()
