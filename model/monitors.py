"""
Objekt bietet Referenz auf einen Prozess und ist in der Lage zu prüfen ob dieser läuft.
Via object.check_status() wird True (Prozess läuft) oder False (läuft nicht) zurückgegeben.
"""
import os
import re
import subprocess
import tempfile

import psutil

from model.dummy_listener import DummyListener
from model.tools import text_tools
from model.tools.system_tools import SystemTools
from model.tools.text_tools import TextTools, DATA_PATH


class ProcessMonitor:

    def __init__(self, target_proc):
        self.target_proc_name = None
        self.target_proc_id = None
        self.proc_running = False
        self.target_proc_name = target_proc

    def check_process_running(self):
        #print("DEBUG: checking process running")
        #print("DEBUG Running: " +  str(self.proc_running))
        try:
            if self.proc_running and psutil.pid_exists(self.target_proc_id):
                if psutil.Process(self.target_proc_id).name().lower() == self.target_proc_name.lower():
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            self.target_proc_id = None

        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == self.target_proc_name.lower():
                    #print("DEBUG: proc found")
                    self.target_proc_id = proc.pid
                    self.proc_running = True
                    return
                #print(f"DEBUG: proc {self.target_proc_name} not found : " + proc.info['name'])
            except Exception as e:
                #print("DEBUG: proc not found except")
                print(e)
                continue
        self.proc_running = False
        self.target_proc_id = None

    def get_state(self):
        self.check_process_running()
        return self.proc_running

class FileMonitor:
    proc_running = False

    target_file_path: str = None

    def __init__(self, target_file_path):
        self.target_file_path = target_file_path

    def read_status_file(self):
        if not os.path.exists(self.target_file_path):
            self.proc_running = False  # Standard, wenn noch nichts da ist
            return
        try:
            with open(self.target_file_path, 'r') as f:
                self.proc_running = (f.readline().strip() == "1")
        except Exception:
            self.proc_running = False

    def write_status_file(self, state: bool):
        folder = os.path.dirname(self.target_file_path)
        # 1. Temporäre Datei im selben Ordner erstellen
        fd, temp_path = tempfile.mkstemp(dir=folder, text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write("1" if state else "0")

            # 2. Die alte Datei atomar ersetzen
            # os.replace ist unter Windows seit Python 3.3 sicher
            os.replace(temp_path, self.target_file_path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"Fehler beim Schreiben: {e}")

    def get_state(self):
        self.read_status_file()
        return self.proc_running

    @staticmethod
    def scan_installed_monitors():
        return_files = []
        try:
            files = SystemTools.ls_files(DATA_PATH)
            return_files = [file.removesuffix(".txt") for file in files if text_tools.STATUS_FILE_PATTERN.match(file)]
        except FileNotFoundError:
            pass
        return return_files

if __name__ == "__main__":
    print(FileMonitor.scan_installed_monitors())


class PortController:

    def __init__(self, port, app_instance_id):
        self.target_port: int = port
        self.dummy_listener: DummyListener = DummyListener(port)
        self.monitor = None
        self.port_state = False
        self.app_instance_id: str = app_instance_id

    def control_port(self, status: bool):
        if status and status != self.port_state:
            self.open_port()
        elif not status and status != self.port_state:
            self.close_port()

    def open_port(self):
        self.manage_firewall(True)
        self.dummy_listener.start()
        #print("DEBUG: Dummy listener gestartet")
        self.port_state = True

    def close_port(self):
        self.manage_firewall(False)
        self.dummy_listener.stop()
        self.port_state = False

    def manage_firewall(self, open_port: bool):
        rule_name = self.app_instance_id
        if open_port:
            # Erstelle die Erlaubnis-Regel
            SystemTools.manage_firewall(rule_name, "allow", self.target_port)
        else:
            # Entferne die Regel komplett.
            # Ohne Regel ist der Port durch die Standard-Firewall-Policy automatisch wieder zu.
            subprocess.run(f'netsh advfirewall firewall delete rule name="{rule_name}"',
                           shell=True, capture_output=True)

    def stop(self):
        self.close_port()