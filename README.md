# Packet Visualization

## Steps to run
This project is developed under a virtual environment follow the next steps to manage packages and run the environment:
- Open the integrated terminal in your project **Note that you have to be in your project's path**
- Run *python3 -m venv venv*
- Run *source venv/bin/activate*
- To test the project as a package run *pip install -e packet-visualize*
- Try testing the package
***
## Dependencies

**To install dependencies in our project please follow these steps**
- To add dependencies use: *pip install your_dependency*
- To look at which dependencies we have in the project: *pip freeze*
- To push dependencies to file: *pip freeze > dev_requirements.txt*
- To install upcoming dependencies: *pip install -r dev_requirements.txt*
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
 
