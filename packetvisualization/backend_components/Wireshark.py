import os
import platform
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget
from PyQt5 import QtWidgets

from packetvisualization.models.pcap import Pcap
from packetvisualization.models.workspace import Workspace


def openwireshark(path):
    if platform.system() == "Linux":

        subprocess.Popen(['wireshark', '-r', path])

    elif platform.system() == "Windows":

        subprocess.Popen("C:\Program Files\Wireshark\wireshark -r " + path)


# def exportToJson():
#     cwd = os.getcwd()
#     length = len(cwd)
#     start = length - 29
#
#     print(cwd[0:start])


def filter(path: str, wsFilter, newFileName, projectTree: QTreeWidget, workspace: Workspace):
    splitPath = path.split(os.sep)
    # splitPath = path.split("\\")
    datasetName = splitPath[len(splitPath) - 2]
    projectName = splitPath[len(splitPath) - 3]

    project = workspace.find_project(name=projectName)

    dataset = project.find_dataset(name=datasetName)

    splitPath[len(splitPath) - 1] = newFileName
    newFilePath = ""
    for i in splitPath:
        if i != splitPath[len(splitPath) - 1]:
            newFilePath += i + "\\"
        else:
            newFilePath += i

    cmd = r"C:\Program Files\Wireshark\tshark -r " + path + r' -w ' + newFilePath + '.pcap -Y '
    for key, value in wsFilter.items():
        cmd += f"\"{value}\""

        # if key == list(wsFilter.keys())[0]:
        #     cmd += f"\"{key} == {value}"
        # else:
        #     cmd += f"{key} == {value}"
        #
        # if key != list(wsFilter)[-1]:
        #     cmd += " && "
        # else:
        #     cmd += "\""

    # subprocess.Popen(cmd)
    print(cmd)
    error = subprocess.run(cmd, stderr=subprocess.PIPE)
    error = error.stderr.decode('utf-8')
    if not error:
        new_pcap = Pcap(file=newFilePath + ".pcap", path=dataset.path, name=newFileName + ".pcap")
        filterFolderExist = False
        dataset_item = projectTree.selectedItems()[0]
        for i in range(dataset_item.childCount()):
            if dataset_item.child(i).text(0) == "Wireshark Filtered Pcaps":
                filterFolderExist = True
                pcap_item = QtWidgets.QTreeWidgetItem()
                pcap_item.setText(0, newFileName + ".pcap")
                pcap_item.setData(0, Qt.UserRole, new_pcap)
                dataset_item.child(i).addChild(pcap_item)
                break
        if filterFolderExist == False:
            filterFolder = QtWidgets.QTreeWidgetItem()
            filterFolder.setText(0, "Wireshark Filtered Pcaps")
            dataset_item.addChild(filterFolder)
            pcap_item = QtWidgets.QTreeWidgetItem()
            pcap_item.setText(0, newFileName + ".pcap")
            pcap_item.setData(0, Qt.UserRole, new_pcap)
            filterFolder.addChild(pcap_item)

        # dataset_item.addChild(pcap_item)

        dataset.add_pcap(new=new_pcap)

    return error
