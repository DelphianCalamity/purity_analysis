#include "utils.h"

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

std::string get_str_from_object(PyObject* obj) {
    PyObject *temp = PyObject_Str(obj);
    temp = PyUnicode_AsASCIIString(temp);

    printf("------DEBUG------\n");
    printf("Obj:\n");
    PyObject_Print(obj, stdout, Py_PRINT_RAW);
    printf("\n");
    printf("temp:\n");
    PyObject_Print(temp, stdout, Py_PRINT_RAW);
    printf("\n");
    printf("------     ------\n");

    if (nullptr == temp)
        return "";
    char* str_name = PyBytes_AsString(temp);
    printf("\n\n-%p-\n", str_name);
    printf("\nfdsfsdfsdfdsfsdf \n\n-%s-\n\n\n\n\n\n\n", str_name);
    return std::string(str_name);
}

void print_bytecode(PyFrameObject *frame) {
    PyObject *dis = PyImport_ImportModule("dis");
    PyObject *get_instructions = PyObject_GetAttrString(dis, "get_instructions");

    PyObject *itertools = PyImport_ImportModule("itertools");
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
