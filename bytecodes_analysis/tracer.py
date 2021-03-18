import json
from itertools import islice

from bytecodes_analysis.utils import *


class Tracer:

    def __init__(self, ignore=None):
        self.functions_visited = {}
        self.ignore = [] if ignore is None else ignore
        self.lmap = {}
        self.init = True

        # with open("bytecodes_analysis/c_function_annotations.json") as json_file:
        #     self.native_annotations = json.load(json_file)

    def _get_instruction(self, frame, index):
        instructions = dis.get_instructions(frame.f_code)
        return next(islice(instructions, int(index / 2), None))

    def generic_tracing(self, frame, event, arg):
        print(colored("!!!!!", "green"), "\n\nEvent:", event, "function: ", frame.f_code.co_name, "arg:", arg)

        caller = frame
        while caller is not None:
            print(colored("\nFrame", "red"), caller)
            print(colored("\nLocals", "red"), caller.f_locals)
            print(colored("\nGlobals", "red"), caller.f_globals)
            self.lmap[hex(id(caller.f_locals))] = caller
            caller = caller.f_back
        pp.pprint(self.lmap)

    def trace_bytecodes(self, frame, event, arg):
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
                    self.functions_visited[caller.f_code.co_name].pure = False
                    self.functions_visited[caller.f_code.co_name].mutates(var)
                caller = caller.f_back

        elif opname == 'STORE_DEREF':
            caller = frame
            while caller is not None and caller.f_code.co_name != FuncType.BASE:
                # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                if var in caller.f_code.co_cellvars:  # Found the owner
                    break
                else:
                    self.functions_visited[caller.f_code.co_name].pure = False
                    self.functions_visited[caller.f_code.co_name].mutates(var)
                caller = caller.f_back

        elif opname in {"STORE_ATTR", "STORE_SUBSCR"}:
            # Get the referrer to the object that we write from the previous bytecode
            last_i = frame.f_lasti - 1 if opname == "STORE_ATTR" else frame.f_lasti - 4
            prev_i = self._get_instruction(frame, last_i)
            mutated_obj_address = value_by_key_globals_or_locals(frame, prev_i.argval)

            print(colored("Starting..\n", "red"))
            ref_ids = [];
            named_refs = []
            find_referrers(self.lmap, mutated_obj_address, named_refs, ref_ids, frame)

            ref_map = {}
            for r in named_refs:
                func_name = r[0].f_code.co_name
                if func_name in ref_map:
                    ref_map[func_name] += r[1]
                else:
                    ref_map[func_name] = r[1]

            print(colored("Refs Map", "red"))
            for r in ref_map:
                print("     ", colored(r, "green"), colored(ref_map[r], "blue"))

            caller = frame
            while caller is not None and caller.f_code.co_name != FuncType.BASE:
                # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)

                ref_map.pop(caller.f_code.co_name)
                if len(ref_map) == 0:
                    return

                # print(colored("Refs Map", "red"))
                # for r in ref_map:
                #     print("     ", colored(r, "green"), colored(ref_map[r], "blue"))

                self.functions_visited[caller.f_code.co_name].pure = False
                self.functions_visited[caller.f_code.co_name].mutates(json.dumps(ref_map))
                caller = caller.f_back


    def trace_calls(self, frame, event, arg):
        co = frame.f_code
        func_name = co.co_name
        frame.f_trace_opcodes = True

        if self.init:
            self.init = False
            caller = frame
            while caller is not None:
                self.lmap[hex(id(caller.f_locals))] = caller
                caller = caller.f_back
            return
        # {FuncType.CONSTRUCTOR,
        if func_name == FuncType.BASE or func_name == FuncType.CONSTRUCTOR or \
                func_name in self.ignore:
            return
        # time.sleep(1)
        if event == EventType.CALL:
            print_frame(frame, event, arg)
            self.lmap[hex(id(frame.f_locals))] = frame

            if func_name not in self.functions_visited:
                self.functions_visited[func_name] = FunctionInfo()
            return self.trace_bytecodes

        # elif event == EventType.RETURN:
        #     print(colored("DELETING FROM LMAP", "green"), frame)
        #     self.lmap.pop(hex(id(frame)))

    def trace_c_calls(self, frame, event, arg):

        if self.init:
            self.init = False
            # print(colored("AAAAAAAA", "blue"))
            # time.sleep(10)
            caller = frame
            while caller is not None:
                self.lmap[hex(id(caller.f_locals))] = caller
                # pp.pprint(self.lmap)
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
            caller = frame
            while caller is not None and caller.f_code.co_name != FuncType.BASE:

                # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                if caller.f_code.co_name in self.functions_visited:
                    self.functions_visited[caller.f_code.co_name].pure = False
                    # self.functions_visited[caller.f_code.co_name].mutates()
                print(caller)
                print(frame.f_back)
                caller = frame.f_back

    def log_annotations(self, filename):
        output = {}
        for func_name in self.functions_visited:
            output[func_name] = {
                "pure": self.functions_visited[func_name].pure,
                "mutated_objects": sorted(list(self.functions_visited[func_name].mutated_objects))
            }
        with open(filename + ".annotations", 'w') as w:
            r = json.dumps(output, indent=4)
            w.write(r)
        pp.pprint(output)
        return output
