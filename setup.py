#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'sentry>=7.0.0',
    'BeautifulSoup>=3.2.1',
    'dicttoxml>=1.6.6',
]

f = open('README.rst')
readme = f.read()
f.close()

setup(
    name='sentry-unfuddle',
    version='1.0.1',
    author='Rick Keilty',
    author_email='rkeilty@gmail.com',
    url='http://github.com/rkeilty/sentry-unfuddle',
    description='A Sentry extension which creates Unfuddle issues from sentry events.',
    long_description=readme,
    license='BSD',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'sentry.apps': [
            'sentry_unfuddle = sentry_unfuddle',
            ],
        'sentry.plugins': [
            'sentry_unfuddle = sentry_unfuddle.plugin:UnfuddlePlugin'
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development'
    ],
)
