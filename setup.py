from setuptools import setup
from webpage.__version__ import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="colibre_webpage",
    version=__version__,
    packages=["webpage", "webpage.html", "webpage.tree", "webpage.plots"],
    url="https://github.com/EvgeniiChaikin/colibre_webpage",
    license="MIT",
    author="Evgenii Chaikin",
    author_email="bowowoda@gmail.com",
    description="A package for arranging and visualising Colibre data",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy", "matplotlib"],
)
