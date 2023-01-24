import os
import sys
from setuptools import setup

assert sys.version_info >= (3, 8, 0), "This package requires Python 3.8"
assert sys.version_info < (3, 9, 0), "This package requires Python 3.8"

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, 'requirements.txt'), 'r', encoding='utf-8') as f:
    required = f.read().splitlines()

setup(install_requires=required)