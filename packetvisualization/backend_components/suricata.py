import os
import subprocess


def suricata(path_to_pcap):
    cwd = os.getcwd()
    print(cwd)

    splitPath = cwd.split(os.sep)
    # splitPath = path.split("\\")
    # datasetName = splitPath[len(splitPath) - 2]
    # projectName = splitPath[len(splitPath) - 3]

    # project = workspace.find_project(name=projectName)

    # dataset = project.find_dataset(name=datasetName)

    # splitPath[len(splitPath) - 1] = newFileName
    newFilePath = ""
    for i in range(0, 4):
        newFilePath += splitPath[i]
        if i < 3:
            newFilePath += "\\"


    print(newFilePath)
    os.chdir('C:/Program Files/Suricata')

    cmd = (fr"suricata -r {path_to_pcap} -l {newFilePath}")
    subprocess.Popen(cmd)

    os.chdir(cwd)
