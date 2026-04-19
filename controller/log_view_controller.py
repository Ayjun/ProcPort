from controller.callback_router import CallbackRouter
from model.tools.text_tools import TextTools
from view.log_view import LogView

class LogViewController:
    def __init__(self, proc, port, callback_router, exit_event):
        self.proc = proc
        self.port = port
        self.callback_router = callback_router
        self.exit_event = exit_event
        self.log_view = LogView(self, callback_router.callback_log_onclick())

    def run(self):
        self.log_view.run()

    def stop(self):
        print("LogViewController.stop()")
        self.log_view.stop()

    def update_state(self, state):
        text = TextTools.create_proc_port_status_text(self.proc, self.port, state)
        self.log_view.write_log(text)

    def toggle(self):
        print("Controller toggles!")
        self.log_view.toggle()

    def check_exit(self):
        return self.exit_event.is_set()