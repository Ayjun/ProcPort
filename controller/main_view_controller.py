import re
import subprocess
import sys
import os


from controller.callback_router import CallbackRouter
from controller.log_view_controller import LogViewController
from controller.tray_view_controller import TrayViewController
from model.installer import Installer
from model.tools.text_tools import TextTools
from model.tools.validate_tools import ValidateTools
from view.main_view import MainView
from model.monitors import FileMonitor
from model.core import Core
from threading import Thread

class MainViewController:
    def __init__(self):
        self.main_view = None
        self.proc = None
        self.port = None
        self.installed_monitors = FileMonitor.scan_installed_monitors()
        self.callback_router = CallbackRouter()
        self.is_frozen = getattr(sys, 'frozen', False)

    def start(self):
        if not self.main_view:
            self.main_view = MainView(self)

        view = self.main_view
        view.callback_start_button = self.main_view_start_button_action
        view.run()


    # Funktion wird aufgerufen wenn der start button im main window gedrückt wird,
    def main_view_start_button_action(self):
        data = self.main_view.get_user_input()

        if self._val_input(data):
            self.proc = data["proc"]
            self.port = data["port"]
            # 1. Ermittle den Pfad zur aktuellen Datei/EXE
            if getattr(sys, 'frozen', False):
                # Wenn als .exe gestartet: Nutze den Pfad der EXE selbst
                current_path = sys.executable
                cmd = [
                    current_path,
                    "--proc", data["proc"],
                    "--port", data["port"]
                ]
            else:
                # Wenn als Skript gestartet: Nutze Python-Interpreter + Pfad zum Skript
                # os.path.abspath(__file__) macht den Pfad unabhängig von deinem User-Namen
                current_path = os.path.abspath(sys.modules['__main__'].__file__)
                cmd = [
                    sys.executable,
                    current_path,
                    "--proc", data["proc"],
                    "--port", data["port"]
                ]

            if self.main_view.var_install.get():
                if not self.askyesno(f"ProcPort für Prozess {data['proc']} und Port {data['port']} fest installieren?"):
                    return
                installer = Installer(self.proc, self.port)
                installer.install()
            else:
                # 2. Prozess starten
                subprocess.Popen(cmd)

        else:
            self.main_view.alarm("Ungültige Eingabe!")

    def scan_installed_monitors(self):
        self.installed_monitors = FileMonitor.scan_installed_monitors()

    def update_installed_monitors(self):
        selected_element = self.main_view.get_list_selected_monitor()
        self.scan_installed_monitors()
        self.main_view.clear_installed_monitors()
        self.main_view.set_installed_monitors(self.installed_monitors)
        if selected_element:
            self.main_view.select_list_selected_monitor(selected_element)

    def _val_input(self, data):
        proc = data["proc"]
        port = data["port"]
        return ValidateTools.val_proc(proc) and ValidateTools.val_port(port)

    def run_standalone(self):
        #1 Controller Setup
        tray_view_controller = TrayViewController(self.proc, self.port, self.callback_router)
        self.callback_router.register_controller(tray=tray_view_controller)

        log_view_controller = LogViewController(self.proc, self.port, self.callback_router)
        self.callback_router.register_controller(log=log_view_controller)

        #2 Core Setup
        core = Core(self.proc,
                    self.port,
                    "standalone",
                    proc_state_change_callback=self.callback_router.callback_proc_state_changed)
        self.callback_router.register_controller(core=core)

        #3 core im eigenen Thread
        core_thread = Thread(target=core.run, daemon=True)
        core_thread.start()

        tray_thread = Thread(target=tray_view_controller.run, daemon=True)
        tray_thread.start()

        log_view_controller.run()

    def info(self, text):
        self.main_view.info(text)

    def alarm(self, text):
        self.main_view.alarm(text)

    def askyesno(self, text):
        return self.main_view.askyesno(text)

    def update_installed_monitors_list_loop(self):
        self.update_installed_monitors()
        self.main_view.root.after(5000, self.update_installed_monitors_list_loop)

    def handle_uninstall_button(self):
        selection = self.main_view.get_list_selected_monitor()

        # Falls nichts ausgewählt ist, direkt abbrechen
        if not selection:
            return

        # 1. Hol den Index (die Zahl)
        selected_index = selection[0]

        # 2. Hol den TEXT aus der Listbox der View (WICHTIG!)
        # Hierfür greifen wir auf das Listbox-Objekt der View zu und nutzen .get()
        raw_id_string = self.main_view.installed_monitors_list.get(selected_index)

        # 3. Jetzt dekodieren (raw_id_string ist ein String, z.B. "proc.exe_80")
        proc, port = TextTools.decode_id(raw_id_string)

        # 4. Sicherheitsabfrage (Benutze proc und port für eine klare Nachricht)
        if self.askyesno(f"Möchtest du {proc} (Port {port}) wirklich deinstallieren?"):
            installer = Installer(proc, port)
            installer.uninstall()


if __name__ == "__main__":
    controller = MainViewController()
    controller.start()



