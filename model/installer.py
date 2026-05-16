import sys
import time

from model.tools import text_tools
from model.tools.system_tools import SystemTools
from model.tools.text_tools import TextTools, INSTALLED_PATH
import subprocess
import os
import shutil
import logging


class Installer:
    def __init__(self, proc, port):
        self.proc = proc
        self.port = port
        self.id = TextTools.generate_id(proc, port)
        self._flag_file_path = TextTools.get_stat_file_path(proc, port)
        self.target_exe_path = os.path.join(INSTALLED_PATH, "ProcPort.exe")

    def install(self):
        # Erkennen, ob wir als .exe oder .py laufen
        is_frozen = getattr(sys, 'frozen', False)

        if not is_frozen:
            return 2

        if self.check_newer():
            self.install_exe()

        self.setup_execution_and_start()

        return 0

    def install_exe(self):
        current_file = sys.executable
        target_path = INSTALLED_PATH
        target_exe_file = os.path.join(target_path, "ProcPort.exe")

        # 1. Verzeichnisse erstellen
        try:
            os.makedirs(target_path, exist_ok=True)
        except OSError as e:
            logging.error(f"Konnte Verzeichnis nicht erstellen: {e}")
            return

        # 2. Datei kopieren
        try:
            # Verhindert Fehler, falls Quelle und Ziel identisch sind
            if os.path.abspath(current_file) != os.path.abspath(target_exe_file):
                shutil.copy2(current_file, target_exe_file)
        except Exception as e:
            logging.error(f"Fehler beim Kopieren der .exe: {e}")
            return

        # 3. Berechtigungen (nur Windows)
        if sys.platform == "win32":
            try:
                # Benutze /grant:r für explizites Ersetzen/Hinzufügen
                subprocess.run(
                    ['icacls', target_path, '/grant', '*S-1-1-0:(OI)(CI)RX', '/T'],
                    capture_output=True,
                    check=True  # Wirft Fehler bei Returncode != 0
                )
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logging.warning(f"Rechte konnten nicht gesetzt werden: {e}")

    def check_newer(self):
        target_file = os.path.join(self.target_exe_path)

        # Wenn die Datei gar nicht existiert, ist der Installer definitiv "neuer"
        if not os.path.exists(target_file):
            return True

        try:
            # Extrahiere Versionen
            def get_version(path):
                result = subprocess.run([path, "--version"], capture_output=True, text=True, check=True)
                # Extrahiere nur die Versionsnummer (falls Text dabeisteht)
                return result.stdout.strip()

            installed_v_str = get_version(target_file)
            this_v_str = get_version(sys.executable)

            print(f"[*] Installed version: {installed_v_str}")
            print(f"[*] Installer version: {this_v_str}")

            # Simpler String-Vergleich (funktioniert nur bei festem Format wie YYYYMMDD)
            # Für SemVer (1.2.3) solltest du eine Hilfsfunktion nutzen
            return TextTools.is_version_newer(this_v_str, installed_v_str)

        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            logging.warning(f"Versionsprüfung fehlgeschlagen, erzwinge Update: {e}")
            return True


    def setup_execution_and_start(self):

        # 5. Flag-Datei erstellen (inklusive Ordnerpfad)
        if hasattr(self, '_flag_file_path') and not os.path.exists(self._flag_file_path):
            try:
                # Extrahiert den reinen Ordnerpfad aus dem Dateipfad
                folder_path = os.path.dirname(self._flag_file_path)

                # Erstellt alle notwendigen Zwischenordner, falls sie fehlen
                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)

                # 'x' erstellt die Datei, falls sie noch nicht vorhanden ist
                with open(self._flag_file_path, 'x') as f:
                    f.write('')  # Eine leere Datei schreiben
                print(f"[+] Instanz-Flag erstellt.")
            except Exception as e:
                print(f"[-] Fehler beim Erstellen der Flag-Datei oder des Ordners: {e}")

        # Pfade vorbereiten (basierend auf deiner Installer-Struktur)
        target_script = self.target_exe_path

        # Die Befehle für die Ausführung definieren
        # Backend: Läuft als SYSTEM (unsichtbar)
        cmd_base_back = f'\\"{target_script}\\" --backend --proc \\"{self.proc}\\" --port {self.port}'
        # Frontend: Läuft im User-Kontext
        cmd_base_front = f'\\"{target_script}\\" --frontend --proc \\"{self.proc}\\" --port {self.port}'

        # --- 1. AUFGABENPLANUNG (BACKEND) ---
        # Erstellt einen Task, der bei JEDEM Login als SYSTEM mit höchsten Rechten startet
        cmd_back_task = (
            f'schtasks /create /tn "ProcPort_Backend_{self.id}" '
            f'/tr "{cmd_base_back}" /sc ONLOGON /rl HIGHEST /ru SYSTEM /f'
        )
        subprocess.run(cmd_back_task, shell=True, capture_output=True)

        # --- 2. REGISTRY AUTOSTART (FRONTEND) ---
        # Trägt das Frontend in den HKLM-Run-Key ein (für alle Benutzer beim Login)
        cmd_reg_front = (
            f'reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run '
            f'/v "ProcPort_Frontend_{self.id}" /t REG_SZ /d "{cmd_base_front}" /f'
        )
        subprocess.run(cmd_reg_front, shell=True, capture_output=True)

        # --- 3. SOFORTIGER START ---
        print("[*] Starte Backend-Dienst via Task...")
        # Startet den gerade erstellten System-Task sofort
        subprocess.run(f'schtasks /run /tn "ProcPort_Backend_{self.id}"', shell=True, capture_output=True)

        print("[*] Starte Frontend-Prozess...")
        # Startet das Frontend direkt im aktuellen Benutzerkontext
        subprocess.Popen([target_script, "--frontend", "--proc", self.proc, "--port", str(self.port)])

    def uninstall(self):
        """
        Deinstalliert die Instanz. Beendet Prozesse via PowerShell mit korrektem Filter-Quoting.
        """
        print(f"[*] Deinstallation der Instanz {self.id} gestartet...")
        task_name = f"ProcPort_Backend_{self.id}"

        # 1. Backend-Prozess über die Aufgabenplanung stoppen
        subprocess.run(f'schtasks /end /tn "{task_name}"', shell=True, capture_output=True)

        # 2. Gezielter Abschuss via PowerShell (korrigiertes Quoting)
        # WICHTIG: Der Filter-String muss komplett in Anführungszeichen stehen: "Name = 'ProcPort.exe'"
        ps_kill_script = (
            f"Get-CimInstance Win32_Process -Filter \"Name = 'ProcPort.exe'\" | "
            f"Where-Object {{ $_.CommandLine -like '*--port {self.port}*' }} | "
            f"ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"
        )

        # Wir verpacken das Ganze in ein Kommando, das keine Probleme mit Sonderzeichen hat
        kill_cmd = ["powershell", "-NoProfile", "-Command", ps_kill_script]

        try:
            print(f"[*] Suche und stoppe Prozesse für Port {self.port}...")
            # Hier nutzen wir eine Liste statt shell=True für stabilere Argumentübergabe
            subprocess.run(kill_cmd, capture_output=True, text=True)
            print(f"[+] Prozess-Cleanup erfolgreich.")
        except Exception as e:
            logging.warning(f"Fehler beim Prozess-Cleanup: {e}")

        # 3. Aufgabenplanung (Backend) löschen
        try:
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, capture_output=True)
            print(f"[+] Task '{task_name}' entfernt.")
        except Exception:
            pass

        # 4. Registry Autostart (Frontend) löschen
        try:
            reg_path = r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            reg_value = f"ProcPort_Frontend_{self.id}"
            subprocess.run(f'reg delete "{reg_path}" /v "{reg_value}" /f', shell=True, capture_output=True)
            print(f"[+] Registry-Eintrag entfernt.")
        except Exception:
            pass

        # 5. Flag-Datei löschen
        if hasattr(self, '_flag_file_path') and os.path.exists(self._flag_file_path):
            try:
                os.remove(self._flag_file_path)
                print(f"[+] Instanz-Flag entfernt.")
            except Exception:
                pass

        print(f"[!] Deinstallation {self.id} fertig.")

if __name__ == "__main__":
    installer = Installer("a.exe", "1")
    print(installer.check_newer())


