#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'requests',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='langusta_client',
    version='0.1.0',
    description="Django application to push/pull translations from Langusta service",
    long_description=readme + '\n\n' + history,
    author="Vasyl Dizhak",
    author_email='vasyl.dizhak@moneypark.com',
    url='https://github.com/rootart/langusta_client',
    packages=[
        'langusta_client',
    ],
    package_dir={'langusta_client':
                 'langusta_client'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='langusta_client',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
