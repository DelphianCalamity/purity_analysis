import dis
import json

from bytecodes_analysis.utils import EventType, FunctionInfo, FunctionVariables, StoreOps


class Tracer:

    def __init__(self):
        self.functions_visited = {}
        self.variables_stack = []  # Treat as a stack

    def generic_tracing(self, frame, event, arg):
        print("Event:", event, "function: ", frame.f_code.co_name, "arg:", arg)

    def trace_calls(self, frame, event, arg):
        co = frame.f_code
        func_name = co.co_name
        if func_name == EventType.BASE:
            return

        if event == EventType.CALL:
            # print_frame(frame, event, arg)

            ########################################################################################################
            if func_name not in self.functions_visited:
                self.functions_visited[func_name] = FunctionInfo()

            # Add frame's variables in the stack
            self.variables_stack.append(FunctionVariables(func_name))
            self.variables_stack[-1].add_locals(co.co_varnames + co.co_cellvars)
            self.variables_stack[-1].add_globals(co.co_names + co.co_freevars)
            # for i in self.variables_stack:
            #     i.print()
            # Track the STORE bytecodes
            bytecodes = dis.get_instructions(frame.f_code)
            for bytecode in bytecodes:
                if bytecode.opname in StoreOps:
                    # print("Bytecode:", bytecode)
                    var = bytecode.argval
                    for function_variables in self.variables_stack[::-1]:
                        if function_variables.find_in_locals(var):  # Trace the origin of this variable
                            break
                        else:  # current function is impure
                            self.functions_visited[function_variables.func_name].pure = False
                            self.functions_visited[function_variables.func_name].mutates(var)

            print("\n\n\n")

        elif event == EventType.RETURN:
            self.variables_stack.pop()

        elif event == EventType.C_CALL:
            print("Frame: ", frame, "line-number", frame.f_lineno, "last-line", frame.f_lasti)
            print("Event: ", event)
            print("Arg: ", arg)
            # print(dis.disco(frame.f_code, lasti=frame.f_lasti))
            # print("bytecode: ", frame.f_code.co_code[frame.f_lasti + 1])
            # print(dis.opname[frame.f_code.co_code[frame.f_lasti]])
            print("\n\n\n")

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
        return output
