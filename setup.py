# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='discurses',
    version='0.0.1',
    description='Discord CLI written in python, based on curses',
    long_description=readme,
    author='Topisani',
    author_email='topisani',
    url='https://github.com/topisani/discurses',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
