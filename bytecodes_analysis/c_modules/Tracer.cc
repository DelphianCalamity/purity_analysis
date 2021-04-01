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

FunctionInfo::FunctionInfo(std::string frame, std::string parent_frame) {
    this->frame = frame;
    this->parent_frame = parent_frame;
    pure = true;
}

Tracer::Tracer() {
    dis = PyImport_ImportModule("dis");
    itertools = PyImport_ImportModule("itertools");
    sys = PyImport_ImportModule("sys");
    initialized = false;
}

void Tracer::initialize(PyFrameObject* frame) {
    PyFrameObject *caller = frame;
    while ((PyObject *) caller != nullptr) {
        PyObject_Print((PyObject *) caller, stdout, Py_PRINT_RAW); printf("\n");
        locals_map[caller->f_locals] = (PyObject *) caller;
        caller = caller->f_back;
    }
    // todo: insert locals from modules imported at a later stage as well
    PyObject *modules = PyObject_GetAttrString(sys, "modules");
    PyObject* vals = PyDict_Values(modules);
    for (int i = 0; i < PyList_Size(vals); ++i) {
        PyObject* module = PyList_GET_ITEM(vals, i);
//        Py_INCREF(module);
        PyObject* locals = PyObject_GetAttrString(module, "__dict__");
//        PyObject_Print(module, stdout, Py_PRINT_RAW); printf("\n");
        locals_map[locals] = module;
    }
}

void Tracer::print_locals_map() {
    puts(Color::YELLOW);
    printf("\n---------------------------------\nLocals-Map:\n");
    for (auto it = locals_map.cbegin(); it != locals_map.cend(); ++it) {
        printf("%p : ", it->first);
        PyObject_Print((PyObject *) it->second, stdout, Py_PRINT_RAW); printf("\n");
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
            while ((PyObject *) caller != Py_None &&
                   PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) {
                if (caller->f_locals != nullptr && PyDict_Contains(caller->f_locals, name)) {
                    break;
                } else {
                    functions_info.at(caller).pure = false;
                    functions_info.at(caller).mutated_objects.insert(get_str_from_object(name));
                    caller = caller->f_back;
                }
            }
            break;
        }
        case STORE_DEREF: {
            PyObject *name = get_name_info(instr.oparg, frame->f_code->co_cellvars, frame->f_code->co_freevars);
            PyObject_Print(name, stdout, Py_PRINT_RAW);
            PyFrameObject *caller = frame;
            while ((PyObject *) caller != Py_None &&
                   PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) {
                if (PyTuple_Contains(caller->f_code->co_cellvars, name)) {
                    break;
                } else {
                    functions_info.at(caller).pure = false;
                    functions_info.at(caller).mutated_objects.insert(get_str_from_object(name));
                    caller = caller->f_back;
                    PyObject_Print((PyObject *) caller, stdout, Py_PRINT_RAW);
                    printf("\n");
                }
            }
            break;
        }
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
        functions_info.insert({frame, FunctionInfo(get_str_from_object((PyObject *) frame), get_str_from_object((PyObject *) frame->f_back))});
    }
    tracer->locals_map[frame->f_locals] = (PyObject *) frame; // todo: increase ref for locals otherwise they will be lost
    return 0;
}

int Tracer::handle_return(PyFrameObject *frame) {
    std::cout << Color::GREEN;
    printf("\n\n\nDELETING FROM LMAP:");
    std::cout << Color::DEFAULT;
    PyObject_Print((PyObject *) frame, stdout, Py_PRINT_RAW); printf("\n");
    tracer->locals_map.erase(frame->f_locals);
    return 0;
}

int Tracer::call(PyObject *self, PyFrameObject *frame, int what, PyObject *arg) {

    if (!tracer->initialized) {
        tracer->initialized = true;
        tracer->initialize(frame);
        tracer->print_locals_map();
        sleep(2);
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

void Tracer::log_annotations(void) {
    FILE* out = fopen("annotations.json", "w");
    for (auto& function_info : functions_info) {
        printf("\n\n\n\nFrame: %s\n", function_info.second.frame.c_str());
        fprintf(out, "Frame: %s\n", function_info.second.frame.c_str());
        printf("\tParent Frame: %s\n", function_info.second.parent_frame.c_str());
        fprintf(out, "\tParent Frame: %s\n", function_info.second.parent_frame.c_str());
        printf("\tpure: %s\n", function_info.second.pure ? "true" : "false");
        fprintf(out, "\tpure: %s\n", function_info.second.pure ? "true" : "false");
        printf("\tMutated objects:\n");
        fprintf(out, "\tMutated objects:\n");
        for (auto& obj : function_info.second.mutated_objects) {
            printf("\t\t%s\n", obj.c_str());
            fprintf(out, "\t\t%s\n", obj.c_str());
        }
    }
    fclose(out);
}
