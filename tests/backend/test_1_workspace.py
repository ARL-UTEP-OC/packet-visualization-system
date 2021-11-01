import hashlib
import os
import pytest

from packetvisualization.models.workspace import Workspace

cwd = None
w = None


def test_create_workspace():
    global w, cwd
    cwd = os.getcwd()
    w = Workspace("testWorkspace1", cwd)
    assert w.name == "testWorkspace1"
    assert w.location == cwd
    assert w.project == []
    assert w.path == os.path.join(cwd, ".testWorkspace1")
    assert os.path.isdir(w.path)


def test_save_workspace():
    global w, cwd
    w.save()
    exported_files = [os.path.join(cwd, "testWorkspace1.zip"), os.path.join(cwd, ".testWorkspace1", "save.json")]
    exported_hash = "1e848eb62e7434c6f709c15ff8b48cef821edf1f"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()


def test_del():
    global w, cwd
    del w
    # Variable/access to the class should be gone
    with pytest.raises(NameError):
        print(w)
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace"))


def test_workspace_with_space():
    w = Workspace("This is my Workspace", "")
    w.save()
    exported_files = [os.path.join(cwd, "This is my Workspace.zip"),
                      os.path.join(cwd, ".This is my Workspace", "save.json")]
    exported_hash = "b8caec90a379a1e6e2deb08a2fd1d0b449025c3c"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()
    del w
