# Systemwerkzeug
import ctypes
import os
import subprocess
import sys
from pathlib import Path

class SystemTools(object):
    PROGRAM_FILES = os.environ.get("ProgramFiles", "C:\\Program Files")
    PROGRAM_DATA = os.environ.get("ProgramData", "C:\\ProgramData")

    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    SW_HIDE, SW_SHOW = 0, 5

    @staticmethod
    def install_missing_packages(packages):
        for package in packages:
            try:
                __import__(package)
            except ImportError:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    @staticmethod
    def get_console_handle():
        return SystemTools.kernel32.GetConsoleWindow()

    @staticmethod
    def disable_quick_edit():
        h_input = SystemTools.kernel32.GetStdHandle(-10)
        mode = ctypes.c_uint()
        SystemTools.kernel32.GetConsoleMode(h_input, ctypes.byref(mode))
        SystemTools.kernel32.SetConsoleMode(h_input, mode.value & ~0x0040)

    @staticmethod
    def run_as_admin(params_list=None):
        # Wenn keine Liste übergeben wurde, nimm die aktuellen Argumente
        if params_list is None:
            params_list = sys.argv[1:]

        # Alle Parameter in Anführungszeichen setzen, um Leerzeichen-Probleme zu vermeiden
        params_string = " ".join([f'"{arg}"' for arg in params_list])

        if getattr(sys, 'frozen', False):
            # Fall: EXE
            executable = sys.executable
            arguments = params_string
        else:
            # Fall: Skript
            executable = sys.executable
            script = os.path.abspath(sys.argv[0])
            arguments = f'"{script}" {params_string}'

        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, arguments, None, 1)
        sys.exit(0)

    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            return os.getuid() == 0 if hasattr(os, 'getuid') else False

    @staticmethod
    def manage_firewall(rule_name, action, target_port):
        subprocess.run(f'netsh advfirewall firewall delete rule name="{rule_name}"', shell=True,
                       capture_output=True)
        cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action={action} protocol=TCP localport={target_port}'
        subprocess.run(cmd, shell=True, capture_output=True)

    @staticmethod
    # Gibt den Inhalt (nur Dateien, keine Unterordner) eines Ordners auf dem System als String list zurück
    def ls_files(path):
        try:
            folder = Path(path)
            files = [file.name for file in folder.iterdir() if file.is_file()]
        except (FileNotFoundError, OSError, PermissionError):
            files = []
        return files

if __name__ == "__main__":
    print(SystemTools.ls_files(".."))