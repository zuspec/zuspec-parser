#!/bin/sh -x

yum update -y
yum install -y glibc-static 
yum install -y java-11-openjdk-devel uuid-devel libuuid-devel

echo "BUILD_NUM=${BUILD_NUM}" >> python/zsp_parser/__build_num__.py
${IVPM_PYTHON} -m pip install ivpm cython
${IVPM_PYTHON} -m ivpm update -a

PYTHON=./packages/python/bin/python
${PYTHON} -m pip install twine auditwheel ninja wheel cython

# First, do all the required code generation. This ensures the
# Python package can be imported during final package build
${PYTHON} setup.py build_ext --inplace

${PYTHON} setup.py bdist_wheel

for whl in dist/*.whl; do
    ${PYTHON} -m auditwheel repair $whl
    rm $whl
done
