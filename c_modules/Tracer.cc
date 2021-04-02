#include "Tracer.h"
#include "utils.h"
#include <opcode.h>
#include <sstream>

using namespace std;
Tracer *tracer;

struct Instruction {
    int opcode;
    int oparg;

    explicit Instruction(const _Py_CODEUNIT *instr) {
        opcode = _Py_OPCODE(*instr);
        oparg = _Py_OPARG(*instr);
    }
};

FunctionInfo::FunctionInfo(const char *frame, const char *parent_frame) :
    pure(true),
    frame(frame),
    parent_frame(parent_frame) {}

Tracer::Tracer() {
    dis = PyImport_ImportModule("dis");
    itertools = PyImport_ImportModule("itertools");
    sys = PyImport_ImportModule("sys");
    gc = PyImport_ImportModule("gc");
    initialized = false;
}

void Tracer::initialize(PyFrameObject *frame) {
    PyFrameObject *caller = frame;
    while (caller != nullptr) {
        PyObject_Print((PyObject *) caller, stdout, Py_PRINT_RAW);
        printf("\n");
        locals_map[caller->f_locals] = (PyObject *) caller;
        caller = caller->f_back;
    }
    // todo: insert locals from modules imported at a later stage as well
    PyObject *modules = PyObject_GetAttrString(sys, "modules");
    PyObject *vals = PyDict_Values(modules);
    for (int i = 0; i < PyList_Size(vals); ++i) {
        PyObject *module = PyList_GET_ITEM(vals, i);
        PyObject *locals = PyObject_GetAttrString(module, "__dict__");
        locals_map[locals] = module;
    }
}

void Tracer::print_locals_map() {
    puts(Color::YELLOW);
    printf("\n---------------------------------\nLocals-Map:\n");
    for (auto it : locals_map) {
        printf("%p : ", it.first);
        PyObject_Print(it.second, stdout, Py_PRINT_RAW);
        printf("\n");
    }
    printf("---------------------------------\n\n");
    puts(Color::DEFAULT);
}

void Tracer::print_refs_map(std::unordered_map<PyFrameObject *, std::unordered_set<std::string>> &refs_map) {
    puts(Color::GREEN);
    printf("\n---------------------------------\nRefs-Map:\n");
    for (const auto &it : refs_map) {
        printf("%p : ", it.first);
//        PyObject_Print(it.second, stdout, Py_PRINT_RAW);
        printf("\n");
    }
    printf("---------------------------------\n\n");
    puts(Color::DEFAULT);
}

unordered_set<string> keys_by_value_locals(PyObject *obj, PyObject *locals) {
    unordered_set<string> res;

    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(locals, &pos, &key, &value)) {
        if (obj == value) {
            res.insert(get_str_from_object(key));
        }
    }
    return res;
}

