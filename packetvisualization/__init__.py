def run():
    from packetvisualization.ui_components.startup_gui_redesign import StartupWindow
    import packetvisualization.models.context.database_context as _context
    # from packetvisualization.backend.context.entities import Dataset, Pcap

    ui = StartupWindow()
    ui.run_program()
