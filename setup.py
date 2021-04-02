import sys

from distutils.core import setup, Extension


def main():
    if sys.platform == 'darwin':
        compile_args = ['-stdlib=libc++', "-std=c++11"]
        link_args = ['-lc++']
        setup(name="ctracer",
              description="Side effect analysis",
              ext_modules=[Extension("ctracer", ["c_modules/ctracer.cc", "c_modules/Tracer.cc", "c_modules/utils.cc"],
                                     extra_compile_args=compile_args, extra_link_args=link_args)])

    else:
        setup(name="ctracer",
              description="Side effect analysis",
              ext_modules=[Extension("ctracer", ["c_modules/ctracer.cc", "c_modules/Tracer.cc", "c_modules/utils.cc"])])

if __name__ == "__main__":
    main()
