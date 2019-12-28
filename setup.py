import setuptools
from setuptools import setup, Extension
#from numpy.distutils.core import setup
#from numpy.distutils.extension import Extension

compile_opts = {
    "extra_f90_compile_args": [
        "-fopenmp", "-ffree-line-length-none", "-fdiagnostics-color=always", "-Wno-tabs"],
    "f2py_options": ["skip:", "map_border", "calc_weights", ":"],
    "extra_link_args": ["-fopenmp"]
}

mcm = Extension(name="pspy.mcm_fortran.mcm_fortran",
                sources=["pspy/mcm_fortran/mcm_fortran.f90", "pspy/wigner3j/wigner3j_sub.f"],
                **compile_opts)
cov = Extension(name="pspy.cov_fortran.cov_fortran",
                sources=["pspy/cov_fortran/cov_fortran.f90", "pspy/wigner3j/wigner3j_sub.f"],
                **compile_opts)

import versioneer
setup(
    name="pspy",
    version= versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Simons Observatory Collaboration Power Spectrum Task Force",
    author_email="",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
        "Programming Language :: Python :: 3.7"
        "Programming Language :: Python :: 3.8"
        ],
    entry_points={},
    ext_modules=[mcm, cov],
    install_requires=[
        "numpy",
        "healpy",
        "cython", # this one should be installed by pyFFTW
        "pyFFTW @ git+https://github.com/pyFFTW/pyFFTW.git",
        "pillow", # this one should be installed by pixell
        "pixell @ git+https://github.com/simonsobs/pixell.git"],
    license="BSD license",
    packages=["pspy"],
    data_files=[("data", ["data/Planck_Parchment_RGB.txt"])],
)
