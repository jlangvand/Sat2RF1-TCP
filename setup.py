import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='groundstation-orbit',
    version='1.0a1',
    url='orbitntnu.com',
    license='GPLv3',
    author='Orbit NTNU',
    author_email='cmo@orbitntnu.com',
    description='Provides TCP sockets for satellite communication and ground station configuration',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8'
)
