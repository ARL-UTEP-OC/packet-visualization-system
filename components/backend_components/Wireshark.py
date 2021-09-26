import os

def openwireshark(path):
    os.system('cd "C:\Program Files\Wireshark" & wireshark -r '+path)
