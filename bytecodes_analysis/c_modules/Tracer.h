#ifndef SCALING_PYTHON_TRACER_H
#define SCALING_PYTHON_TRACER_H

#include <Python.h>
#include <frameobject.h>

#include <string>
#include <unordered_set>
#include <unordered_map>

struct FunctionInfo {
    bool pure;
    std::string frame;
    std::string parent_frame;
    std::unordered_set <std::string> mutated_objects;

    FunctionInfo(std::string frame, std::string parent_frame);
};

class Tracer{
    std::unordered_map<PyObject*, PyObject*> locals_map;
    std::unordered_map<PyFrameObject*, FunctionInfo> functions_info;

    public:
    Tracer();
    PyObject *dis;
    PyObject *itertools;
    PyObject *sys;
    bool initialized;

    int handle_call(PyFrameObject *);
    int handle_opcode(PyFrameObject *);
    int handle_return(PyFrameObject *);
    int call(PyObject *, PyFrameObject *, int, PyObject *);
};

extern Tracer *tracer;

#endif //SCALING_PYTHON_TRACER_H
