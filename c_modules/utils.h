#ifndef SCALING_PYTHON_UTILS_H
#define SCALING_PYTHON_UTILS_H

#include <Python.h>
#include <frameobject.h>

PyObject *frame_getlocals(PyFrameObject *f);

PyObject *loadFunc(const char *module, const char *method);

_Py_CODEUNIT *get_curr_instruction(PyFrameObject *frame);

PyObject *get_referrers(PyObject *obj, PyObject *gc);

PyObject *tos(PyFrameObject *frame, int i);

void debug_obj(PyObject *obj);

void debug_frame_info(PyFrameObject *frame);

int PyTuple_Contains(PyObject *a, PyObject *el);

void print_bytecode(PyFrameObject *frame, PyObject *dis, PyObject *itertools);

PyObject *get_name_info(Py_ssize_t name_index, PyObject *cellvars, PyObject *);

const char *get_str_from_object(PyObject *obj);

namespace Color {
    extern const char *RED;
    extern const char *GREEN;
    extern const char *YELLOW;
    extern const char *BLUE;
    extern const char *MAGENTA;
    extern const char *CYAN;
    extern const char *WHITE;
    extern const char *DEFAULT;
}

#endif //SCALING_PYTHON_UTILS_H
