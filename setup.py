from codecs import open as copen
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with copen(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyvstreamango',
    version='0.1.0',
    description='Python wrapper for streamango.com API',
    long_description=long_description,
    url='https://github.com/odysseusmax/PySteamango/',
    author='Christy Roys',
    author_email='royschristy@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['streamango', 'wrapper', 'api', 'api client'],
    packages=find_packages(exclude=['docs']),
    install_requires=['requests>=2.20.0', 'requests-toolbelt==0.9.1'],
)
