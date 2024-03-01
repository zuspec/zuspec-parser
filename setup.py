#*****************************************************************************
#* setup.py
#*
#* zuspec-parser Python extension setup file
#*****************************************************************************

import os
import sys

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
except ImportError as e:
    from setuptools import setup
    print("Falling back: %s" % str(e))


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
            'zsp_parser = zsp_parser.pkginfo:PkgInfo'
        }
    },
    install_requires=[
        'debug_mgr',
        'ciostream'
    ],
    setup_requires=[
        'pyastbuilder',
        'cython'
    ]
)

if isSrcBuild:
    setup_args["ivpm_extdep_pkgs"] = ["debug-mgr", "ciostream"]
    setup_args["ivpm_extra_data"] = {
        "zsp_parser": [
            ("build/include", "share"),
            ("build/{libdir}/{libpref}antlr4-runtime{dllext}", ""),
            ("build/{libdir}/{libpref}ast{dllext}", ""),
            ("build/{libdir}/{libpref}zsp-parser{dllext}", ""),
        ]
    }

setup(**setup_args)
