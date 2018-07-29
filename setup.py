import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pygdrive3",
    version="0.5.2",
    author="Matheus Almeida",
    author_email="mat.almeida@live.com",
    description="Use Google Drive API v3 with a python interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matalmeida/pygdrive3",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license="MIT"
)
