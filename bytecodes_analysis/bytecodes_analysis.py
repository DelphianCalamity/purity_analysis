import argparse
import json
import os


def to_package(name):
    return 'tests.' + name


def to_path(name):
    return 'tests/' + name + ".py"


class BytecodesAnalysis:

    def __init__(self, name):
        self.name = name
        self.source_path = to_path(self.name)
        self.old_code = None
        self.backup = None

    def inject_tracing_code(self, ignore):
        with open(self.source_path) as fp:
            self.old_code = fp.read()
            new_code = f"""\
import sys
from bytecodes_analysis.tracer import Tracer
tracer = Tracer({ignore})
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)

{self.old_code}

sys.settrace(None) 
sys.setprofile(None)
tracer.log_annotations(__file__)
"""
        self.backup = self.source_path + ".backup"
        os.rename(self.source_path, self.backup)

        with open(self.source_path, 'w') as w:
            w.write(new_code)

    def execute(self):
        os.system("python3 -m " + to_package(self.name))

    def finalize(self):
        os.rename(self.backup, self.source_path)


def analyze(source_input, ignore=None):
    ignore = [] if ignore is None else ignore
    app = BytecodesAnalysis(source_input)
    app.inject_tracing_code(ignore)
    app.execute()
    with open(app.source_path + ".annotations") as json_file:
        annotations = json.load(json_file)
    app.finalize()

    return annotations


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help='Input file', required=True)
    args = parser.parse_args()
    analyze(args.input)
