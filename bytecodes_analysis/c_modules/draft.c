printf("Stack pointer: %p\n", stack_pointer);
printf("Value stack: %p\n", frame->f_valuestack);
if (EMPTY()) {
printf("EMPTY STACK\n");
} else {
printf("STACK TOP: ");
PyObject *top = PEEK(1);
PyObject_Print(top, stdout, Py_PRINT_RAW);
printf("\n");
}

//static PyMethodDef TracerMethods[] = {
//        {"start", method_tracer_start, METH_VARARGS, "Start the tracer."},
//        {"stop",  method_tracer_stop,  METH_VARARGS, "Stop the tracer."},
//        {NULL, NULL, 0, NULL}
//};

//static struct PyModuleDef tracermodule = {
//        PyModuleDef_HEAD_INIT,
//        "ctracer",
//        "Side-Effect analysis",
//        -1,
//        TracerMethods
//};


#ifndef _COVERAGE_UTIL_H
#define _COVERAGE_UTIL_H

#include <Python.h>

/* Compile-time debugging helpers */
#undef WHAT_LOG         /* Define to log the WHAT params in the trace function. */
#undef TRACE_LOG        /* Define to log our bookkeeping. */
#undef COLLECT_STATS    /* Collect counters: stats are printed when tracer is stopped. */
#undef DO_NOTHING       /* Define this to make the tracer do nothing. */

/* Py 2.x and 3.x compatibility */

#if PY_MAJOR_VERSION >= 3

#define MyText_Type                     PyUnicode_Type
#define MyText_AS_BYTES(o)              PyUnicode_AsASCIIString(o)
#define MyBytes_GET_SIZE(o)             PyBytes_GET_SIZE(o)
#define MyBytes_AS_STRING(o)            PyBytes_AS_STRING(o)
#define MyText_AsString(o)              PyUnicode_AsUTF8(o)
#define MyText_FromFormat               PyUnicode_FromFormat
#define MyInt_FromInt(i)                PyLong_FromLong((long)i)
#define MyInt_AsInt(o)                  (int)PyLong_AsLong(o)
#define MyText_InternFromString(s)      PyUnicode_InternFromString(s)

#define MyType_HEAD_INIT                PyVarObject_HEAD_INIT(NULL, 0)

#else

#define MyText_Type                     PyString_Type
#define MyText_AS_BYTES(o)              (Py_INCREF(o), o)
#define MyBytes_GET_SIZE(o)             PyString_GET_SIZE(o)
#define MyBytes_AS_STRING(o)            PyString_AS_STRING(o)
#define MyText_AsString(o)              PyString_AsString(o)
#define MyText_FromFormat               PyUnicode_FromFormat
#define MyInt_FromInt(i)                PyInt_FromLong((long)i)
#define MyInt_AsInt(o)                  (int)PyInt_AsLong(o)
#define MyText_InternFromString(s)      PyString_InternFromString(s)

#define MyType_HEAD_INIT                PyObject_HEAD_INIT(NULL)  0,

#endif /* Py3k */

// Undocumented, and not in all 2.7.x, so our own copy of it.
#define My_XSETREF(op, op2)                     \
    do {                                        \
        PyObject *_py_tmp = (PyObject *)(op);   \
        (op) = (op2);                           \
        Py_XDECREF(_py_tmp);                    \
    } while (0)

/* The values returned to indicate ok or error. */
#define RET_OK      0
#define RET_ERROR   -1

/* Nicer booleans */
typedef int BOOL;
#define FALSE   0
#define TRUE    1

/* Only for extreme machete-mode debugging! */
#define CRASH       { printf("*** CRASH! ***\n"); *((int*)1) = 1; }

#endif /* _COVERAGE_UTIL_H */

PyObject *name = GETITEM(names, oparg);
PyObject *ns = f->f_locals;
if (PyDict_CheckExact(ns))
err = PyDict_SetItem(ns, name, v);
else


//                    PyObject *temp = PyUnicode_AsASCIIString(caller->f_code->co_name);
//                    if (nullptr == temp)
//                        return -1;
//                    char *str_name = PyByteArray_AsString(temp);

//            PyErr_PrintEx(0);