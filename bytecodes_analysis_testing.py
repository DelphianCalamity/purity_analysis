import unittest
from bytecodes_analysis import analyze

# how do we know if foo is defined in g?
# how we do determine if nonlocal var is in parent func or outside?
class TestBytecodesAnalysis(unittest.TestCase):
    def test_pure(self):
#         source = """
# def foo(x, y):
#     z = x + y
#     x = 3
#
# x = 1
# y = 4
# foo(x, y)
# """

        source = """
def g(x, y):
    # x = ''
    z=1

    def foo():  # impure
        nonlocal x
        x = 5 + y
        z = 1    
        
    if y != 0:
        foo()
        
x=1
y=2
g(x,y)
"""
        received_out = analyze(source)
        expected_out = {'foo': {'pure': 1, 'mutated_objects': []}}
        self.assertEqual(received_out, expected_out)








if __name__ == '__main__':
    unittest.main()