void Tracer::find_referrers(PyObject *obj,
                            std::unordered_map<PyFrameObject *, std::unordered_set<std::string>> &refs_map,
                            std::unordered_set<PyObject *> &excluded_ids) {
    PyObject_CallMethod(gc, "collect", nullptr);

    puts(Color::YELLOW);
    printf("Object %p:\n", obj);
    PyObject_Print((PyObject *) obj, stdout, Py_PRINT_RAW);
    printf("\n");
    puts(Color::DEFAULT);
    PyObject *referrers = get_referrers(obj, gc);
    excluded_ids.insert(referrers);
    puts(Color::RED);
    printf("Referrers:\n");
    PyObject_Print((PyObject *) referrers, stdout, Py_PRINT_RAW);
    printf("\n");
    puts(Color::DEFAULT);
    puts(Color::GREEN);
    for (int i = 0; i < PyList_Size(referrers); ++i) {
        PyObject *referrer = PyList_GET_ITEM(referrers, i);

        if (excluded_ids.find(referrer) != excluded_ids.end()) continue;
        if (frame_ids.find(referrer) != frame_ids.end()) continue;
        printf("Excluded ids:\n");
        for (auto id : excluded_ids) {
            printf("%p ", id);
        }
        printf("\n");
        excluded_ids.insert(referrer);
        printf("REF-ID: %p, ", referrer);
        PyObject_Print((PyObject *) Py_TYPE(referrer), stdout, Py_PRINT_RAW);
        printf("\n");

        //Direct Reference - base case
//        print_locals_map();
        if (locals_map.find(referrer) != locals_map.end()) {
            PyObject *r = locals_map[referrer];
            printf("Found in L-map\n");
            PyObject *locals;
            if (PyModule_Check(r)) {
                locals = PyObject_GetAttrString(r, "__dict__");
            } else {
                locals = ((PyFrameObject *) r)->f_locals;
            }
            unordered_set<string> keys = keys_by_value_locals(obj, locals);
            // TODO: PyObject*
            refs_map[(PyFrameObject *) r].insert(keys.begin(), keys.end());
        } else {
            //Indirect reference - recursive case
            //trace back indirect referrers till we reach locals
            find_referrers(referrer, refs_map, excluded_ids);
        }
//        del excluded_ids[-1];
        excluded_ids.erase(referrer);
    }
//    del excluded_ids[-1];
    excluded_ids.erase(referrers);
    Py_DecRef(referrers);
    puts(Color::DEFAULT);
}

int Tracer::handle_opcode(PyFrameObject *frame) {
    Instruction instr(get_curr_instruction(frame));
    print_bytecode(frame, dis, itertools);
    switch (instr.opcode) {
        case STORE_GLOBAL:
        case STORE_NAME: {
            PyObject *name = PyTuple_GetItem(frame->f_code->co_names, instr.oparg);
            PyFrameObject *caller = frame;
            while ((PyObject *) caller != Py_None) {
                if (!PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) break;
                if (caller->f_locals != nullptr && PyDict_Contains(caller->f_locals, name)) break;
                auto &function_info = functions_info.at((PyObject *) caller);
                function_info.pure = false;

                stringstream f_addr;
                f_addr << caller;
                function_info.mutated_objects[f_addr.str()].insert(get_str_from_object(name));
                caller = caller->f_back;
            }
        }
            break;
        case STORE_DEREF: {
            PyObject *name = get_name_info(instr.oparg, frame->f_code->co_cellvars, frame->f_code->co_freevars);
            PyFrameObject *caller = frame;
//            unordered_set<basic_string<char>> mutated;
            while ((PyObject *) caller != Py_None) {
                if (!PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) break;
                if (PyTuple_Contains(caller->f_code->co_cellvars, name)) break;
                auto &function_info = functions_info.at((PyObject *) caller);
                function_info.pure = false;

                std::stringstream f_addr;
                f_addr << caller;
                function_info.mutated_objects[f_addr.str()].insert(get_str_from_object(name));
                caller = caller->f_back;
            }
//            functions_info.at(caller)
        }
            break;
        case STORE_ATTR:
        case STORE_SUBSCR: {
            for (auto f : frame_ids) {
                frame_getlocals((PyFrameObject *) f);
            }

            puts(Color::RED);
            printf("Starting..\n");
            PyObject_Print((PyObject *) frame->f_locals, stdout, Py_PRINT_RAW);
            printf("\n");
            puts(Color::DEFAULT);
            PyObject *TOS = tos(frame, instr.opcode == STORE_ATTR ? 1 : 2);
//            debug_obj(TOS);

            std::unordered_set<PyObject *> excluded_ids;
            std::unordered_map<PyFrameObject *, std::unordered_set<std::string>> named_refs_map;

            find_referrers(TOS, named_refs_map, excluded_ids);
            print_refs_map(named_refs_map);

            PyFrameObject *caller = frame;
            while ((PyObject *) caller != Py_None) {
                if (!PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) break;

                if (named_refs_map.find(caller) != named_refs_map.end()) {
                    named_refs_map.erase(caller);
                }
                if (named_refs_map.empty()) {
                    break;
                }

                auto &function_info = functions_info.at((PyObject *) caller);
                function_info.pure = false;

                for (const auto &ref : named_refs_map) {
                    stringstream f_addr;
                    f_addr << ref.first;
                    function_info.mutated_objects[f_addr.str()].insert(ref.second.begin(), ref.second.end());
                }
                caller = caller->f_back;
            }
        }
            break;
        default:
            break;
    }
    return 0;
}

