#*****************************************************************************
#* setup.py
#*
#* zuspec-parser Python extension setup file
#*****************************************************************************

import os
import sys
import subprocess
import sysconfig
import shutil

from setuptools import Extension, setup, find_namespace_packages
from setuptools.command.build_ext import build_ext as _build_ext
from distutils.file_util import copy_file
from Cython.Build import cythonize

version="0.0.1"

if "-DDEBUG" in sys.argv:
    sys.argv.remove("-DDEBUG")
    CMAKE_BUILD_TYPE="Debug"
    _DEBUG = True
else:
    CMAKE_BUILD_TYPE="Release"
    _DEBUG = False

zuspecparser_dir = os.path.dirname(os.path.abspath(__file__))
pythondir = os.path.join(zuspecparser_dir, "python")

if os.path.isdir(os.path.join(zuspecparser_dir, "packages")):
    print("Pacakges are inside this directory")
    packages_dir = os.path.join(zuspecparser_dir, "packages")
else:
    parent = os.path.dirname(zuspecparser_dir)

    if os.path.isdir(os.path.join(parent, "zuspec-parser")):
        print("zuspec-parser is a peer")
        packages_dir = parent
    else:
        raise Exception("Unexpected source layout")

cwd = os.getcwd()
if not os.path.isdir(os.path.join(cwd, "build")):
    os.makedirs(os.path.join(cwd, "build"))

env = os.environ.copy()
python_bindir = os.path.dirname(sys.executable)
print("python_bindir: %s" % str(python_bindir))

if "PATH" in env.keys():
    env["PATH"] = python_bindir + os.pathsep + env["PATH"]
else:
    env["PATH"] = python_bindir

# Run configure...
result = subprocess.run(
    ["cmake", 
     zuspecparser_dir,
     "-GNinja",
     "-DCMAKE_BUILD_TYPE=%s" % CMAKE_BUILD_TYPE,
     "-DPACKAGES_DIR=%s" % packages_dir,
     ],
    cwd=os.path.join(cwd, "build"),
    env=env)

if result.returncode != 0:
    raise Exception("cmake configure failed")

result = subprocess.run(
    ["ninja",
     "-j",
     "%d" % os.cpu_count()
     ],
    cwd=os.path.join(cwd, "build"),
    env=env)
if result.returncode != 0:
    raise Exception("build failed")

#********************************************************************
#* Copy over required files
#********************************************************************
builddir = os.path.join(cwd, "build")
file_m = {
    os.path.join(builddir, "zsp_ast/ext/zsp_ast_decl.pxd") : os.path.join(pythondir, "zuspec_parser/zsp_ast_decl.pxd"),
    os.path.join(builddir, "zsp_ast/ext/zsp_ast.pxd") : os.path.join(pythondir, "zuspec_parser/zsp_ast.pxd"),
    os.path.join(builddir, "zsp_ast/ext/zsp_ast.pyx") : os.path.join(pythondir, "zsp_ast.pyx"),
    os.path.join(builddir, "zsp_ast/ext/PyBaseVisitor.h") : os.path.join(pythondir, "PyBaseVisitor.h")
}

for src,dst in file_m.items():
    shutil.copy(src, dst)

extra_compile_args = sysconfig.get_config_var('CFLAGS').split()
extra_compile_args = []
#extra_compile_args += ["-std=c++11", "-Wall", "-Wextra"]
if _DEBUG:
#    extra_compile_args += ["-g", "-O0", "-DDEBUG=%s" % _DEBUG_LEVEL, "-UNDEBUG"]
    extra_compile_args += ["-g", "-O0", "-UNDEBUG"]
else:
    extra_compile_args += ["-DNDEBUG", "-O3"]

class build_ext(_build_ext):
    def run(self):
        super().run()

    # Needed for Windows to not assume python module (generate interface in def file)
    def get_export_symbols(self, ext):
        return None

    def copy_extensions_to_source(self):
        """ Like the base class method, but copy libs into proper directory in develop. """
        print("copy_extensions_to_source", flush=True)
        super().copy_extensions_to_source()

        build_py = self.get_finalized_command("build_py")
        
        ext = self.extensions[0]
        fullname = self.get_ext_fullname(ext.name)
        filename = self.get_ext_filename(fullname)
        modpath = fullname.split(".")
        package = ".".join(modpath[:-1])
        package_dir = build_py.get_package_dir(package)

        copy_file(
            os.path.join(cwd, "build", "src", "libzuspec-parser.so"),
            os.path.join(package_dir, "libzuspec-parser.so"))
        copy_file(
            os.path.join(cwd, "build", "antlr4", "lib64", "libantlr4-runtime.so"),
            os.path.join(package_dir, "libantlr4-runtime.so"))
                
        dest_filename = os.path.join(package_dir, filename)
        
        print("package_dir: %s dest_filename: %s" % (package_dir, dest_filename))
        
        return

include_dirs=[]

include_dirs.append(os.path.join(zuspecparser_dir, "src/include"))

build_dir = os.path.join(zuspecparser_dir, "build")

include_dirs.append(build_dir)
include_dirs.append(os.path.join(build_dir, "zsp_ast/ext"))
include_dirs.append(os.path.join(build_dir, "zsp_ast/src/include"))

if "CMAKE_BINARY_DIR" in os.environ.keys():
    cmake_binary_dir=os.environ["CMAKE_BINARY_DIR"]
    include_dirs.append(os.path.join(cmake_binary_dir, "zsp_ast/ext"))
    include_dirs.append(os.path.join(cmake_binary_dir, "zsp_ast/ext/"))
    include_dirs.append(os.path.join(cmake_binary_dir, "zsp_ast/src/include"))
    include_dirs.append(os.path.join(pythondir))

library_dirs = [] 

libraries = []

sources = []
sources.append(os.path.join(pythondir, "core.pyx"))

print("sources=" + str(sources))

# TODO: depending on the platform, perform the link differently
extra_link_args=[]
#extra_link_args.append(os.path.join(os.getcwd(), "../antlr4/lib/libantlr4-runtime.a"))

ast_ext_srcs = [os.path.join(pythondir, "zsp_ast.pyx")],
ast_ext = Extension(
    "zuspec_parser.zsp_ast", 
    [
        os.path.join(pythondir, "zsp_ast.pyx"),
#        os.path.join(pythondir, "PyBaseVisitor.cpp")
    ],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    extra_link_args=extra_link_args,
    language="c++")
ext = Extension(
    "zuspec_parser.core", 
    sources,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    extra_link_args=extra_link_args,
    language="c++")

extensions=[ast_ext, ext]

setup(
    name="zuspec-parser",
    packages=find_namespace_packages(where='python'),
    package_dir={'' : 'python' },
    version=version,
    author="Matthew Ballance",
    author_email="matt.ballance@gmail.com",
    description="Provides a PSS parser and related tools",
    long_description="""
    Zuspec parser
    """,
    ext_modules=cythonize(extensions),
    cmdclass={'build_ext': build_ext}
    )
