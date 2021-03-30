#include "utils.h"

PyObject *loadFunc(const char *module, const char *method) {
    PyObject *myModuleString = PyUnicode_FromString(module);
    PyObject *myModule = PyImport_Import(myModuleString);
    return PyObject_GetAttrString(myModule, method);
}

_Py_CODEUNIT *get_curr_instruction(PyFrameObject *frame) {
    _Py_CODEUNIT *first_instr = (_Py_CODEUNIT *) PyBytes_AS_STRING(frame->f_code->co_code);
    _Py_CODEUNIT *instr = first_instr;
    if (frame->f_lasti >= 0) {
        instr += frame->f_lasti / sizeof(_Py_CODEUNIT);
    }
    return instr;
}

void print_bytecode(PyFrameObject *frame) {
    PyObject *args = PyTuple_Pack(1, frame->f_code);
    PyObject *get_instructions = loadFunc("dis", "get_instructions");
    PyObject *gen = PyObject_CallObject(get_instructions, args);
    args = PyTuple_Pack(3, gen, PyLong_FromLong(frame->f_lasti / 2), Py_None);
    PyObject *islice = loadFunc("itertools", "islice");
    PyObject *slice = PyObject_CallObject(islice, args);
    PyObject *next = PyObject_GetAttrString(slice, "__next__");
    PyObject *result = PyObject_CallFunction(next, NULL);
    PyObject_Print(result, stdout, Py_PRINT_RAW);
    printf("\n");
}