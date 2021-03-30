#ifndef SCALING_PYTHON_UTILS_H
#define SCALING_PYTHON_UTILS_H

#include <Python.h>
#include <frameobject.h>
#include <code.h>
#include <structmember.h>
#include <opcode.h>
#include "utils.h"
#include <unordered_set>
#include <unordered_map>
#include <string>
#define RET_OK      0
#define RET_ERROR   -1

PyObject *loadFunc(const char *module, const char *method);
_Py_CODEUNIT * get_curr_instruction(PyFrameObject *frame);
void print_bytecode(PyFrameObject *frame);

#endif //SCALING_PYTHON_UTILS_H
