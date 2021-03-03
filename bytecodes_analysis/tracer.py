import dis
import json
import pprint as pp
from itertools import islice

from bytecodes_analysis.utils import EventType, FunctionInfo, print_frame


class Tracer:

    def __init__(self, ignore=None):
        self.functions_visited = {}
        self.ignore = [] if ignore is None else ignore

    def generic_tracing(self, frame, event, arg):
        print("Event:", event, "function: ", frame.f_code.co_name, "arg:", arg)

    def trace_bytecodes(self, frame, event, arg):

        if event != "opcode":
            return

        print("Event:", event, "function: ", frame.f_code.co_name, "arg:", arg)
        instructions = dis.get_instructions(frame.f_code)
        i = next(islice(instructions, int(frame.f_lasti / 2), None))
        print(i)

        opname = i.opname
        var = i.argval

        if opname in {'STORE_DEREF', 'STORE_GLOBAL', 'STORE_NAME'}:
            # Trace var all the way back to the initial frame; stop when it is found in a frame's locals
            caller = frame
            while caller is not None:
                print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                if var in caller.f_locals:
                    break
                else:
                    self.functions_visited[caller.f_code.co_name].pure = False
                    self.functions_visited[caller.f_code.co_name].mutates(var)
                print(caller)
                print(frame.f_back)
                if caller == frame.f_back:
                    return
                caller = frame.f_back

        # elif opname == "STORE_ATTR":

    def trace_calls(self, frame, event, arg):
        co = frame.f_code
        func_name = co.co_name
        frame.f_trace_opcodes = True

        # if func_name in self.ignore: #+[FuncType.CONSTRUCTOR]:
        #     return

        if event == EventType.CALL:
            print_frame(frame, event, arg)
            ########################################################################################################
            if func_name not in self.functions_visited:
                self.functions_visited[func_name] = FunctionInfo()
            return self.trace_bytecodes

        # elif event == EventType.C_CALL:
        #     print("Frame: ", frame, "line-number", frame.f_lineno, "last-line", frame.f_lasti)
        #     print("Event: ", event)
        #     print("Arg: ", arg)
        #     # print(dis.disco(frame.f_code, lasti=frame.f_lasti))
        #     # print("bytecode: ", frame.f_code.co_code[frame.f_lasti + 1])
        #     # print(dis.opname[frame.f_code.co_code[frame.f_lasti]])
        #     print("\n\n\n")


    def log_annotations(self, filename):
        output = {}
        for func_name in self.functions_visited:
            output[func_name] = {
                "pure": self.functions_visited[func_name].pure,
                "mutated_objects": sorted(list(self.functions_visited[func_name].mutated_objects))
            }
        with open(filename + ".annotations", 'w') as w:
            r = json.dumps(output)
            w.write(r)
        pp.pprint(output)
        return output
