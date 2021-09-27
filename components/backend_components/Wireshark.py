import os
import platform

def openwireshark(path):

    if(platform.system()=="Linux"):
        os.system('wireshark -r '+path)

    elif(platform.system()=="Windows"):
        os.system('cd "C:\Program Files\Wireshark" & wireshark -r '+path)
