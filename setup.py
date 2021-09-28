import setuptools

setuptools.setup(
    name="packetvisualization",
    version="0.0.1",
    author="team-1",
    author_email="hbarrazalo@miners.utep.edu",
    description="packet visualization",
    url="https://gitlab.com/utep/packet-visualize",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=['packet-visualize', 'packet-visualize.*'],exclude=["tests"]),
    install_requires=[],
    include_package_data=True,
    python_requires=">=3.6",
)