int Tracer::handle_call(PyFrameObject *frame) {

    if (frame->f_locals == nullptr) {
        frame_getlocals(frame); // TODO DECREF?
    }

    debug_frame_info(frame);
    if (functions_info.find((PyObject *) frame) == functions_info.end()) {
        functions_info.insert({(PyObject *) frame, {
            get_str_from_object((PyObject *) frame),
            get_str_from_object((PyObject *) frame->f_back)
        }});
    }
    locals_map[frame->f_locals] = (PyObject *) frame; // todo: increase ref for locals otherwise they will be lost
    frame_ids.insert((PyObject *) frame);
    return 0;
}

int Tracer::handle_return(PyFrameObject *frame) {
    puts(Color::GREEN);
    printf("DELETING FROM LMAP:");
    puts(Color::DEFAULT);
    PyObject_Print((PyObject *) frame, stdout, Py_PRINT_RAW);
    printf("\n");
    locals_map.erase(frame->f_locals);
    frame_ids.erase((PyObject *) frame);
    return 0;
}

int Tracer::trace(PyFrameObject *frame, int what) {
    if (!initialized) {
        initialized = true;
        initialize(frame);
        print_locals_map();
    }
    frame->f_trace_opcodes = 1;
    switch (what) {
        case PyTrace_CALL:
            if (handle_call(frame) < 0) {
                return -1;
            }
            break;
        case PyTrace_RETURN:
            if (handle_return(frame) < 0) {
                return -1;
            }
            break;
        case PyTrace_OPCODE:
            if (handle_opcode(frame) < 0) {
                return -1;
            }
            break;
        case PyTrace_EXCEPTION:
            printf("PyTrace_EXCEPTION\n");
            return -1;
        case PyTrace_C_CALL:
            printf("PyTrace_C_CALL\n");
            PyObject_Print((PyObject *) frame, stdout, Py_PRINT_RAW);
            printf("\n");
            break;
        default:
            break;
    }
    return 0;
}

void Tracer::log_annotations(const char *filename) {
    FILE *out = fopen(filename, "w");
    if (out == nullptr) {
        log_annotations(stdout);
    } else {
        log_annotations(out);
        fclose(out);
    }
}

void Tracer::log_annotations(FILE *out) {
    size_t functions = functions_info.size();
    fprintf(out, "[\n");
    for (auto &function_entry : functions_info) {
        FunctionInfo &functionInfo = function_entry.second;
        fprintf(out, "  {\n"\
                            "    \"frame\": \"%s\",\n"\
                            "    \"parent\": \"%s\",\n"\
                            "    \"pure\": %s,\n"\
                            "    \"mutated\": {\n",
                functionInfo.frame.c_str(),
                functionInfo.parent_frame.c_str(),
                functionInfo.pure ? "true" : "false");
        size_t mutated = functionInfo.mutated_objects.size();
        for (auto &mutations_entry : functionInfo.mutated_objects) {
            fprintf(out, "      \"%s\": [\n", mutations_entry.first.c_str());
            size_t mutations = mutations_entry.second.size();
            for (auto &obj : mutations_entry.second) {
                fprintf(out, "        \"%s\"%s\n", obj.c_str(), --mutations ? "," : "");
            }
            fprintf(out, "      ]%s\n", --mutated ? "," : "");
        }
        fprintf(out, "    }\n"\
                            "  }%s\n", --functions ? "," : "");
    }
    fprintf(out, "]\n");
}
