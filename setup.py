import setuptools

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "LongDesc.md").read_text()

setuptools.setup(
    name="packetvisualization",
    version="1.0.0",
    author="team-1",
    author_email="hbarrazalo@miners.utep.edu",
    description="packet visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/utep/packet-visualize",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=['packetvisualization', 'packetvisualization.*'], exclude=["tests"]),
    install_requires=['pyshark', 'PyQt5', 'pandas', 'plotly', 'PyQtWebEngine', 'scapy', 'pymongo', 'python-decouple', 'certifi', 'liac-arff', 'sklearn'],
    include_package_data=True,
    python_requires=">=3.6",
)
