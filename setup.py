import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pinhole",
    version="0.0.1dev",
    author="Felipe Reyes",
    author_email="freyes@tty.cl",
    description="A photo manager on the cloud",
    keywords="web api photo manager",
    packages=find_packages(),
    install_requires=["flask", "flask-restful", "flask-sqlalchemy"],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)
