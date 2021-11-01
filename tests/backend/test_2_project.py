import hashlib
import os
import pytest

from packetvisualization.models.project import Project
from packetvisualization.models.workspace import Workspace

cwd = None
w = None
p1, p2 = None, None


def test_create_project():
    global w, cwd, p1, p2
    cwd = os.getcwd()
    w = Workspace("testWorkspace2", cwd)
    p1 = Project("testProject1", w.path, 1632527017.653542)
    p2 = Project("testProject2", w.path, 1632527130.789377)
    assert p1.name == "testProject1"
    assert p2.name == "testProject2"
    assert p1.c_time == 1632527017.653542
    assert p2.c_time == 1632527130.789377
    assert p1.size == 4096
    assert p2.size == 4096
    assert p1.dataset == []
    assert p2.dataset == []
    assert p1.path == os.path.join(cwd, ".testWorkspace2", "testProject1")
    for p in [p1, p2]:
        assert os.path.isdir(os.path.join(cwd, ".testWorkspace2", p.name))
    assert w.project == []


def test_add_project():
    global w, p1, p2
    assert [p1] == w.add_project(p1)
    assert [p1, p2] == w.add_project(p2)
    assert w.project == [p1, p2]


def test_find_project():
    global w, p1, p2
    assert w.find_project("testProject1") == p1
    assert w.find_project("testProject2") == p2
    assert w.find_project("testProject3") == None


def test_del_project():
    global w, p1, p2
    assert [p2] == w.del_project(p1)
    assert w.project == [p2]
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace2", "testProject1"))


def test_save_project():
    global w
    w.save()  # testing saving up to projects
    exported_files = [os.path.join(cwd, "testWorkspace2.zip"), os.path.join(cwd, ".testWorkspace2", "save.json")]
    exported_hash = "588a0a1700b334e9a2446e711c7aa4a5ffab2b70"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()


def test_save_project_overwrite():
    # make sure saving multiple times overwrites the previous save
    w.add_project(p1)
    w.save()
    exported_files = [os.path.join(cwd, "testWorkspace2.zip"), os.path.join(cwd, ".testWorkspace2", "save.json")]
    # new checksum
    exported_hash = "da244ac6526e58c02065a6c7994a814b61fdba91"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()

    w.del_project(p1)
    w.save()
    # back to old checksum
    exported_hash = "588a0a1700b334e9a2446e711c7aa4a5ffab2b70"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()


def test_del():
    global w, p1, p2
    del w
    with pytest.raises(NameError):
        print(w)
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace"))
