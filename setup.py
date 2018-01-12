#!/usr/bin/env python3
from os import path
from os.path import join

from pip.req import parse_requirements
from setuptools import find_packages, setup

CWD = path.abspath(path.dirname(__file__))

with open(path.join(CWD, 'README.md')) as f:
    readme = f.read()

with open(path.join(CWD, 'LICENSE')) as f:
    license = f.read()


def requires():
    """Parse the requirements file and generate a requirements list."""
    install_reqs = parse_requirements(join(CWD, 'requirements', 'base.txt'),
                                      session=False)
    return [str(ir.req) for ir in install_reqs]


setup(
    name='discurses',
    version='0.2.5',
    description='Discord CLI written in python, based on urwid',
    long_description=readme,
    author='Topisani',
    author_email='topisani@hamsterpoison.com',
    url='https://github.com/topisani/discurses',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['urwid', 'discord.py', 'pyyaml'],
    entry_points={
        'console_scripts': [
            'discurses=discurses:main',
        ],
    },
    setup_requires=[
        'setuptools_scm'
    ],
)
