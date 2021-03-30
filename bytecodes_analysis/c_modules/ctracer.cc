#include "ctracer.h"
#include "Tracer.h"

#define PEEK(n)           (stack_pointer[-(n)])
#define STACK_LEVEL()     ((int)(stack_pointer - frame->f_valuestack))
#define EMPTY()           (STACK_LEVEL() == 0)

int Tracer_call(PyObject *obj, PyFrameObject *frame, int what, PyObject *arg) {
    return tracer->call(obj, frame, what, arg);
}

static PyObject *tracer_start(PyObject *self, PyObject *args_unused) {
    if (tracer) {
        delete tracer;
    }
    tracer = new Tracer;
    PyEval_SetTrace((Py_tracefunc) Tracer_call, (PyObject *) self);
    Py_RETURN_NONE;
}

static PyObject *tracer_stop(PyObject *self, PyObject *args) {
    PyEval_SetTrace(NULL, NULL);
    delete tracer;
    Py_RETURN_NONE;
}

static PyMethodDef Tracer_methods[] = {
    {"start", (PyCFunction) tracer_start, METH_VARARGS,
        PyDoc_STR("Start the tracer")},

    {"stop",  (PyCFunction) tracer_stop,  METH_VARARGS,
        PyDoc_STR("Stop the tracer")},
    {NULL}
};

static PyModuleDef tracermodule = {
    PyModuleDef_HEAD_INIT,
    "ctracer",
    "Side-Effect analysis",
    -1,
    Tracer_methods       /* methods */
};

PyMODINIT_FUNC PyInit_ctracer(void) {
    return PyModule_Create(&tracermodule);
}
