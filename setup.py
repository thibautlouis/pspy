#- 
# setup.py
#-

import setuptools
from distutils.errors import DistutilsError
from numpy.distutils.core import setup, Extension, build_ext, build_src
import os, sys
import subprocess as sp
import numpy as np


compile_opts = {
    'extra_f90_compile_args': ['-fopenmp','-ffree-line-length-none', '-fdiagnostics-color=always', '-Wno-tabs'],
    'f2py_options': ['skip:', 'map_border', 'calc_weights', ':'],
    'extra_link_args': ['-fopenmp']
}

mcm = Extension(name = 'pspy.mcm_fortran.mcm_fortran',
                sources = ['pspy/mcm_fortran/mcm_fortran.f90', 'pspy/wigner3j/wigner3j_sub.f'],
                **compile_opts)
cov =Extension(name = 'pspy.cov_fortran.cov_fortran',
               sources = ['pspy/cov_fortran/cov_fortran.f90', 'pspy/wigner3j/wigner3j_sub.f'],
               **compile_opts)

requirements=['numpy','pixell']

setup(
      author="Simons Observatory Collaboration Power Spectrum Task Force",
      author_email='',
      classifiers=[
                   'Development Status :: 2 - Pre-Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   ],
      description="PSPY",
      url= "https://github.com/thibautlouis/pspy",
      download_url= "https://github.com/thibautlouis/pspy",
      package_dir={"pspy": "pspy"},
      entry_points={},
      ext_modules=[mcm,cov],
      install_requires=requirements,
      license="BSD license",
      packages=['pspy'],
      data_files=[("data", ["data/Planck_Parchment_RGB.txt"])],
      name= "pspy",
      version= '0.0.1'
)



