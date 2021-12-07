# Packet Visualization

## Steps to run your virtual environment
This project is developed under a virtual environment follow the next steps to manage packages and run test mode:
- Open the integrated terminal in your project **Note that you have to be in your project's path**
- Run *python3 -m venv venv*
- Run *source venv/bin/activate*
***
## Run and debug package as a mock user
Once your changes are done and need to run the package as if you were a user of it. 
Follow these steps:
1. Open your command line interface.
2. Locate your self in our project's file path *cd your/path-to/packet-visualize*
3. Once in run: *pip install -e .*
4. You can now run *python* and test the package. 
5. Suggestion: The following is the way to run the system.
   1. import packetvisualization
   2. packetvisualization.run()
***
## Dependencies
We treat dependencies via dev_requirements.txt, which will install everything we need in order for the package to work.
Once you have pulled a new branch or going to start fresh please run *pip install -r dev_requirements.txt*

**To install dependencies in our project please follow these steps**
- Make sure your virtual env is running. Refer to **Steps to run**.
- Once in your venv, to install dependencies use: *pip install your_dependency*
- To check if your dependency has been installed run and find with: *pip freeze*
- To push dependencies to our file: *pip freeze > dev_requirements.txt*
- Must install suricata to use filter by suricata feature. After install, must modify
suricata.yaml file by searching for "log.pcap" and change enabled to "yes".
***
## Tests - Using PyTest
When creating a new test file, follow this naming convention test_*your_test*.py.
When creating a new test function, follow the same naming convention def test_*your_test_method*:

To run tests locally execute the following command on the project home folder: 
`python3 -m pytest`

**It is important to follow this step otherwise the test discovery will be broken**
***
## Setup.py
**NOTE: If we require the ones who use this packages to install dependencies please for our project to work add them to the install_requires property in the Setup.py file** 
***
## Performance Measurements
**Adding a Pcap/Dataset (Pcap size)**
- 9,000 KB ~10 seconds
- 20,000 KB ~90 seconds
- 360,000 KB ~11.5 minutes

**Generating Packet Table (Pcap size)**
- 20,000 KB ~15 seconds
- 360,000 KB ~70 seconds

**Export/View in Wireshark/Create Dataset from Table (ackets elected)**
- 5000 packets ~15 seconds
- 14,000 packets ~50 seconds
- 30,000 packets ~9.5 minutes
