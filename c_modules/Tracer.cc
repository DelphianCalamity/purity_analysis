#include "Tracer.h"
#include "utils.h"
#include <opcode.h>

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

int Tracer::handle_opcode(PyFrameObject *frame) {
    Instruction instr(get_curr_instruction(frame));
    print_bytecode(frame, tracer->dis, tracer->itertools);

    switch (instr.opcode) {
        case STORE_GLOBAL:
        case STORE_NAME: {
            PyObject *name = PyTuple_GetItem(frame->f_code->co_names, instr.oparg);
            PyFrameObject *caller = frame;
            while ((PyObject *) caller != Py_None) {
                if (!PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) break;
                if (caller->f_locals != nullptr && PyDict_Contains(caller->f_locals, name)) break;
                functions_info.at(caller).pure = false;
                functions_info.at(caller).mutated_objects["dummy"].insert(get_str_from_object(name));
                caller = caller->f_back;
            }
        }
            break;
        case STORE_DEREF: {
            PyObject *name = get_name_info(instr.oparg, frame->f_code->co_cellvars, frame->f_code->co_freevars);
            PyFrameObject *caller = frame;
            while ((PyObject *) caller != Py_None) {
                if (!PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) break;
                if (PyTuple_Contains(caller->f_code->co_cellvars, name)) break;
                functions_info.at(caller).pure = false;
                functions_info.at(caller).mutated_objects["dummy"].insert(get_str_from_object(name));
                caller = caller->f_back;
            }
        }
            break;
        case STORE_ATTR:
            printf("STORE_ATTR\n");
            break;
        case STORE_SUBSCR:
            printf("STORE_SUBSCR\n");
            break;
        default:
            break;
    }
    return 0;
}

int Tracer::handle_call(PyFrameObject *frame) {
    debug_frame_info(frame);
    if (functions_info.find(frame) == functions_info.end()) {
        functions_info.insert({frame, FunctionInfo(get_str_from_object((PyObject *) frame),
                                                   get_str_from_object((PyObject *) frame->f_back))});
    }
    tracer->locals_map[frame->f_locals] = (PyObject *) frame; // todo: increase ref for locals otherwise they will be lost
    return 0;
}

int Tracer::handle_return(PyFrameObject *frame) {
    puts(Color::GREEN);
    printf("DELETING FROM LMAP:");
    puts(Color::DEFAULT);
    PyObject_Print((PyObject *) frame, stdout, Py_PRINT_RAW);
    printf("\n");
    tracer->locals_map.erase(frame->f_locals);
    return 0;
}

int Tracer::trace(PyFrameObject *frame, int what) {
    if (!tracer->initialized) {
        tracer->initialized = true;
        tracer->initialize(frame);
        tracer->print_locals_map();
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
            if (handle_opcode(frame)) {
                return -1;
            }
            break;
        case PyTrace_EXCEPTION:
            printf("error\n");
            exit(0);
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