import ctypes
import dis
import gc
import pprint as pp
from collections import defaultdict
from types import ModuleType

from termcolor import colored


class FuncType:
    BASE = '<module>'
    CONSTRUCTOR = "__init__"


class EventType:
    C_CALL = 'c_call'
    CALL = 'call'
    RETURN = 'return'


# StoreOps = {
#     'STORE_ATTR',
#     'STORE_DEREF',
#     # 'STORE_FAST',
#     'STORE_GLOBAL',
#     'STORE_NAME',
#     'STORE_SUBSCR',
# }


class FunctionInfo:
    def __init__(self, frame=None):
        self.func_name = frame.f_code.co_name
        self.func_line_no = frame.f_lineno
        self.func_filename = frame.f_code.co_filename
        frame = frame.f_back
        self.pfunc_name = frame.f_code.co_name
        self.pfunc_line_no = frame.f_lineno
        self.pfunc_filename = frame.f_code.co_filename
        self.pure = True
        # nonlocal vars only
        self.mutated_objects = defaultdict(set)


def keys_by_value_locals(locals, value):
    res = []
    for key in locals:
        if hex(id(locals[key])) == value:
            res.append(key)
    return res


def value_by_key_globals_or_locals(frame, var):
    var_address = None
    if var in frame.f_locals:
        var_ = frame.f_locals[var]
        var_address = hex(id(var_))
    elif var in frame.f_globals:
        var_ = frame.f_globals[var]
        var_address = hex(id(var_))
    else:
        print("\n\n\n~~~Bug~~~!\n\n")
        # exit(1)
    return var_address


def find_referrers(lmap, obj_address, named_refs, ref_ids, frame_ids):
    gc.collect()
    referrers = gc.get_referrers(ctypes.cast(int(obj_address, 0), ctypes.py_object).value)
    ref_ids.append(hex(id(referrers)))
    i = 0
    for ref in referrers:

        print("\n\n\n\n\n\n\n\n\n\n", 'len refs', colored(len(referrers) - i, "green"))
        i += 1
        ref_id = hex(id(ref))

        if ref_id in ref_ids or ref_id in frame_ids:
            print("Continue")
            continue

        ref_ids.append(ref_id)
        print(colored("REF-ID", "yellow"), hex(id(ref)), type(ref))
        # if isinstance(ref, dict):
        #     pp.pprint(ref.keys())
        # else:
        #     pp.pprint(ref)
        # Direct Reference - base case
        if ref_id in lmap:
            f = lmap[ref_id]
            print(colored("Found in L-map", "red"))
            pp.pprint(lmap[ref_id])
            # print("Locals", f.f_locals)
            if isinstance(f, ModuleType):
                locals_ = vars(f)
            else:
                locals_ = f.f_locals
            keys = keys_by_value_locals(locals_, obj_address)
            if hex(id(f)) in named_refs:
                named_refs[hex(id(f))][1] += keys
            else:
                named_refs[hex(id(f))] = [f, keys]

            print(colored("Named Referrers", "red"))
            for r in named_refs.values():
                if isinstance(r[0], ModuleType):
                    func_name = str(r[0])
                else:
                    func_name = r[0].f_code.co_name
                print("     ", colored(func_name, "green"), colored(r[1], "blue"))

        # Indirect reference - recursive case
        # trace back indirect referrers till we reach locals
        else:
            find_referrers(lmap, ref_id, named_refs, ref_ids, frame_ids)

        del ref_ids[-1]
    del ref_ids[-1]


def print_frame(frame, event, arg):
    co = frame.f_code
    func_name = co.co_name

    print(colored("\n\n##############################", "yellow"))
    print("\n\nFrame: ", frame)
    print("Event: ", event)
    print("Arg: ", arg)
    print("-------Frame code object------ ", co)
    # print("CodeObject argcount: ", co.co_argcount)

    print(colored("CodeObject nlocals: ", "red"), co.co_nlocals)
    print(colored("CodeObject varnames: ", "red"), co.co_varnames)
    print(colored("CodeObject cellvars: ", "red"), co.co_cellvars)
    print(colored("CodeObject freevars: ", "red"), co.co_freevars)
    print(colored("CodeObject globals: ", "red"), co.co_names)
    print("CodeObject bytecodes: ", dis.disco(co))
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
    print(colored('Calling: \n func-name: %s\n,  on line: %s, of file: %s from line: %s, of file: %s' % \
                  (func_name, func_line_no, func_filename,
                   caller_line_no, caller_filename), "green"))
    # frame.f_back.f_code.f_lineo
    # print(colored("Frame flocals: ", "yellow"))
    # print(colored(f_locals.keys(), "blue"))
    # print(colored("\nFrame fglob: ", "yellow"))
    # print(colored(f_globals.keys(), "blue"))