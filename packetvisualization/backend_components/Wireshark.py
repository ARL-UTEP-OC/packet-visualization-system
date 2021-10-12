import os
import platform
import subprocess

from PyQt5.QtWidgets import QTreeWidget
from PyQt5 import QtWidgets

from packetvisualization.models.pcap import Pcap
from packetvisualization.models.workspace import Workspace


def openwireshark(path):

    if(platform.system()=="Linux"):

        subprocess.Popen('wireshark -r '+path)

    elif(platform.system()=="Windows"):

        subprocess.Popen("C:\Program Files\Wireshark\wireshark -r " + path)
        print(path)


def exportToJson():
    cwd = os.getcwd()
    length = len(cwd)
    start = length - 29

    print(cwd[0:start])


def filter(path: str, wsFilter, newFileName, projectTree: QTreeWidget, workspace: Workspace):

    splitPath = path.split("\\")
    datasetName = splitPath[len(splitPath) - 2]
    projectName = splitPath[len(splitPath) - 3]

    print(projectName)
    project = workspace.find_project(name=projectName)

    dataset_item = projectTree.selectedItems()[0]
    pcap_item = QtWidgets.QTreeWidgetItem()
    pcap_item.setText(0, newFileName+".pcap")
    dataset_item.addChild(pcap_item)

    print(datasetName)
    dataset = project.find_dataset(name=datasetName)

    print(splitPath)
    splitPath[len(splitPath) - 1] = newFileName
    newFilePath = ""
    for i in splitPath:
        if i != splitPath[len(splitPath) - 1]:
            newFilePath += i + "\\"

        else:
            newFilePath += i

    print(newFilePath)

    # cmd = r"C:\Program Files\Wireshark\tshark -r "+path+r' -w C:\Users\timmy\Downloads\filteredPcap.pcap -Y '
    cmd = r"C:\Program Files\Wireshark\tshark -r " + path + r' -w ' + newFilePath + '.pcap -Y '
    for key, value in wsFilter.items():
        print(f"{key}: {value}")

        if key == list(wsFilter.keys())[0]:
            cmd += f"\"{key} == {value}"
        else:
            cmd += f"{key} == {value}"

        if key != list(wsFilter)[-1]:
            cmd += " && "
        else:
            cmd += "\""
    print(cmd)
    #subprocess.Popen(cmd)
    subprocess.call(cmd)

    new_pcap = Pcap(file=newFilePath+".pcap", path=dataset.path, name=newFileName + ".pcap")
    dataset.add_pcap(new=new_pcap)

    print(dataset.pcaps[1].path)
    print(dataset.pcaps[1].path)

    #subprocess.Popen(r"C:\Program Files\Wireshark\tshark -r "+path+r' -w C:\Users\timmy\Downloads\filteredPcap.pcap -Y "ip.src == 172.16.11.12"')

