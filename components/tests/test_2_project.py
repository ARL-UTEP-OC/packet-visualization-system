from components.models.workspace import Workspace
from components.models.project import Project
import os, pytest, hashlib

cwd = None
w = None
p1 = None
pw = None

def test_create_project():
    global w,cwd,p1,p2
    cwd = os.getcwd()
    w = Workspace("testWorkspace2", cwd)
    p1 = Project("testProject1", 12345678)
    p2 = Project("testProject2", 14687539)
    assert p1.name == "testProject1"
    assert p1.c_time == 12345678
    assert p1.size == 4096
    assert p1.dataset == []
    assert p1.path == os.path.join(cwd, ".testWorkspace2", "testProject1")
    for p in [p1,p2]:
        assert os.path.isdir(os.path.join(cwd, ".testWorkspace2", p.name))
    assert w.project == []

def test_add_project():
    global w,p1,p2
    w.add_project(p1)
    w.add_project(p2)
    assert w.project == [p1, p2]

def test_del_project():
    global w,p1,p2
    w.del_project(p1)
    assert w.project == [p2]
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace2", "testProject1"))

def test_save_project():
    global w
    w.save() # testing saving up to projects
    exported_files = [os.path.join(cwd, "testWorkspace2.zip"), os.path.join(cwd, ".testWorkspace2", "save.json")]
    exported_hash = "fe732eb8e3235464805c53d0dc9b4f0659d28401"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()

def test_del():
    global w,p1,p2
    del w
    with pytest.raises(NameError):
        print(w)
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace", "testProject1"))
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace", "testProject2"))
