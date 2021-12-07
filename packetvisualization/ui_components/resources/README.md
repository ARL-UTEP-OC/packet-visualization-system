# Adding Icons or Files
To add icons, images or other files, add the resource to the `resources.qrc` file following 
the format `<file alias="folder.svg">svg/folder.svg</file>`. In this example, the alias "folder.svg" 
is the name that will be called in your code using the format ":folder.svg". The "svg/folder.svg" is 
the path to the file. 

After all resources have been added, run the following command to create `qrc_resources.py`. Also run 
this command if a document being added changes to update:
```buildoutcfg
pyrcc5 -o qrc_resources.py resources.qrc
```

Finally, to use your document import the python package into the file you are working on, below
is an example of how to use the folder.svg icon.

```python
from PyQt5.QtGui import QIcon
from packetvisualization.ui_components.resources import qrc_resources

QIcon(":folder.svg")
```