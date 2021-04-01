#include "Tracer.h"

static int Tracer_trace(PyObject *Py_UNUSED(obj), PyFrameObject *frame, int what, PyObject *Py_UNUSED(arg)) {
    return tracer->trace(frame, what);
}

static PyObject *tracer_start(PyObject *Py_UNUSED(self), PyObject *Py_UNUSED(args)) {
    delete tracer;
    tracer = new Tracer;
    PyEval_SetTrace(Tracer_trace, nullptr);
    Py_RETURN_NONE;
}

static PyObject *tracer_stop(PyObject *Py_UNUSED(self), PyObject *args) {
    PyEval_SetTrace(nullptr, nullptr);

    const char *arg = nullptr;
    char *str = nullptr;
    if (PyArg_ParseTuple(args, "|s", &arg) && arg != nullptr) {
        str = new char[strlen(arg) + 6]; // strlen(".json") + 1
        strcpy(str, arg);
        strcat(str, ".json");
    }
    tracer->log_annotations(str);
    delete[] str;
    delete tracer;
    Py_RETURN_NONE;
}

static PyMethodDef Tracer_methods[] = {
    {"start", tracer_start, METH_VARARGS, PyDoc_STR("Start the tracer")},
    {"stop",  tracer_stop,  METH_VARARGS, PyDoc_STR("Stop the tracer")},
    {nullptr, nullptr, 0, nullptr}
};

static PyModuleDef tracermodule = {
    PyModuleDef_HEAD_INIT,
    "ctracer",
    "Side-Effect analysis",
    -1,
    Tracer_methods,       /* methods */
    nullptr,
    nullptr,
    nullptr,
    nullptr
};

PyMODINIT_FUNC PyInit_ctracer(void) {
    return PyModule_Create(&tracermodule);
}
