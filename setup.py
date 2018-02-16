#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: Get version in telops machines
    'matplotlib>=1.4.2,<2.0',
    # TODO: Get version in telops machines
    'numpy>=1.9.1',
]

extra_requirements = {
    # TODO: Get version in telops machines
    'telops': ["pyepics>=3.2.6"]
}

setup(
    name='star_pairs',
    version='0.1.0',
    description="Pick pairs of stars for Gemini nightly calibration",
    long_description=readme + '\n\n' + history,
    author="Manuel Gómez Jiménez",
    author_email='mgomez@gemini.edu',
    url='https://github.com/mgomezjimenez/star_pairs',
    packages=find_packages(include=['star_pairs']),
    entry_points={
        'console_scripts': [
            'star_pairs=star_pairs.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='star_pairs',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    extras_require=extra_requirements,
)
