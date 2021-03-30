#ifndef SCALING_PYTHON_CTRACER_H
#define SCALING_PYTHON_CTRACER_H

#include <Python.h>
#include <frameobject.h>
#include <code.h>
#include <structmember.h>
#include <opcode.h>
#include "utils.h"
#include <unordered_set>
#include <unordered_map>
#include <string>

struct FunctionInfo {
    bool pure;
    PyFrameObject *frame;
    PyFrameObject *parent_frame;
    std::unordered_set <std::string> mutated_objects;
};


class Tracer {
    std::unordered_map < PyFrameObject * , FunctionInfo > functions_info;

    public:
    int handle_call(PyFrameObject*);
    int handle_opcode(PyFrameObject*);
    int call(PyObject*, PyFrameObject*, int, PyObject*);
};

extern Tracer *tracer;

#endif //SCALING_PYTHON_CTRACER_H
