import pystray
from model.tools.image_tools import ImageTools

class TrayView:
    def __init__(self, controller, proc, port, toggle_callback, quit_callback):
        self.controller = controller
        self.target_port = port
        self.target_proc = proc
        self.toggle_callback = toggle_callback
        self.quit_callback = quit_callback
        self.tray_icon = self.create_tray_icon(self.target_port, self.target_proc)

    def create_tray_icon(self, target_port, target_proc):
        # Startet initial mit Rot (wird sofort vom Monitor-Thread korrigiert)
        tray_icon = pystray.Icon("PortMonitor", ImageTools.create_status_image((255, 0, 0)),
                            title=f"Monitoring: {target_proc}\nPort: {target_port}")
        tray_icon.menu = pystray.Menu(
            pystray.MenuItem(f"Programm: {target_proc}", None, enabled=False),
            pystray.MenuItem(f"Port: {target_port}", None, enabled=False),
            pystray.MenuItem("Anzeigen / Verstecken", self.toggle, default=True),
            pystray.MenuItem("Beenden", lambda i, item: self.on_quit(i, item))
        )
        return tray_icon

    def update_state(self, is_active: bool):
        color = (0, 255, 0) if is_active else (255, 0, 0)
        self.tray_icon.icon = ImageTools.create_status_image(color)

    def toggle(self, icon, item):
        if self.toggle_callback:
            self.toggle_callback()

    def on_quit(self, icon, item):
        if self.quit_callback:
            self.quit_callback()

    def run(self):
        """Wird vom Controller aufgerufen, um den Loop zu starten."""
        self.tray_icon.run()

    def stop(self):
        """Wird vom Controller aufgerufen, um das Icon zu entfernen."""
        print("Stopping Tray View!")
        self.tray_icon.stop()
