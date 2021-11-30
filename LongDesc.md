## Run
Once your changes are done and need to run the package as if you were a user of it. 
Follow these steps:
1. Run *pip install packet visualization*
2. Run *python*
3. Type
    ``` 
    from components.ui_components.startup_gui import Ui_startup_window
    ui = Ui_startup_window()
    ui.run_program()
    ```
## Requirements

1. Have a local mongo db server installed and running. The program uses this to create a local db instance.
2. Install wireshark

