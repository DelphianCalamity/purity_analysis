cmake_minimum_required(VERSION 3.16)
project(purity_analysis)

set(CMAKE_CXX_STANDARD 14)

include_directories(/usr/include/python3.8)

add_executable(purity_analysis
        bytecodes_analysis/c_modules/ctracer.cc
        bytecodes_analysis/c_modules/Tracer.cc
        bytecodes_analysis/c_modules/Tracer.h
        bytecodes_analysis/c_modules/utils.cc
        bytecodes_analysis/c_modules/utils.h)
