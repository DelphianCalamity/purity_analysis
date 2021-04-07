import ctypes
import dis
import gc
import pprint as pp
from collections import defaultdict
from types import ModuleType, FrameType

from termcolor import colored


class FuncType:
    BASE = '<module>'
    CONSTRUCTOR = "__init__"


class EventType:
    C_CALL = 'c_call'
    CALL = 'call'
    RETURN = 'return'


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
        self.other_mutated_objects = defaultdict(set)


def find_referrers(lmap, obj_address, named_refs, ref_ids, frame_ids):
    # gc.collect()
    referrers = gc.get_referrers(ctypes.cast(obj_address, ctypes.py_object).value)
    ref_ids.append(id(referrers))
    ref_ids.append(id(lmap))
    i = 0
    for ref in referrers:
        print("\n\n\n\n\n\n\n\n\n\n", 'len refs', colored(len(referrers) - i, "green"))
        i += 1
        ref_id = id(ref)

        if ref_id in ref_ids or ref_id in frame_ids:
            print("Continue")
            continue
        if isinstance(ref, FrameType):
            print("Continue2")
            continue

        ref_ids.append(ref_id)
        print(colored("REF-ID", "yellow"), id(ref), type(ref))
        if ref_id in lmap:
            f = lmap[ref_id]
            print(colored("Found in L-map", "red"))
            pp.pprint(lmap[ref_id])
            if isinstance(f, ModuleType):
                locals_ = vars(f)
            else:
                locals_ = f.f_locals
            keys = [k for k, v in locals_.items() if id(v) == obj_address]
            if id(f) in named_refs:
                named_refs[id(f)][1] += keys
            else:
                named_refs[id(f)] = [f, keys]

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

    print(colored("CodeObject nlocals: ", "red"), co.co_nlocals)
    print(colored("CodeObject varnames: ", "red"), co.co_varnames)
    print(colored("CodeObject cellvars: ", "red"), co.co_cellvars)
    print(colored("CodeObject freevars: ", "red"), co.co_freevars)
    print(colored("CodeObject globals: ", "red"), co.co_names)
    print("CodeObject bytecodes: ", dis.disco(co))

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
