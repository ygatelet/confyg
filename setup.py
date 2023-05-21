from setuptools import setup
from confyg import __version__


with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name="confyg",
    version=__version__,
    description='Pydantic-based YAML configuration manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['confyg'],
    install_requires=[
        'pydantic>=1.9.2',
        'PyYAML>=6.0',
    ],
    url='https://github.com/ygatelet/confyg',
    classifiers=[
        'Private :: Do Not Upload',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Pydantic',
    ],
    python_requires='>=3.10',
)
