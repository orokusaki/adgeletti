#!/usr/bin/env python
from setuptools import setup, find_packages


# Dynamically calculate the version based on adgeletti.VERSION
version_tuple = __import__('adgeletti').VERSION
version = '.'.join([str(v) for v in version_tuple])

setup(
    name = 'adgeletti',
    description = ('A truely plugable Django app, providing easy integration '
                   'of Google GPT ad displaying into your website.'),
    version = version,
    author = 'Jeff Ober and Michael Angeletti',
    author_email = 'Jeff.Ober and Michael.Angeletti @ CMG Digital [dot] com',
    url = 'http://github.com/orokusaki/adgeletti/',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    packages=find_packages(),
)
