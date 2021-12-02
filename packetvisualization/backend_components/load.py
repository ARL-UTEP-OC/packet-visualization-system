import json
import os
import shutil
import traceback

import pandas as pd

from packetvisualization.models.analysis import Analysis
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap
from packetvisualization.models.project import Project
from packetvisualization.models.workspace import Workspace


class Load:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def open_zip(self, path: str) -> None:
        try:
            if not os.path.isfile(path):
                raise Exception
            root, ext = os.path.splitext(path)
            if ext.lower() != ".zip":
                raise Exception
            head, tail = os.path.split(root)
            tail = "." + tail
            working_dir = os.path.join(head, tail)
            if os.path.isdir(working_dir):
                shutil.rmtree(working_dir)
            shutil.unpack_archive(path, working_dir)
            self.load_workspace(working_dir)
        except Exception:
            print("Error while trying to read ZIP file.")
            traceback.print_exc()
            return None

    def open_dir(self, path: str) -> None:
        try:
            if not os.path.isdir(path):
                raise Exception
            head, tail = os.path.split(path)
            tail = "." + tail
            working_dir = os.path.join(head, tail)
            if os.path.isdir(working_dir):
                shutil.rmtree(working_dir)
            shutil.copytree(path, working_dir)
            self.load_workspace(working_dir)

        except Exception:
            print("Error while trying to read directory.")
            traceback.print_exc()
            return None

    def load_workspace(self, path: str) -> None:
        try:
            head, tail = os.path.split(path)
            with open(os.path.join(path, 'save.json')) as f:
                data = f.read()
            w = json.loads(data)
            # w = Workspace(js['name'], head, open_existing=True)
            self.load_project(w['project'])
        except FileNotFoundError:
            print("Specified ZIP or directory does not contain a save file.")
            shutil.rmtree(path)
            traceback.print_exc()
            return None
        except Exception:
            print("Unable to read save file. File may be corrupted.")
            shutil.rmtree(path)
            traceback.print_exc()
            return None

    def load_project(self, projects: list) -> None:
        for p in projects:
            proj = Project(p['name'], self.workspace.path, p['c_time'])
            self.load_dataset(proj, p['dataset'])
            self.load_analysis(proj, p['analysis'])
            self.workspace.add_project(proj)

    def load_dataset(self, project: Project, datasets: list) -> None:
        for d in datasets:
            data = Dataset(d['name'], project.path, d['m_data'])
            self.load_pcap(data, d['pcaps'])
            project.add_dataset(data)

    def load_analysis(self, project: Project, analysis: list) -> None:
        try:
            for a in analysis:
                csv_path = os.path.join(project.path, a['name'] + ".csv")
                df = pd.read_csv(csv_path)
                anal = Analysis(a['name'], df, a['features'], project.path, a['origin'], a['m_data'])
                project.add_analysis(anal)
        except Exception:
            traceback.print_exc()

    def load_pcap(self, dataset: Dataset, pcaps: list) -> None:
        for a in pcaps:
            pcap = Pcap(a['name'], dataset.path, os.path.join(dataset.path, a['name']))
            dataset.add_pcap(pcap)
