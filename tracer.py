import dis
import json
import sys
import traceback
from itertools import islice

import ctracer
from utils import *


def get_instruction(frame, index):
    instructions = dis.get_instructions(frame.f_code)
    return next(islice(instructions, int(index / 2), None))


class Tracer:

    def __init__(self, ignore=None):
        self.functions_visited = {}
        self.ignore = [] if ignore is None else ignore
        self.lmap = {}
        self.frame_ids = set()
        self.init = True

        # with open("bytecodes_analysis/c_function_annotations.json") as json_file:
        #     self.native_annotations = json.load(json_file)

    def _get_instruction(self, frame, index):
        instructions = dis.get_instructions(frame.f_code)
        return next(islice(instructions, int(index / 2), None))

    def generic_tracing(self, frame, event, arg):
        try:
            print(colored("!!!!!", "green"),
                  "\n\nEvent:", event, "function: ", frame.f_code.co_name, "arg:", arg, "frame",
                  colored(str(frame), "blue"))

            caller = frame
            # while caller is not None:
            #     print(colored("\nFrame", "red"), caller)
            print(colored("\nLocals", "red"), caller.f_locals.keys(), hex(id(caller.f_locals)))
            print(colored("\nGlobals", "red"), caller.f_globals.keys(), hex(id(caller.f_globals)))
        #     self.lmap[hex(id(caller.f_locals))] = caller
        #     caller = caller.f_back
        # pp.pprint(self.lmap)
        except:
            print(colored("\n\nTrace Generic failed\n\n", "red"))
            print(colored(traceback.format_exc(), "red"))

    def trace_bytecodes(self, frame, event, arg):

        try:
            if event != "opcode":
                return

            # print("Event:", event, "function: ", frame.f_code.co_name, "arg:", arg)
            i = self._get_instruction(frame, frame.f_lasti)
            print(i)
            opname = i.opname
            var = i.argval
            if opname == "RETURN_VALUE":
                print(colored("\n\n\nDELETING FROM LMAP", "green"), frame)
                self.lmap.pop(hex(id(frame.f_locals)))
                self.frame_ids.remove(hex(id(frame)))

            # print("\ncaller", frame.f_code.co_name, "\nLocals", frame.f_locals, "\nGlobals", frame.f_globals)
            if opname in {'STORE_GLOBAL', 'STORE_NAME'}:
                # Trace var all the way back to the initial frame; stop if it is found in a frame's locals
                # _, var_address = self.find_in_globals_or_locals(frame, var)
                caller = frame
                while caller is not None and caller.f_code.co_name != FuncType.BASE:
                    # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                    if var in caller.f_locals:
                        break
                    else:
                        frame_id = hex(id(caller))
                        self.functions_visited[frame_id].pure = False
                        self.functions_visited[frame_id].mutated_objects['todo'].add(var)
                    caller = caller.f_back

            elif opname == 'STORE_DEREF':
                caller = frame
                while caller is not None and caller.f_code.co_name != FuncType.BASE:
                    # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                    if var in caller.f_code.co_cellvars:  # Found the owner
                        break
                    else:
                        frame_id = hex(id(caller))
                        self.functions_visited[frame_id].pure = False
                        self.functions_visited[frame_id].mutated_objects['todo'].add(var)
                    caller = caller.f_back

            elif opname in {"STORE_ATTR", "STORE_SUBSCR"}:
                # Get the referrer to the object that we write from the previous bytecode
                # last_i = frame.f_lasti - 1 if opname == "STORE_ATTR" else frame.f_lasti - 4
                # prev_i = self._get_instruction(frame, last_i)
                # print(colored(prev_i, "yellow"))
                # mutated_obj_address = value_by_key_globals_or_locals(frame, prev_i.argval)
                i = 1 if opname == "STORE_ATTR" else 2
                tos = ctracer.tos(frame, i)
                mutated_obj_address = hex(id(tos))
                # print("fdsfsdfsdfdsfsdfa", tos)
                del tos
                if mutated_obj_address == None:
                    print(colored("\n\nCouldn't find object; Ignoring current 'STORE_ATTR'\n\n", "red"))
                    return

                print(colored("Starting..\n", "red"))
                ref_ids = []
                named_refs = {}
                find_referrers(self.lmap, mutated_obj_address, named_refs, ref_ids, self.frame_ids)

                print(colored("Refs Map", "red"))
                for f, keys in named_refs.values():
                    if isinstance(f, ModuleType):
                        func_name = str(f)
                    else:
                        func_name = f.f_code.co_name
                    print("     ", colored(func_name, "green"), colored(keys, "blue"))

                caller = frame
                while caller is not None and caller.f_code.co_name != FuncType.BASE:
                    # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                    frame_id = hex(id(caller))
                    if frame_id in named_refs.keys():
                        named_refs.pop(frame_id)
                    if len(named_refs) == 0:
                        return
                    # print(colored("Refs Map", "red"))
                    # for r in ref_map:
                    #     print("     ", colored(r, "green"), colored(ref_map[r], "blue"))

                    self.functions_visited[frame_id].pure = False
                    for f, vars in named_refs.values():
                        self.functions_visited[frame_id].mutated_objects[str(f)].update(vars)
                    caller = caller.f_back
        except:
            print(colored("\n\nTrace Bytecodes failed\n\n", "red"))
            print(colored(traceback.format_exc(), "red"))
            sys.settrace(None)
            sys.setprofile(None)
            exit(1)

    def trace_calls(self, frame, event, arg):
        try:
            frame.f_trace_opcodes = True

            if self.init:
                self.init = False
                # Add the locals of all the imported modules todo: insert locals from modules imported at a later stage as well
                for module in sys.modules.values():
                    self.lmap[hex(id(vars(module)))] = module

                caller = frame
                while caller is not None:
                    self.lmap[hex(id(caller.f_locals))] = caller
                    caller = caller.f_back
                # return
            # {FuncType.CONSTRUCTOR,
            # or func_name == FuncType.CONSTRUCTOR or
            # if func_name == FuncType.BASE or \
            #         func_name in self.ignore:
            #     return
            # time.sleep(2)
            if event == EventType.CALL:
                print_frame(frame, event, arg)
                self.lmap[hex(id(frame.f_locals))] = frame
                self.frame_ids.add(hex(id(frame)))
                print(colored("\n\nInstert", "red"), self.frame_ids)

                if hex(id(frame)) not in self.functions_visited:
                    self.functions_visited[hex(id(frame))] = FunctionInfo(frame)
                return self.trace_bytecodes

        except:
            print(colored("\n\nTrace Calls failed\n\n", "red"))
            print(colored(traceback.format_exc(), "red"))
            sys.settrace(None)
            sys.setprofile(None)
            exit(1)

        # elif event == EventType.RETURN:
        #     print(colored("DELETING FROM LMAP", "green"), frame)
        #     self.lmap.pop(hex(id(frame)))

    def trace_c_calls(self, frame, event, arg):
        try:
            if self.init:
                self.init = False
                # Add the locals of all the imported modules todo: insert locals from modules imported at a later stage as well
                for module in sys.modules.values():
                    self.lmap[hex(id(vars(module)))] = module

                caller = frame
                while caller is not None:
                    self.lmap[hex(id(caller.f_locals))] = caller
                    pp.pprint(self.lmap)
                    # print(colored("\nFrame", "red"), caller)
                    # print(colored("\nLocals", "red"), caller.f_locals)
                    # print(colored("\nGlobals", "red"), caller.f_globals)
                    caller = caller.f_back
                # exit(0)

            if event == EventType.C_CALL:
                print("\n\nEvent", event, "Frame: ", frame, "line-number", frame.f_lineno, "last-line", frame.f_lasti,
                      "Arg", arg)
                # print(colored("\n\n\n,Arg", "green"), dir(arg), arg.__name__, "\n\n\n")
                # if arg.__name__ in self.native_annotations \
                #     and self.native_annotations[arg.__name__] == True:
                #         return
                # caller = frame
                # while caller is not None and caller.f_code.co_name != FuncType.BASE:
                #     frame_id = hex(id(caller))
                #     print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                #     if frame_id in self.functions_visited:
                #         self.functions_visited[frame_id].pure = False
                #         self.functions_visited[frame_id].mutates()
                #     print(caller)
                #     caller = caller.f_back
        except:
            print(colored("\n\nTrace C calls failed\n\n", "red"))
            print(colored(traceback.format_exc(), "red"))
            sys.settrace(None)
            sys.setprofile(None)
            exit(1)

    def log_annotations(self, filename):
        try:
            output = []
            for function_info in self.functions_visited.values():
                mutated_objects = {k: list(v) for k, v in function_info.mutated_objects.items()}
                output.append({
                    "func_name": function_info.func_name,
                    "func_line_no": function_info.func_line_no,
                    "func_filename": function_info.func_filename,
                    "pfunc_name": function_info.pfunc_name,
                    "pfunc_line_no": function_info.pfunc_line_no,
                    "pfunc_filename": function_info.pfunc_filename,
                    "pure": function_info.pure,
                    "mutated_objects": mutated_objects
                })
            with open(filename + ".json", 'w') as w:
                r = json.dumps(output, indent=4)
                w.write(r)
            pp.pprint(output)
            return output
        except:
            print(colored("\n\nLog annotations\n\n", "red"))
            print(colored(traceback.format_exc(), "red"))
            exit(1)
