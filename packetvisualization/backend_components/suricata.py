import os
import platform
import subprocess
import traceback
from time import sleep

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget
from PyQt5 import QtWidgets

from packetvisualization.models.pcap import Pcap
from packetvisualization.models.workspace import Workspace


def suricata(path, projectTree: QTreeWidget, workspace: Workspace):
    splitPath = path.split(os.sep)

    datasetName = splitPath[len(splitPath) - 2]
    projectName = splitPath[len(splitPath) - 3]

    project = workspace.find_project(name=projectName)

    dataset = project.find_dataset(name=datasetName)

    newFileName = "suricataPcap"

    # splitPath[len(splitPath) - 1] = newFileName
    buggyNewFilePath = ""
    try:
        for i in range(0, len(splitPath) - 1):
            if i != splitPath[len(splitPath) - 1]:
                buggyNewFilePath += splitPath[i] + os.sep
            else:
                buggyNewFilePath += splitPath[i]
    except Exception:
        print(traceback.format_exc())

    newFilePath = buggyNewFilePath[: -1]

    cwd = os.getcwd()

    if platform.system() == "Windows":
        os.chdir('C:/Program Files/Suricata')
    cmd = f"suricata -r {path} -l {newFilePath}"
    error = subprocess.call(cmd, shell=True, stderr=subprocess.PIPE)

    os.chdir(cwd)

    searchPath = buggyNewFilePath

    for fname in os.listdir(path=searchPath):
        print(fname)
        if fname.startswith("log"):
            src = os.path.join(buggyNewFilePath, fname)
            dst = os.path.join(buggyNewFilePath, "suricataPcap.pcap")
            os.rename(src, dst)

    new_pcap = Pcap(file=buggyNewFilePath + newFileName + ".pcap", path=dataset.path, name=newFileName + ".pcap")

    filterFolderExist = False
    dataset_item = projectTree.selectedItems()[0]
    for i in range(dataset_item.childCount()):
        if dataset_item.child(i).text(0) == "Suricata Filtered Pcaps":
            filterFolderExist = True
            pcap_item = QtWidgets.QTreeWidgetItem()
            pcap_item.setText(0, newFileName + ".pcap")
            pcap_item.setData(0, Qt.UserRole, new_pcap)
            dataset_item.child(i).addChild(pcap_item)
            break
    if filterFolderExist == False:
        filterFolder = QtWidgets.QTreeWidgetItem()
        filterFolder.setText(0, "Suricata Filtered Pcaps")
        dataset_item.addChild(filterFolder)
        pcap_item = QtWidgets.QTreeWidgetItem()
        pcap_item.setText(0, newFileName + ".pcap")
        pcap_item.setData(0, Qt.UserRole, new_pcap)
        filterFolder.addChild(pcap_item)

    dataset.add_pcap(new=new_pcap)
