import json
import sys
import traceback
from itertools import islice

import ctracer

from purity_analysis.utils import *


def get_instruction(frame, index):
    instructions = dis.get_instructions(frame.f_code)
    return next(islice(instructions, index // 2, None))

class Tracer:

    def __init__(self, filename, ignore=None):
        self.functions_visited = {}
        self.ignore = [] if ignore is None else ignore
        self.lmap = {}
        self.frame_ids = set()
        self.init = True
        self.enabled_tracing = False
        self.filename = filename
        self.mapping_file = "mapping_file"
        self.summaries_db = "summaries"
        self.mapping = {}
        self.args = {}
        self.argvalues = {}
        self.key = None
        self.cache_ids = set()

        # with open("bytecodes_analysis/c_function_annotations.json") as json_file:
        #     self.native_annotations = json.load(json_file)

    def generic_tracing(self, frame, event, arg):
        try:
            print(colored("!!!!!", "green"),
                  "\n\nEvent:", event, "function: ", frame.f_code.co_name, "arg:", arg, "frame",
                  colored(str(frame), "blue"))

            caller = frame
            # while caller is not None:
            #     print(colored("\nFrame", "red"), caller)
            print(colored("\nLocals", "red"), caller.f_locals.keys(), id(caller.f_locals))
            print(colored("\nGlobals", "red"), caller.f_globals.keys(), id(caller.f_globals))
        #     self.lmap[id(caller.f_locals)] = caller
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
            i = get_instruction(frame, frame.f_lasti)
            print(i)
            opname = i.opname
            var = i.argval
            if opname == "RETURN_VALUE":
                print(colored("\n\n\nDELETING FROM LMAP", "green"), frame)
                self.lmap.pop(id(frame.f_locals))
                self.frame_ids.remove(id(frame))

            # print("\ncaller", frame.f_code.co_name, "\nLocals", frame.f_locals, "\nGlobals", frame.f_globals)
            if opname in {'STORE_GLOBAL'}:
                # Trace var all the way back to the initial frame; stop if it is found in a frame's locals
                # _, var_address = self.find_in_globals_or_locals(frame, var)
                caller = frame
                while caller is not None and caller.f_code.co_name != FuncType.BASE:
                    # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                    if var in caller.f_locals:
                        break
                    else:
                        # key = str((id(caller), caller.f_back.f_lineno))
                        # if key in self.functions_visited:
                        if caller.f_back.f_code.co_filename == self.filename:
                            key = f'{caller.f_code.co_name} : {caller.f_code.co_firstlineno} : {caller.f_code.co_filename}'
                            self.functions_visited[key].pure = False
                            self.functions_visited[key].mutated_objects['todo'].add(var)
                    caller = caller.f_back

            elif opname == 'STORE_DEREF':
                caller = frame
                while caller is not None and caller.f_code.co_name != FuncType.BASE:
                    # print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                    if var in caller.f_code.co_cellvars:  # Found the owner
                        break
                    else:
                        # key = str((id(caller), caller.f_back.f_lineno))
                        # if key in self.functions_visited:
                        if caller.f_back.f_code.co_filename == self.filename:
                            key = f'{caller.f_code.co_name} : {caller.f_code.co_firstlineno} : {caller.f_code.co_filename}'
                            self.functions_visited[key].pure = False
                            self.functions_visited[key].mutated_objects['todo'].add(var)
                    caller = caller.f_back

            elif opname in {"STORE_ATTR", "STORE_SUBSCR"}:
                # Get the referrer to the object that we write
                i = 1 if opname == "STORE_ATTR" else 2
                tos = ctracer.tos(frame, i)
                if tos is None:
                    print(colored("\n\nCouldn't find object; Ignoring current 'STORE_ATTR'\n\n", "red"))
                    return
                mutated_obj_address = id(tos)

                # print(colored("mutated obj id", "yellow"), hex(mutated_obj_address))
                # for x in self.args:
                #     print(colored("\t{}={}".format(x, self.argvalues[x]), "green"))

                del tos

                if mutated_obj_address in self.cache_ids:
                    return
                else:
                    self.cache_ids.add(mutated_obj_address)

                print(colored("Starting..\n", "red"))
                ref_ids = []
                named_refs = {}
                gc.collect()
                print(self.args); print(self.argvalues)
                # exit(0)
                find_referrers(self.lmap, mutated_obj_address, named_refs, ref_ids, self.frame_ids, self.key, self.args, self.argvalues, self.functions_visited)

                print(colored("Refs Map", "red"))
                for f, keys in named_refs.values():
                    if isinstance(f, ModuleType):
                        func_name = str(f)
                    else:
                        func_name = f.f_code.co_name
                    print("     ", colored(func_name, "green"), colored(keys, "blue"))

                named_refs2 = {}
                caller = frame
                while caller is not None:
                    frame_id = id(caller)
                    if frame_id in named_refs.keys():
                        named_refs2[frame_id] = named_refs[frame_id]
                        named_refs.pop(frame_id)
                    if len(named_refs) == 0:
                        break
                    caller = caller.f_back
                else:
                    print('Continue3')
                    # self.functions_visited[frame_id].pure = False todo
                    # key = str((id(frame), frame.f_back.f_lineno))
                    key = f'{frame.f_code.co_name} : {frame.f_code.co_firstlineno} : {frame.f_code.co_filename}'
                    if frame.f_back.f_code.co_filename == self.filename:
                        for f, vars in named_refs.values():
                            self.functions_visited[key].other_mutated_objects[str(f)].update(vars)

                named_refs = named_refs2
                caller = frame
                while caller is not None and caller.f_code.co_name != FuncType.BASE:
                    frame_id = id(caller)
                    if frame_id in named_refs.keys():
                        named_refs.pop(frame_id)
                    if len(named_refs) == 0:
                        break
                    # key = str((id(caller), caller.f_back.f_lineno))
                    # if key in self.functions_visited:
                    if caller.f_back.f_code.co_filename == self.filename:
                        key = f'{caller.f_code.co_name} : {caller.f_code.co_firstlineno} : {caller.f_code.co_filename}'
                        self.functions_visited[key].pure = False
                        for f, vars in named_refs.values():
                            self.functions_visited[key].mutated_objects[str((f.f_code.co_filename, f.f_code.co_name, f.f_code.co_firstlineno))].update(vars)
                    caller = caller.f_back
        except:
            print(colored("\n\nTrace Bytecodes failed\n\n", "red"), file=sys.stderr)
            print(colored(traceback.format_exc(), "red"), file=sys.stderr)
            sys.settrace(None)
            sys.setprofile(None)
            exit(1)

    def trace_calls(self, frame, event, arg):
        try:
            if self.init:
                self.init = False
                # Add the locals of all the imported modules todo: insert locals from modules imported at a later stage as well
                for module in sys.modules.values():
                    self.lmap[id(vars(module))] = module
                caller = frame
                while caller is not None:
                    self.lmap[id(caller.f_locals)] = caller
                    caller = caller.f_back


            if event == EventType.CALL:
                # print(frame.f_code.co_filename, self.filename)
                # print(frame.f_back.f_code.co_filename, self.filename)
                if frame.f_back.f_code.co_filename == self.filename:  # It is one of the functions I care about
                    self.cache_ids = set()

                    self.args, _, _, argvalues = inspect.getargvalues(frame)
                    if self.args is not None:
                        for i in self.args:
                            print(colored("\t{}={}".format(i, argvalues[i]), "yellow"))
                            self.argvalues[i] = id(argvalues[i])
                            print(colored("\t{}={}".format(i, self.argvalues[i]), "blue"))
                        # exit(0)

                    self.enabled_tracing = True
                    call_site = f'{frame.f_back.f_code.co_filename} : {frame.f_back.f_lineno-6}' # -6 = lines injected for tracing
                    definition_site = f'{frame.f_code.co_name} : {frame.f_code.co_firstlineno} : {frame.f_code.co_filename}'
                    self.key = definition_site

                    if call_site in self.mapping:
                        self.mapping[call_site][len(self.mapping[call_site])] = definition_site
                    else:
                        self.mapping[call_site] = {0 : definition_site}

                    with open(self.summaries_db + ".json", 'r') as summaries:
                        fsummaries = json.load(summaries)
                        if definition_site in fsummaries:
                            self.enabled_tracing = False
                        else:
                            self.functions_visited[definition_site] = FunctionInfo(frame)
                if not self.enabled_tracing:
                    return

                frame.f_trace_opcodes = True
                print_frame(frame, event, arg)
                self.lmap[id(frame.f_locals)] = frame
                self.frame_ids.add(id(frame))
                print(colored("\n\nInsert", "red"), self.frame_ids)

                # key = str((id(frame), frame.f_back.f_lineno))
                # if key not in self.functions_visited:
                #     self.functions_visited[key] = FunctionInfo(frame)
                return self.trace_bytecodes

        except:
            print(colored("\n\nTrace Calls failed\n\n", "red"), file=sys.stderr)
            print(colored(traceback.format_exc(), "red"), file=sys.stderr)
            sys.settrace(None)
            sys.setprofile(None)
            exit(1)

        # elif event == EventType.RETURN:
        #     print(colored("DELETING FROM LMAP", "green"), frame)
        #     self.lmap.pop(id(frame))

    def trace_c_calls(self, frame, event, arg):
        try:
            if self.init:
                self.init = False
                # Add the locals of all the imported modules todo: insert locals from modules imported at a later stage as well
                for module in sys.modules.values():
                    self.lmap[id(vars(module))] = module

                caller = frame
                while caller is not None:
                    self.lmap[id(caller.f_locals)] = caller
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
                #     frame_id = id(caller)
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
            output = {}
            for key, function_info in self.functions_visited.items():
                mutated_objects = {k: list(v) for k, v in function_info.mutated_objects.items()}
                other_mutated_objects = {k: list(v) for k, v in function_info.other_mutated_objects.items()}
                output[f'({function_info.func_name} : {key.split()[1]}'] = {
                    "func_name": function_info.func_name,
                    "func_line_no": function_info.func_line_no,
                    "func_filename": function_info.func_filename,
                    "pfunc_name": function_info.pfunc_name,
                    "pfunc_line_no": function_info.pfunc_line_no,
                    "pfunc_filename": function_info.pfunc_filename,
                    "pure": function_info.pure,
                    "mutated_objects": mutated_objects,
                    "other_mutated_objects": other_mutated_objects
                }
            with open(filename + ".json", 'w') as w:
                r = json.dumps(output, indent=4)
                w.write(r)
            pp.pprint(output)
            return output
        except:
            print(colored("\n\nLog annotations\n\n", "red"))
            print(colored(traceback.format_exc(), "red"))
            exit(1)

    def store_summaries_and_mapping(self):
        try:
            output = {}
            for key, function_info in self.functions_visited.items():
                mutated_objects = {k: list(v) for k, v in function_info.mutated_objects.items()}
                other_mutated_objects = {k: list(v) for k, v in function_info.other_mutated_objects.items()}
                mutated_args = {k: list(v) for k, v in function_info.mutated_args.items()}

                output[key] = {
                    "pure": function_info.pure,
                    "mutated_args": mutated_args,
                    "mutated_objects": mutated_objects,
                    "other_mutated_objects": other_mutated_objects
                }

            # Store new summaries
            with open(self.summaries_db + ".json", 'r') as r:
                fsummaries = json.load(r)

            fsummaries.update(output)
            with open(self.summaries_db + ".json", 'w') as w:
                r = json.dumps(fsummaries, indent=4)
                w.write(r)

            # Store mapping file
            with open(self.mapping_file + ".json", 'w') as w:
                r = json.dumps(self.mapping, indent=4)
                w.write(r)

            pp.pprint(output)
            pp.pprint(self.mapping)

            return output

        except:
            print(colored("\n\nLog annotations\n\n", "red"))
            print(colored(traceback.format_exc(), "red"))
            exit(1)