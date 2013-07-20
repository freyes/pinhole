import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pinhole",
    version="0.1.0dev",
    author="Felipe Reyes",
    author_email="freyes@tty.cl",
    description="A photo manager on the cloud",
    keywords="web api photo manager",
    packages=find_packages(),
    test_suite = 'nose.collector',
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
    entry_points = """
    [console_scripts]
    pinhole-syncdb = pinhole.bin.sync_db:main
    """
)
