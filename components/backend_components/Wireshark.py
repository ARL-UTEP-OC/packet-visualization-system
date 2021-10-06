import os
import platform
import subprocess

def openwireshark(path):

    if(platform.system()=="Linux"):

        subprocess.Popen('wireshark -r '+path)

    elif(platform.system()=="Windows"):

        subprocess.Popen("C:\Program Files\Wireshark\wireshark -r " + path)

