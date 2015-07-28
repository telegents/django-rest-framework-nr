#!/bin/bin/env python

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

setup(
    name='djangorestframework-ipglobal',
    version='0.1.1',
    description='Provide nested router and Authorize Stormpath token  access to Django REST framework resources',
    url='https://github.com/ipglobal/djangorestframework-stormpath',
    author='Jarrod Baumann',
    author_email='jarrod@unixc.org',
    license='MIT',
    keywords='djangorestframework stormpath',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['PyJWT', 'requests'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP', 
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Web Environment',
        'Framework :: Django',
    ]
)

