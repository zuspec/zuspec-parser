#*****************************************************************************
#* setup.py
#*
#* zuspec-parser Python extension setup file
#*****************************************************************************
import os
import sys
import platform
from setuptools import Extension, setup, find_namespace_packages

version="0.0.1"

proj_dir = os.path.dirname(os.path.abspath(__file__))
pythondir = os.path.join(proj_dir, "python")

try:
    import sys
    sys.path.insert(0, os.path.join(proj_dir, "python"))
    from zsp_parser.__build_num__ import BUILD_NUM
    version += ".%d" % BUILD_NUM
except Exception:
    pass

isSrcBuild = False

try:
    from ivpm.setup import setup
    isSrcBuild = os.path.isdir(os.path.join(proj_dir, "src"))
    print("zuspec-parser: isSrcBuild: %s" % str(isSrcBuild))
except ImportError as e:
    from setuptools import setup
    print("zuspec-parser: not IVPM build (Falling back): %s" % str(e))

include_dirs = []

if isSrcBuild:
    include_dirs.append(pythondir)
    include_dirs.append(os.path.join(proj_dir, "src", "include"))
    include_dirs.append(os.path.join(proj_dir, "build", "include"))

library_dirs = []
libraries = []
extra_link_args = []

# TODO: in 'src' mode, must copy extension files

ast_ext = Extension(
    "zsp_parser.ast", 
    [
        os.path.join(pythondir, "ast.pyx"),
        os.path.join(pythondir, "PyBaseVisitor.cpp")
    ],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    extra_link_args=extra_link_args,
    language="c++")
ext = Extension(
    "zsp_parser.core", 
    [ os.path.join(pythondir, "core.pyx") ],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    extra_link_args=extra_link_args,
    language="c++")

extensions=[ast_ext, ext]

setup_requires=['cython', 'ciostream']

if isSrcBuild:
    setup_requires.append('pyastbuilder')

setup_args = dict(
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
    ext_modules=extensions,
    entry_points={
        "ivpm.pkginfo": {
            'zuspec-parser = zsp_parser.pkginfo:PkgInfo'
        }
    },
    install_requires=[
        'debug-mgr',
        'ciostream'
    ],
    setup_requires=setup_requires,
)

if isSrcBuild:
    import shutil
    # Copy generated 'AST' extension files over before
    # attempting to build
    # for file in ('ast_decl.pxd', 'ast.pxd'):
    #     shutil.copyfile(
    #         os.path.join(proj_dir, "build", "zsp_ast", "ext", file),
    #         os.path.join(proj_dir, "python", "zsp_parser", file))
    # shutil.copyfile(
    #     os.path.join(proj_dir, "build", "zsp_ast", "ext", 'ast.pyx'),
    #     os.path.join(proj_dir, "python", 'ast.pyx'))

    setup_args["ivpm_extdep_pkgs"] = ["debug-mgr", "ciostream"]
    setup_args["ivpm_extdep_data"] = [
        (os.path.join(proj_dir, "build", "zsp_ast", "ext", 'ast_decl.pxd'),
            os.path.join(proj_dir, "python", "zsp_parser", 'ast_decl.pxd')),
        (os.path.join(proj_dir, "build", "zsp_ast", "ext", 'ast.pxd'),
            os.path.join(proj_dir, "python", "zsp_parser", 'ast.pxd')),
        (os.path.join(proj_dir, "build", "zsp_ast", "ext", 'ast.pyx'),
            os.path.join(proj_dir, "python", 'ast.pyx')),
        (os.path.join(proj_dir, "build", "zsp_ast", "ext", 'PyBaseVisitor.cpp'),
            os.path.join(proj_dir, "python", 'PyBaseVisitor.cpp')),
        (os.path.join(proj_dir, "build", "zsp_ast", "ext", 'PyBaseVisitor.h'),
            os.path.join(proj_dir, "python", 'PyBaseVisitor.h')),
    ]
    setup_args["ivpm_extra_data"] = {
        "zsp_parser": [
            ("build/include", "share"),
            ("build/{libdir}/{libpref}antlr4-runtime{dllext}", ""),
            ("build/{libdir}/{libpref}ast{dllext}", ""),
            ("build/{libdir}/{libpref}zsp-parser{dllext}", ""),
        ]
    }

setup(**setup_args)
