from components.models.workspace import Workspace
from components.models.project import Project
from components.models.dataset import Dataset
import os, pytest, hashlib

cwd = None
w = None
p1,p2 = None, None
d1,d2 = None, None

def test_crete_dataset():
    # create the testing environment
    global cwd, w, p1, p2, d1, d2
    cwd = os.getcwd()
    w = Workspace("testWorkspace3", cwd)
    p1 = Project("testProject3", w.path, 1632527017.653542) # specify c_time for a static checksum of save.json
    p2 = Project("testProject4", w.path, 1632527130.789377)
    w.add_project(p1)
    w.add_project(p2)
    d1 = Dataset("testDataset1", p1.path)
    d2 = Dataset("testDataset2", p1.path)
    # test all attributes to make sure the objects were created properly
    assert d1.name == "testDataset1"
    assert d2.name == "testDataset2"
    assert d1.path == os.path.join(cwd, ".testWorkspace3", "testProject3", "testDataset1")
    assert d2.path == os.path.join(cwd, ".testWorkspace3", "testProject3", "testDataset2")
    assert d1.pcaps == []
    assert d2.pcaps == []
    assert d1.totalPackets == 0
    assert d2.totalPackets == 0
    assert d1.protocols == None
    assert d2.protocols == None
    # make sure the folders were created properly
    for d in [d1,d2]:
        assert os.path.isdir(os.path.join(cwd, ".testWorkspace3", "testProject3", d.name))
    assert p1.dataset == []

def test_add_dataset():
    global w, p1, p2, d1, d2
    # make sure datasets are properly linked to the project
    assert [d1] == p1.add_dataset(d1)
    assert [d1, d2] == p1.add_dataset(d2)
    assert p1.dataset == [d1, d2]
    assert p2.dataset == [] # make sure projects are not pointing to the same dataset array

def test_find_dataset():
    global w, p1, p2, d1, d2
    # funciton should return the dataset opject if the names match
    assert p1.find_dataset("testDataset1") == d1
    assert p1.find_dataset("testDataset2") == d2
    assert p1.find_dataset("testDataset3") == None
    assert p2.find_dataset("testDataset1") == None

def test_del_dataset():
    global w, p1, p2, d1, d2
    assert [d1] == p1.del_dataset(d2)
    assert p1.dataset == [d1]
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace3", "testProject3", "testDataset2"))

def test_save_dataset():
    global w, cwd
    w.save() # testing saving up to datasets
    # list of files that should be exported
    exported_files = [os.path.join(cwd, "testWorkspace3.zip"), os.path.join(cwd, ".testWorkspace3", "save.json")]
    # manually checked the save.json file was correct and calculated the checksum to the value below
    exported_hash = "5e4d477403a13e9bffcf448166de34b15d9d2709"
    for f in exported_files:
        # check files exist
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        # confirm checksum of save.json
        # would check for zip as well but the checksum keeps changing
        assert exported_hash == hashlib.sha1(data).hexdigest()

def test_save_dataset_overwrite():
    # make sure saving multiple times overwrites the previous save
    p1.add_dataset(d2)
    w.save()
    exported_files = [os.path.join(cwd, "testWorkspace3.zip"), os.path.join(cwd, ".testWorkspace3", "save.json")]
    # new checksum
    exported_hash = "0876378c9a9d907deeb5abc6661160f17d20c1ee"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()
    
    p1.del_dataset(d2)
    w.save()
    # back to old checksum
    exported_hash = "5e4d477403a13e9bffcf448166de34b15d9d2709"
    for f in exported_files:
        assert os.path.isfile(f)
    with open(exported_files[1], 'rb') as f:
        data = f.read()
        assert exported_hash == hashlib.sha1(data).hexdigest()

def test_del():
    global w
    del w
    with pytest.raises(NameError):
        print(w)
    # make sure when the workspace is deleted, nothing prevents the temp folder from being deleted
    assert not os.path.isdir(os.path.join(cwd, ".testWorkspace3"))