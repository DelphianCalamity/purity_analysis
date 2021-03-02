class EventType:
    BASE = '<module>'
    C_CALL = 'c_call'
    CALL = 'call'
    RETURN = 'return'


StoreOps = {
    'STORE_ATTR',
    'STORE_DEREF',
    'STORE_FAST',
    'STORE_GLOBAL',
    'STORE_NAME',
    'STORE_SUBSCR',
}


class FunctionInfo:
    def __init__(self):
        self.pure = True
        # nonlocal vars only
        self.mutated_objects = set()

    def mutates(self, var_name):
        self.mutated_objects.add(var_name)


class FunctionVariables:
    def __init__(self, func_name):
        self.func_name = func_name
        self.locals = ()
        self.globals = ()

    def add_locals(self, locals):
        self.locals += locals

    def add_globals(self, globals):
        self.globals += (globals)

    def find_in_locals(self, var):
        print(var)
        print(self.locals)
        return (var in self.locals)

    def find_in_globals(self, var):
        return (var in self.globals)

    def print(self):
        print("func:", self.func_name, ", locals:", self.locals, ", globals:", self.globals)


def print_frame(frame, event, arg):
    co = frame.f_code
    func_name = co.co_name

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
    # print("CodeObject bytecodes: ", dis.disco(co))
    f_locals = frame.f_locals
    f_globals = frame.f_globals

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
