#include "Tracer.h"

int Tracer_call(PyObject *obj, PyFrameObject *frame, int what, PyObject *arg) {
    return tracer->call(obj, frame, what, arg);
}

static PyObject *tracer_start(PyObject *self, PyObject *args) {
    delete tracer;
    tracer = new Tracer;
    PyEval_SetTrace(Tracer_call, nullptr);
    Py_RETURN_NONE;
}

static PyObject *tracer_stop(PyObject *self, PyObject *args) {
    printf("stop\n");
    PyEval_SetTrace(nullptr, nullptr);
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
