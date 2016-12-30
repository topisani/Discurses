# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    readme = f.read()

with open(path.join(here, 'LICENSE')) as f:
    license = f.read()

setup(
    name='discurses',
    version='0.2.4',
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
)
