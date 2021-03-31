#include "Tracer.h"
#include "utils.h"
#include <opcode.h>

Tracer *tracer;

struct Instruction {
    int opcode;
    int oparg;

    explicit Instruction(const _Py_CODEUNIT *instr) {
        opcode = _Py_OPCODE(*instr);
        oparg = _Py_OPARG(*instr);
    }
};

void debug_info(PyFrameObject *frame) {
    printf("debug info\n");
    print_bytecode(frame);
    Instruction instr(get_curr_instruction(frame));
    switch (instr.opcode) {
        PyObject *obj;
//        case STORE_GLOBAL:
//        case STORE_NAME:
//        case STORE_DEREF:
        case STORE_ATTR:
            obj = tos(frame, 1);
        case STORE_SUBSCR:
            obj = tos(frame, 2);
            debug_obj(obj);
        default:
            printf("other\n");
    }
}

int Tracer::handle_opcode(PyFrameObject *frame) {
    Instruction instr(get_curr_instruction(frame));

    switch (instr.opcode) {
        case STORE_GLOBAL:
        case STORE_NAME: {
            PyFrameObject *caller = frame;
            PyObject *name = PyTuple_GetItem(frame->f_code->co_names, instr.oparg);
            PyObject_Print(name, stdout, Py_PRINT_RAW);
            printf("\n");

//          PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")
            while ((PyObject *) caller != Py_None &&
                   PyUnicode_CompareWithASCIIString(caller->f_code->co_name, "<module>")) {
                // print("\ncaller", caller.f_code.co_name, "\nLocals", caller.f_locals, "\nGlobals", caller.f_globals)
                PyObject *temp = PyUnicode_AsASCIIString(caller->f_code->co_name);
                if (nullptr == temp) {
                    return -1;
                }
                char *str_name = PyByteArray_AsString(temp);
                PyObject_Print((PyObject *) caller, stdout, Py_PRINT_RAW);
                PyObject_Print(caller->f_locals, stdout, Py_PRINT_RAW);

                if (caller->f_locals != nullptr && PyDict_Contains(caller->f_locals, name)) {
                    break;
                } else {
                    functions_info[caller].pure = false;
                    functions_info[caller].mutated_objects.insert(str_name);
                    caller = caller->f_back;
                }
            }
            break;
        }
        case STORE_DEREF:
            printf("STORE_DEREF\n");
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
    printf("\n");
    return 0;
}

int Tracer::handle_call(PyFrameObject *frame) {
    printf("Frame name: ");
    PyObject_Print(frame->f_code->co_name, stdout, Py_PRINT_RAW);
    PyObject_Print(frame->f_code->co_code, stdout, Py_PRINT_RAW);
    printf("\n");
    printf("CodeObject bytecodes:\n--------\n");
    PyObject *args = PyTuple_Pack(1, frame->f_code);
    PyObject *disco = loadFunc("dis", "disco");
    PyObject_CallObject(disco, args);
    printf("\n--------\n\n");

    if (functions_info.find(frame) == functions_info.end()) {
        functions_info.insert({frame, FunctionInfo()});
    }
    return 0;
}

int Tracer::call(PyObject *self, PyFrameObject *frame, int what, PyObject *arg) {
    frame->f_trace_opcodes = 1;
    if (what == PyTrace_OPCODE) {
        debug_info(frame);
    }
    return 0;
    switch (what) {
        case PyTrace_CALL:
            if (handle_call(frame) < 0) {
                return -1;
            }
            break;
        case PyTrace_OPCODE:
            if (handle_opcode(frame)) {
                return -1;
            }
            break;
        default:
            break;
    }
    return 0;
}
