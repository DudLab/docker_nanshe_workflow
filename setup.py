__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Aug 03 2015 20:22:54 EDT$"


from setuptools import setup


setup(
    name="startup-nanshe-workflow",
    version="0.0.1",
    description="A container-based image processing workflow.",
    url="https://github.com/nanshe-org/docker_nanshe_workflow",
    license="Apache 2.0",
    author="John Kirkham",
    author_email="kirkhamj@janelia.hhmi.org",
    scripts=["startup-nanshe-workflow"],
    py_modules=[],
    packages=[],
    build_requires=[],
    install_requires=[],
    tests_require=[],
    zip_safe=True
)
