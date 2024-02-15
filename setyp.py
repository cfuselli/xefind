from setuptools import setup, find_packages

setup(
    name='xefind',
    version='1.0.0',
    author='Carlo Fuselli',
    description='A fancy package to easily find XENONnT data available',
    packages=find_packages(),
    install_requires=[
        'utilix',
        'pandas',
        'os',
        'argparse'
    ],
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)