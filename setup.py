from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Fall Apart Pipeline'
LONG_DESCRIPTION = 'A Pipeline for fall apart.'

# Setting up
setup(
    name="fall_apart",
    version=VERSION,
    author="Fall Apart Team",
    author_email="<fallapart@artfx.fr>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['opencv-python', 'pyautogui', 'pyaudio', 'twine', 'setuptools'],
    keywords=['python', 'vfx', 'pipeline'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)