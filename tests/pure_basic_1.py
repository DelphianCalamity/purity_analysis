TRACE = True
CTRACE = False

if TRACE:
    import sys
    from tracer import Tracer

    tracer = Tracer([])
    sys.settrace(tracer.trace_calls)
    sys.setprofile(tracer.trace_c_calls)

if CTRACE:
    import ctracer

    ctracer.start()

# read param
def foo1(x):
    y = x
    print(y)


def main():
    foo1(4242)

main()

if TRACE:
    sys.settrace(None)
    sys.setprofile(None)
    tracer.log_annotations(__file__)

if CTRACE:
    ctracer.stop()


