import unittest
from bytecodes_analysis import analyze


class TestBytecodesAnalysis(unittest.TestCase):
    def test_pure_basic(self):
        file_path = 'pure_basic'
        received_out = analyze(file_path)
        expected_out = {
            'foo1': {'pure': True, 'mutated_objects': set()},
            'foo2': {'pure': True, 'mutated_objects': set()},
            'foo3': {'pure': True, 'mutated_objects': set()},
            'foo4': {'pure': True, 'mutated_objects': set()},
            'main': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_basic(self):
        file_path = 'impure_basic'
        received_out = analyze(file_path)
        expected_out = {
            'foo1': {'pure': False, 'mutated_objects': {'global_x'}},
            'foo2': {'pure': False, 'mutated_objects': {'global_x'}},
            'main': {'pure': False, 'mutated_objects': {'global_x'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_obj(self):
        file_path = 'pure_obj'
        received_out = analyze(file_path)
        expected_out = {
            'foo1': {'pure': True, 'mutated_objects': set()},
            'foo2': {'pure': True, 'mutated_objects': set()},
            'foo3': {'pure': True, 'mutated_objects': set()},
            'main': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_obj(self):
        file_path = 'impure_obj'
        received_out = analyze(file_path)
        expected_out = {
            'foo1': {'pure': False, 'mutated_objects': {'person'}},
            'foo2': {'pure': False, 'mutated_objects': {'person'}},
            'foo3': {'pure': False, 'mutated_objects': {'nums'}},
            'foo4': {'pure': False, 'mutated_objects': {'nums'}},
            'main': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_call(self):
        file_path = 'pure_call'
        received_out = analyze(file_path)
        expected_out = {
            'foo1': {'pure': True, 'mutated_objects': set()},
            'bar1': {'pure': True, 'mutated_objects': set()},
            'foo2': {'pure': True, 'mutated_objects': set()},
            'bar2': {'pure': False, 'mutated_objects': {'person2'}},
            'main': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_call(self):
        file_path = 'impure_call'
        received_out = analyze(file_path)
        expected_out = {
            'foo1': {'pure': False, 'mutated_objects': {'global_x'}},
            'bar1': {'pure': True, 'mutated_objects': set()},
            'foo2': {'pure': False, 'mutated_objects': {'global_x'}},
            'bar2': {'pure': False, 'mutated_objects': {'global_x'}},
            'main': {'pure': False, 'mutated_objects': {'global_x'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_recursive_call(self):
        file_path = 'pure_recursive'
        received_out = analyze(file_path)
        expected_out = {
            'foo': {'pure': True, 'mutated_objects': set()},
            'main': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_recursive_call(self):
        file_path = 'impure_recursive'
        received_out = analyze(file_path)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'global_x'}},
            'main': {'pure': False, 'mutated_objects': {'global_x'}},
        }
        self.assertEqual(received_out, expected_out)

    def test_pure_closure(self):
        file_path = 'pure_closure'
        received_out = analyze(file_path)
        expected_out = {
            'foo1': {'pure': True, 'mutated_objects': set()},
            'bar1': {'pure': True, 'mutated_objects': set()},
            'foo2': {'pure': True, 'mutated_objects': set()},
            'bar2': {'pure': True, 'mutated_objects': set()},
            'foo3': {'pure': True, 'mutated_objects': set()},
            'bar3': {'pure': False, 'mutated_objects': {'nonlocal_x', 'nonlocal_y'}},
            'main': {'pure': True, 'mutated_objects': set()},
        }
        self.assertEqual(received_out, expected_out)

    def test_impure_closure(self):
        file_path = 'impure_closure'
        received_out = analyze(file_path)
        expected_out = {
            'foo': {'pure': False, 'mutated_objects': {'global_x', 'global_y'}},
            'bar': {'pure': False, 'mutated_objects': {'global_x', 'global_y'}},
            'main': {'pure': False, 'mutated_objects': {'global_x', 'global_y'}},
        }
        self.assertEqual(received_out, expected_out)


if __name__ == '__main__':
    unittest.main()
