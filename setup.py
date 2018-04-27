from setuptools import setup
from os.path import join

def readme():
    with open('README.rst') as f:
        return f.read()

def requirements():
    with open('requirements.txt') as f:
        return f.read()

setup(name='papget',
      version='0.0',
      description='A small package for downloading papers from various sources',
      long_description=readme(),
      #url='https://github.com/tim6her/papget',
      author='Tim B. Herbstrith',
      license='MIT',
      packages=['papget'],
      install_requires=requirements(),
      scripts=[join('scripts', 'papget.py')],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
