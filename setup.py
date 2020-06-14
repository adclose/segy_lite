import setuptools

long_description = open("README.md", "r").read()

setuptools.setup(
    name="segy_lite",
    version="0.0.4",
    author="Aaron Close",
    author_email="adclose@gmail.com",
    description="Lightweight SEGY Reading and Plotting Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['numpy', 'scipy', 'matplotlib', 'ibm2ieee', 'ebcdic', 'shapely', 'descartes'],
    url="https://github.com/adclose/segy_lite",
    packages=setuptools.find_packages(exclude='tests'),
    package_data={"": ["assets/*.json"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)