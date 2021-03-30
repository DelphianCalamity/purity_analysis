from distutils.core import setup, Extension

def main():
    setup(name="ctracer",
          version="1.0.0",
          description="Side effect analysis",
          author="<your name>",
          author_email="your_email@gmail.com",
          ext_modules=[Extension("ctracer", ["c_modules/ctracer.cc", "c_modules/Tracer.cc", "c_modules/utils.cc"])])

if __name__ == "__main__":
    main()