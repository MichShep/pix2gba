from setuptools import setup, find_packages

setup(
    name="gba_converter",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "img2gba.py = gba_converter.img2gba.py:main"
        ]
    },
    install_requires=[
        "numpy",
        "pillow"
    ],
)
