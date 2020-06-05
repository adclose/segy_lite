import setuptools

long_description = open("README.md", "r").read()

setuptools.setup(
    name="segy_lite",
    version="0.0.2",
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
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)