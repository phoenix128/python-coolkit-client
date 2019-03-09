import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coolkit-client-phoenix",
    version="1.0.2",
    author="Riccardo Tempesta",
    author_email="info@riccardotempesta.com",
    description="Sonoff control library through coolkit/ewelink cloud",
    long_description=long_description,
    url="https://github.com/phoenix128/python-coolkit-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
