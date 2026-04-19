import sys
import time


class CallbackRouter:
    def __init__(self, exit_event=None):
        self.main_ctrl = None
        self.tray_ctrl = None
        self.log_ctrl = None
        self.core = None
        self.exit_event = exit_event

    def callback_proc_state_changed(self, state):
        print(f"Callback Proc State Changed: {state}")
        if self.tray_ctrl:
            self.tray_ctrl.update_state(state)

        if self.log_ctrl:
            self.log_ctrl.update_state(state)

    def callback_tray_toggle(self):
        print(f"Callback Tray Toggle!")
        if self.log_ctrl:
            print("Log Controller gefunden")
            self.log_ctrl.toggle()

    def callback_tray_quit(self):
        if self.exit_event:
            self.exit_event.set()

    def callback_log_onclick(self):
        if self.log_ctrl:
            pass

    def register_controller(self, main=None, tray=None, log=None, core=None):
        if main: self.main_ctrl = main
        if tray: self.tray_ctrl = tray
        if log: self.log_ctrl = log
        if core: self.core = core