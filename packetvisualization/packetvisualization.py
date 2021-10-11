from packetvisualization.ui_components.startup_gui_redesign import StartupWindow
import packetvisualization.models.context.database_context as _context
#from packetvisualization.models.context.entities import Dataset, Pcap

def run():
    _context.Base.metadata.create_all(bind=_context.engine, checkfirst=True)
    ui = StartupWindow()
    ui.run_program()