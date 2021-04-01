#ifndef SCALING_PYTHON_UTILS_H
#define SCALING_PYTHON_UTILS_H

#include <Python.h>
#include <frameobject.h>
#include <string>

PyObject *loadFunc(const char *module, const char *method);

_Py_CODEUNIT *get_curr_instruction(PyFrameObject *frame);

void print_bytecode(PyFrameObject *frame);

PyObject *get_referrers(PyObject *obj);

PyObject *tos(PyFrameObject *frame, int i);

void debug_obj(PyObject *obj);

void debug_frame_info(PyFrameObject *frame);

#endif //SCALING_PYTHON_UTILS_H
