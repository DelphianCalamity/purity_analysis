from distutils.core import setup, Extension


def main():
    setup(name="ctracer",
          description="Side effect analysis",
          ext_modules=[Extension("ctracer", ["c_modules/ctracer.cc", "c_modules/Tracer.cc", "c_modules/utils.cc"])])


if __name__ == "__main__":
    main()
