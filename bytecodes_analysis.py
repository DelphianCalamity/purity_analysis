import sys
import dis

class FunctionInfo:
    def __init__(self):
        self.pure = 1
        self.mutated_objects = set()

    def mutates(self, varname):
        self.mutated_objects.add(varname)

class FunctionVariables:
    def __init__(self, func_name):
        self.func_name = func_name
        self.locals = set()
        self.globals = set()

    def add_locals(self, locals):
        self.locals.add(locals)

    def add_globals(self, globals):
        self.globals.add(globals)

    def find_in_locals(self, var):
        return var in self.locals

    def find_in_globals(self, var):
        return var in self.globals



def analyze(code):

    def trace_calls(frame, event, arg):
        co = frame.f_code
        func_name = co.co_name
        if func_name in ignore_functions:
            return

        if event == "call":

            print("Frame: ", frame)
            print("Event: ", event)
            print("Arg: ", arg)
            print("-------Frame code object------ ", co)
            print("CodeObject argcount: ", co.co_argcount)
            print("CodeObject nlocals: ", co.co_nlocals)
            print("CodeObject varnames: ", co.co_varnames)
            print("CodeObject cellvars: ", co.co_cellvars)
            print("CodeObject freevars: ", co.co_freevars)
            print("CodeObject globals: ", co.co_names)
            print("CodeObject consts: ", co.co_consts)
            print("CodeObject stacksize: ", co.co_stacksize)
            print("CodeObject code: ", co.co_code)
            print("CodeObject bytecodes: ", dis.disco(co))

            f_locals = frame.f_locals
            # f_globals = frame.f_globals

            func_line_no = frame.f_lineno
            func_filename = co.co_filename
            caller = frame.f_back
            print(caller)
            if caller is not None:
                caller_line_no = caller.f_lineno
                caller_filename = caller.f_code.co_filename
            else:
                caller_line_no = None
                caller_filename = None
            print('Calling: \n func-name: %s\n,  on line: %s, of file: %s from line: %s, of file: %s' % \
                  (func_name, func_line_no, func_filename,
                   caller_line_no, caller_filename))

            print("Frame flocals: ", f_locals)
            # print("Frame fglob: ", f_globals)

            #############################################################################################################
            if func_name not in functions_visited:
                functions_visited[func_name] = FunctionInfo()

            # Add frame's variables in the stack
            variables_stack.append(FunctionVariables(func_name))
            variables_stack[-1].add_locals(co.co_varnames + co.co_cellvars)
            variables_stack[-1].add_globals(co.co_names)

            # Track the STORE bytecodes
            bytecodes = dis.get_instructions(frame.f_code)
            for bytecode in bytecodes:
                if bytecode.opname == "STORE_GLOBAL":
                    print("Bytecode:", bytecode)

                    var = bytecode.argval
                    for function_variables in variables_stack[::-1]:
                        if function_variables.find_in_locals(var):  # Trace the origin of this variable
                            break
                        else: # current function is impure
                            functions_visited[function_variables.func_name].pure = 0
                            functions_visited[function_variables.func_name].mutates(var)

            print("\n\n\n")

        elif event == "return":
            variables_stack.pop()

        elif event == "c_call":
            print("Frame: ", frame, "line-number", frame.f_lineno, "last-line", frame.f_lasti)
            print("Event: ", event)
            print("Arg: ", arg)
            # print(dis.disco(frame.f_code, lasti=frame.f_lasti))
            # print("bytecode: ", frame.f_code.co_code[frame.f_lasti + 1])
            # print(dis.opname[frame.f_code.co_code[frame.f_lasti]])
            print("\n\n\n")



    functions_visited = {}
    variables_stack = []        # Treat as a stack
    ignore_functions = {"<module>"}
    sys.setprofile(trace_calls)
    exec(code)
    sys.setprofile(None)

    output = {}
    for func_name in functions_visited:
        output[func_name] = {"pure" : functions_visited[func_name].pure,
                             "mutated_objects" : list(functions_visited[func_name].mutated_objects)}
    print(output)
    return output


if __name__ == '__main__':

    source = """ 
def foo():
    def bar():  
        global x, y
        x = y = 1 

    bar()

x = y = 0
foo()
"""

    analyze(source)