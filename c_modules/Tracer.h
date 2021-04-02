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
    std::unordered_map<std::string, std::unordered_set<std::string>> mutated_objects;

    FunctionInfo(const char *frame, const char *parent_frame);
};

class Tracer {
    std::unordered_map<PyObject *, PyObject *> locals_map;
    // [Module | PyFrameObject] -> FunctionInfo
    std::unordered_map<PyObject *, FunctionInfo> functions_info;
    std::unordered_set<PyObject *> frame_ids;

public:
    Tracer();

    PyObject *dis;
    PyObject *itertools;
    PyObject *sys;
    PyObject *gc;
    bool initialized;

    int handle_call(PyFrameObject *);

    int handle_opcode(PyFrameObject *);

    int handle_return(PyFrameObject *);

    int trace(PyFrameObject *frame, int what);

    void initialize(PyFrameObject *frame);

    void find_referrers(PyObject *, std::unordered_map<PyFrameObject *, std::unordered_set<std::string>> &,
                        std::unordered_set<PyObject *> &);

    void print_locals_map();

    static void print_refs_map(std::unordered_map<PyFrameObject *, std::unordered_set<std::string>> &);

    void log_annotations(FILE *out);

    void log_annotations(const char *filename);
};

extern Tracer *tracer;

#endif //SCALING_PYTHON_TRACER_H
