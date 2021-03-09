#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
  def finalize_options(self):
    _build_ext.finalize_options(self)
    # Prevent numpy from thinking it is still in its setup process:
    __builtins__.__NUMPY_SETUP__ = False
    import numpy
    self.include_dirs.append(numpy.get_include())

setup(
  name='whirlpool_stats',
  packages=find_packages(),
  version='0.2.0',
  description='A set of python scripts allowing to compute statistics about Whirlpool.',
  author='laurentmt',
  author_email='laurentmt145@gmail.com',
  maintainer='laurentmt',
  url='https://github.com/Samourai-Wallet/whirlpool_stats',
  download_url='https://code.samourai.io/whirlpool/whirlpool_stats/-/archive/v0.2.0/whirlpool_stats-v0.2.0.tar.gz',
  keywords=['bitcoin', 'privacy'],
  classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'License :: OSI Approved :: MIT License',
               'Natural Language :: English', 'Programming Language :: Python :: 3.4',
               'Topic :: Security'],
  cmdclass={'build_ext': build_ext},
  install_requires=[
    'PySocks',
    'requests[socks]',
    'plotly >= 4.1.0',
    'numpy >= 1.11.0',
    'datasketch'
  ]
)
