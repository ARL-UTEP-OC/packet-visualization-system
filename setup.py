import setuptools

def readme():
    with open('README.md') as f:
        return f.read

setuptools.setup(
    name="packet-visualization",
    version="0.0.1",
    author="team-1",
    author_email="hbarrazalo@miners.utep.edu",
    description="packet visualization",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["components"],
    install_requires=[],
    include_package_data=True,
    python_requires=">=3.6",
)