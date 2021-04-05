if __name__ == '__main__':
    from purity_analysis import Tracer
    import sys
    from runpy import _run_module_as_main

    # Run the module specified as the next command line argument
    if len(sys.argv) < 2:
        print("No module specified for execution", file=sys.stderr)
    else:
        del sys.argv[0]  # Make the requested module sys.argv[0]

        tracer = Tracer()
        sys.settrace(tracer.trace_calls)
        sys.setprofile(tracer.trace_c_calls)

        _run_module_as_main(sys.argv[0])

        sys.setprofile(None)
        sys.settrace(None)
        tracer.log_annotations(__file__)
