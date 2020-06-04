import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="segy_lite", # Replace with your own username
    version="0.0.1",
    author="Aaron Close",
    author_email="aaron@gmail.com   ",
    description="Segy driver for multi cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adclose/segy_blob",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)