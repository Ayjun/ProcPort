from datetime import datetime
import os
import re

from model.tools.system_tools import SystemTools

INSTALLED_PATH = os.path.join(SystemTools.PROGRAM_FILES, "ProcPort")
DATA_PATH = os.path.join(SystemTools.PROGRAM_DATA, "ProcPort")
STATUS_FILE_PATTERN = re.compile(r"^(.+\.exe_\d+)\.txt$")

class TextTools():
    @staticmethod
    def create_proc_port_status_text(proc, port, state: bool):
        text = ""
        dt = datetime.now()
        ts = dt.strftime("%Y-%m-%d %H:%M:%S")
        if state:
            text = f"{ts} [+] {proc} gefunden, {port} offen!"
        else:
            text = f"{ts} [-] {proc} nicht gefunden, {port} geschlossen!"
        return text

    @staticmethod
    def generate_id(proc, port):
        return f"{re.sub(r'[^\w.]', '_', proc)}_{port}"

    @staticmethod
    def decode_id(id_str):
        # rsplit("_", 1) teilt den String nur am LETZTEN Unterstrich auf.
        # Das schützt den Prozessnamen, falls dieser selbst Unterstriche enthält.
        parts = id_str.rsplit("_", 1)
        if len(parts) == 2:
            print(parts[0].strip(), parts[1].strip())
            return parts[0].strip(), parts[1].strip()
        return parts[0], ""  # Fallback, falls kein Port gefunden wurde

    @staticmethod
    def get_stat_file_path(proc, port):
        return f"{DATA_PATH}\\{TextTools.generate_id(proc, port)}.txt"

    @staticmethod
    def is_version_newer(current_v_str, installed_v_str):
        """
        Vergleicht zwei Versionsstrings (z.B. '1.2.3' vs '1.10.0').
        Gibt True zurück, wenn current_v_str neuer ist als installed_v_str.
        """
        try:
            # Extrahiere nur Zahlen (hilft, wenn 'v1.2.3' oder 'Version 1.2' übergeben wird)
            def parse_version(v):
                # Entferne alles außer Ziffern und Punkte, dann splitten
                clean_v = ''.join(c for c in v if c.isdigit() or c == '.')
                return [int(part) for part in clean_v.split('.') if part]

            v_current = parse_version(current_v_str)
            v_installed = parse_version(installed_v_str)

            # Python kann Listen von Integern direkt vergleichen: [1, 10] > [1, 2] -> True
            return v_current > v_installed

        except (ValueError, AttributeError):
            # Falls das Format totaler Quatsch ist, gehen wir sicherheitshalber von "Update nötig" aus
            return True

if __name__ == "__main__":
    print(TextTools.get_stat_file_path("cmd.exe", 42))