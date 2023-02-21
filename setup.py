#!/usr/bin/env python3
from setuptools import setup

def get_install_requires():
    """
    parse requirements.txt, ignore links, exclude comments
    """
    requirements = []
    for requirements_file in ('requirements.txt',):
        for line in open(requirements_file).readlines():
            line = line.rstrip()
            # skip to next iteration if comment or empty line
            if any([line.startswith('#'), line == '', line.startswith('http'), line.startswith('git'), line == '-r base.txt']):
                continue
            # add line to requirements
            requirements.append(line)
    return requirements

setup(
    name='tau2',
    packages=['tau2', 'tau2.bot', 'tau2.client', 'tau2.lib', 'tau2.server'],
    entry_points={
        'console_scripts': ['tau = tau2.client.main:main']
    },
    install_requires=get_install_requires(),
    author="tau developers",
    description="tau task management",
    keywords=['task management', 'tau', 'cli'],
    url='https://github.com/narodnik/tau2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    long_description="tau task management (centralized)"
)
