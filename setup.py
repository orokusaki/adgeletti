#!/usr/bin/env python
from distutils.core import setup


# Dynamically calculate the version based on adgeletti.VERSION
version_tuple = __import__('adgeletti').VERSION
version = '.'.join([str(v) for v in version_tuple])

setup(
    name = 'adgeletti',
    description = """A truely plugable Django app, providing easy integration
    of Google DFP responsive-ready ad displaying into your website.""",
    version = version,
    author = 'Jeff.Ober and Michael.Angeletti @ CMG Digital [dot] com',
    url = 'http://github.com/orokusaki/adgeletti/',
    packages=['adgeletti'],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
