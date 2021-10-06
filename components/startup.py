from components.ui_components.startup_gui import Ui_startup_window
import components.models.context.database_context as _context
from components.models.context.entities import Dataset, Pcap

class Main():
    def __init__(self):
        _context.Base.metadata.create_all(bind=_context.engine, checkfirst=True)  

    def __del__(self):
        _context.session.close()

    def init_program():
        ui = Ui_startup_window()
        ui.run_program()
