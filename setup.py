import setuptools

setuptools.setup(
    name="packet-visualization",
    version="0.0.2",
    author="team-1",
    author_email="hbarrazalo@miners.utep.edu",
    description="packet visualization",
    url="https://gitlab.com/utep/packet-visualize",
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