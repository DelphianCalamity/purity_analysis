# import pydron
import sys
import time

from purity_analysis import Tracer

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)


# @pydron.functional
def foo1(num):
    time.sleep(1)
    return num
    # return num + math.log(num)


# @pydron.functional
def foo2(num):
    time.sleep(1)
    return num


# @pydron.schedule
def calibration_pipeline(inputs):
    inputs[0] = 0
    outputs = []
    x = 4
    for num in inputs:
        output = foo1(num) + foo2(num)
        outputs = outputs + [output]
    return outputs


if __name__ == '__main__':
    start = time.time()
    vals = [n for n in range(5)]
    print(calibration_pipeline(vals))
    end = time.time()
    print(end - start)

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
