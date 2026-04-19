from view.tray_view import TrayView


class TrayViewController:
    def __init__(self, proc, port, callback_router):
        self.view = TrayView(self,
                             proc,
                             port,
                             callback_router.callback_tray_toggle,
                             callback_router.callback_tray_quit)

    def update_state(self, state: bool):
        self.view.update_state(state)

    def run(self):
        self.view.run()

    def stop(self):
        print("Tray View Controller stop")
        self.view.stop()