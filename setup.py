import os

from setuptools import setup


# Utility function to read the README file.
def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='stockBot',
    version='0.0.1',
    author='BFather',
    description=('stock bot for guoguo',),
    license='MIT',
    keywords='stock bot',
    url='https://github.com/',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    requires=['itchat>=1.3.9', 'bs4>=0.0.1', 'rx>=1.5.9', 'feedparser>=5.2.1']
)