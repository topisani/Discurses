#!/usr/bin/env python3
from os.path import dirname, join
from setuptools import find_packages, setup


INSTALL_REQUIRES = ['urwid', 'discord.py', 'pyyaml']

PROJECT_DIR = dirname(__file__)
README_FILE = join(PROJECT_DIR, 'README.rst')
ABOUT_FILE = join(PROJECT_DIR, 'src', 'discurses', '__about__.py')


def get_readme():
    with open(README_FILE) as fileobj:
        return fileobj.read()


def get_about():
    about = {}
    with open(ABOUT_FILE) as fileobj:
        exec(fileobj.read(), about)
    return about


ABOUT = get_about()

setup(
    name=ABOUT['__title__'],
    version=ABOUT['__version__'],
    description=ABOUT['__summary__'],
    long_description=get_readme(),
    author=ABOUT['__author__'],
    author_email=ABOUT['__email__'],
    url=ABOUT['__uri__'],
    license=ABOUT['__uri__'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            'discurses=discurses.__main__:main',
        ],
    },
    setup_requires=[
        'setuptools_scm'
    ],
    python_requires='>=3.6, <4',
    zip_safe=False,
)
