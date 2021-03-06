import dis
import json
import pprint as pp
from itertools import islice

from bytecodes_analysis.utils import EventType, FuncType, FunctionInfo, print_frame

class Tracer:

    def __init__(self, ignore=None):
        self.functions_visited = {}
        self.ignore = [] if ignore is None else ignore

    def _get_instruction(self, frame, index):
        instructions = dis.get_instructions(frame.f_code)
        return next(islice(instructions, int(index / 2), None))

    def generic_tracing(self, frame, event, arg):
        print("Event:", event, "function: ", frame.f_code.co_name, "arg:", arg)

    def trace_bytecodes(self, frame, event, arg):
        if event != "opcode":
            return

        # print("Event:", event, "function: ", frame.f_code.co_name, "arg:", arg)
        i = self._get_instruction(frame, frame.f_lasti)
        print(i)
        opname = i.opname
        var = i.argval
        # print("\ncaller", frame.f_code.co_name, "\nLocals", frame.f_locals, "\nGlobals", frame.f_globals)

        if opname in {'STORE_GLOBAL', 'STORE_NAME'}:
            # Trace var all the way back to the initial frame; stop if it is found in a frame's locals
            caller = frame
            while caller is not None:
                print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                if var in caller.f_locals:
                    break
                else:
                    self.functions_visited[caller.f_code.co_name].pure = False
                    self.functions_visited[caller.f_code.co_name].mutates(var)
                # print("aa", caller.f_back, caller.f_back.f_code.co_name)
                # print(caller); print(caller.f_back)
                # if caller == frame.f_back or \
                if caller.f_back.f_code.co_name == FuncType.BASE:
                    return
                # time.sleep(2)
                caller = caller.f_back

        elif opname in {"STORE_ATTR", "STORE_SUBSCR"}:
            # Writes in the heap; declare all parent functions including this one as impure
            caller = frame
            while caller is not None:
                print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                self.functions_visited[caller.f_code.co_name].pure = False
                # self.functions_visited[caller.f_code.co_name].mutates()
                if caller.f_back.f_code.co_name == FuncType.BASE:
                    return
                caller = caller.f_back

        elif opname == 'STORE_DEREF':
            caller = frame
            while caller is not None:
                print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                if var in caller.f_code.co_cellvars:  # Found the owner
                    break
                else:
                    self.functions_visited[caller.f_code.co_name].pure = False
                    self.functions_visited[caller.f_code.co_name].mutates(var)
                if caller.f_back.f_code.co_name == FuncType.BASE:
                    return
                caller = caller.f_back

    def trace_calls(self, frame, event, arg):
        co = frame.f_code
        func_name = co.co_name
        frame.f_trace_opcodes = True

        if func_name == FuncType.CONSTRUCTOR:
            # print("\n\n\n")
            # print(frame.f_globals)
            # print(frame.f_locals)
            # print("\n\n\n")
            return

        if func_name in self.ignore:
            return

        if event == EventType.CALL:
            print_frame(frame, event, arg)
            ########################################################################################################
            if func_name not in self.functions_visited:
                self.functions_visited[func_name] = FunctionInfo()
            return self.trace_bytecodes

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

    def trace_c_calls(self, frame, event, arg):
        if event == EventType.C_CALL:
            print("\n\nEvent", event, "Frame: ", frame, "line-number", frame.f_lineno, "last-line", frame.f_lasti,
                  "Arg", arg)
            caller = frame
            while caller is not None:
                # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                if caller.f_code.co_name in self.functions_visited:
                    self.functions_visited[caller.f_code.co_name].pure = False
                    # self.functions_visited[caller.f_code.co_name].mutates()
                print(caller)
                print(frame.f_back)
                if caller == frame.f_back or \
                        frame.f_back.f_code.co_name == "<module>":
                    return
                caller = frame.f_back
                # time.sleep(2)
