#include "utils.h"

namespace Color {
    const char *RED = "\033[31m";
    const char *GREEN = "\033[32m";
    const char *YELLOW = "\033[33m";
    const char *BLUE = "\033[34m";
    const char *MAGENTA = "\033[35m";
    const char *CYAN = "\033[36m";
    const char *WHITE = "\033[37m";
    const char *DEFAULT = "\033[39m";
}

PyObject *loadFunc(const char *module, const char *method) {
    PyObject *myModule = PyImport_ImportModule(module);
    return PyObject_GetAttrString(myModule, method);
}

_Py_CODEUNIT *get_curr_instruction(PyFrameObject *frame) {
    auto *first_instr = (_Py_CODEUNIT *) PyBytes_AS_STRING(frame->f_code->co_code);
    _Py_CODEUNIT *instr = first_instr;
    if (frame->f_lasti >= 0) {
        instr += frame->f_lasti / sizeof(_Py_CODEUNIT);
    }
    return instr;
}

const char *get_str_from_object(PyObject *obj) {
    PyObject *temp = PyObject_Str(obj);
    temp = PyUnicode_AsASCIIString(temp);
    if (nullptr == temp)
        return "";
    char *str_name = PyBytes_AsString(temp);
    return str_name;
}

void print_bytecode(PyFrameObject *frame, PyObject *dis, PyObject *itertools) {
    PyObject *get_instructions = PyObject_GetAttrString(dis, "get_instructions");
    PyObject *islice = PyObject_GetAttrString(itertools, "islice");

    PyObject *args = PyTuple_Pack(1, frame->f_code);
    PyObject *gen = PyObject_CallObject(get_instructions, args);

    args = PyTuple_Pack(3, gen, PyLong_FromLong(frame->f_lasti / 2), Py_None);
    PyObject *slice = PyObject_CallObject(islice, args);

    PyObject *result = PyObject_CallMethod(slice, "__next__", nullptr);
    PyObject_Print(result, stdout, Py_PRINT_RAW);
    printf("\n");
}

PyObject *get_referrers(PyObject *obj) {
    PyObject *gc = PyImport_ImportModule("gc");
    PyObject *get_referrers = PyObject_GetAttrString(gc, "get_referrers");

    PyObject *args = PyTuple_Pack(1, obj);
    return PyObject_CallObject(get_referrers, args);
}

void iterate_list_print(PyObject *list) {
    Py_ssize_t len = PyList_Size(list);
    printf("----(%ld)----\n", len);
    for (Py_ssize_t i = 0; i < len; ++i) {
        PyObject *result = PyList_GET_ITEM(list, i);
        PyObject_Print(result, stdout, Py_PRINT_RAW);
        printf("\n");
    }
    printf("------------\n");
}

PyObject *tos(PyFrameObject *frame, int i) {
    PyObject **stack_pointer = frame->f_stacktop;
    return stack_pointer[-i];
}

void debug_obj(PyObject *obj) {
    PyObject_Print(obj, stdout, Py_PRINT_RAW);
    printf("\n");
    PyObject *referrers = get_referrers(obj);
    iterate_list_print(referrers);
}

int PyList_Contains(PyObject *a, PyObject *el) {
    PyObject *item;
    Py_ssize_t i;
    int cmp;
    for (i = 0, cmp = 0; cmp == 0 && i < PyList_Size(a); ++i) {
        item = PyList_GET_ITEM(a, i);
        Py_INCREF(item);
        cmp = PyObject_RichCompareBool(item, el, Py_EQ);
        Py_DECREF(item);
    }
    return cmp;
}

int PyTuple_Contains(PyObject *a, PyObject *el) {
    Py_ssize_t i;
    int cmp;
    for (i = 0, cmp = 0; cmp == 0 && i < PyTuple_Size(a); ++i)
        cmp = PyObject_RichCompareBool(PyTuple_GET_ITEM(a, i), el, Py_EQ);
    return cmp;
}

PyObject *get_name_info(Py_ssize_t name_index, PyObject *cellvars, PyObject *freevars) {
    PyObject *res;
    if (name_index < PyTuple_GET_SIZE(cellvars)) {
        res = PyTuple_GetItem(cellvars, name_index);
    } else {
        res = PyTuple_GetItem(freevars, name_index - PyTuple_GET_SIZE(cellvars));
    }
    return res;
}

void debug_frame_info(PyFrameObject *frame) {
    puts(Color::RED);
    printf("\n\n-------------\nFrame name: ");
    puts(Color::DEFAULT);
    PyObject_Print(frame->f_code->co_name, stdout, Py_PRINT_RAW);
//    PyObject_Print(frame->f_code->co_code, stdout, Py_PRINT_RAW);
    printf("\n-------------\n\n");
    printf("CodeObject bytecodes:\n--------\n");
    PyObject *args = PyTuple_Pack(1, frame->f_code);
    PyObject *disco = loadFunc("dis", "disco");
    PyObject_CallObject(disco, args);
    printf("\n--------\n\n");
    printf("CodeObject varnames: ");
    PyObject_Print(frame->f_code->co_varnames, stdout, Py_PRINT_RAW);
    printf("\n");
    printf("CodeObject cellvars: ");
    PyObject_Print(frame->f_code->co_cellvars, stdout, Py_PRINT_RAW);
    printf("\n");
    printf("CodeObject freevars: ");
    PyObject_Print(frame->f_code->co_freevars, stdout, Py_PRINT_RAW);
    printf("\n");
    printf("CodeObject globals: ");
    PyObject_Print(frame->f_code->co_names, stdout, Py_PRINT_RAW);
    printf("\n");

    puts(Color::BLUE);
    printf("LOCALS: ");
    puts(Color::DEFAULT);
    PyObject_Print(frame->f_locals, stdout, Py_PRINT_RAW);
    printf("\n");
    puts(Color::BLUE);
    printf("GLOBALS: ");
    puts(Color::DEFAULT);
    PyObject_Print(frame->f_locals, stdout, Py_PRINT_RAW);
    printf("\n");
}
