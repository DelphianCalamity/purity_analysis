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
