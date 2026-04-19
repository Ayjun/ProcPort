# ProcPort – Network Tracking Bridge

Choose your language / Wählen Sie Ihre Sprache:
* [English](#english)
* [Deutsch](#deutsch)

---

## <a name="english"></a> 🇺🇸 ENGLISH: ProcPort – Network Tracking Bridge

**ProcPort** is a utility for Windows designed to ensure the visibility of local applications for network monitoring software (e.g., PRTG, Checkmk, Zabbix). It functions as a **beacon** by opening a specific port as soon as a monitored process is active.

### 🎯 Purpose
Many monitoring solutions verify software availability via TCP port queries. If a program:
* Does not open a network port itself,
* Runs only sporadically,
* Is located behind a restrictive local firewall,

...it cannot be reliably tracked by network monitoring. **ProcPort** solves this by monitoring the status of the process and, upon activity, opening a "dummy port" and activating the corresponding firewall rule.

### 🚀 Core Features
* **Process-to-Port Mapping:** Links the existence of a Windows process (e.g., `backup-tool.exe`) to a freely selectable TCP port (e.g., `9001`).
* **Automated TCP Listener:** Starts a resource-efficient socket server that responds to requests from monitoring software.
* **Dynamic Firewall Punching:** Automatically creates and removes the necessary "allow" rules in the Windows Firewall via `netsh`.
* **System Integration:** Can be installed as a persistent background service (backend) that runs independently of user login.
* **Status Visualization:** A tray icon informs the local user of the current tracking status (**Green** = Process active / Port open).

### 📖 Installation & Usage
**Prerequisites:**
> [!CAUTION]
Use the Compiled Executable Only:
You must use the pre-compiled .exe (generated via PyInstaller) found in the Releases section of this repository. The source code contains strict environment filters; therefore, installation and background service features will not function when running directly from the .py script.
* Windows 10/11 or Windows Server.
* Administrator rights (required for firewall control and service installation).

**Quick Start (GUI):**
Run the `.exe` to launch the graphical user interface.

> [!IMPORTANT]
> **Regarding Permanent System Rule Installation:**
> For simplicity, the `.exe` automatically copies itself to `PROGRAM_FILES\ProcPort` (typically `C:\Program Files\ProcPort`) when a permanent rule is first installed.
>
> Additionally, the following are created for each installed monitoring task (removable via the "Uninstall" button in the GUI):
> * **Backend Task:** `\Microsoft\Windows\TaskScheduler\ProcPort_Backend_...`
> * **Autostart Key:** `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
> * **Status Flags:** `C:\ProgramData\[App Name]\...`

**Note:** This tool is designed as a bridge for monitoring purposes and should not be used to bypass network security policies without consulting IT administration.

---

## <a name="deutsch"></a> 🇩🇪 DEUTSCH: ProcPort – Network Tracking Bridge

**ProcPort** ist ein Hilfswerkzeug für Windows, das die Sichtbarkeit von lokalen Anwendungen für Netzwerk-Monitoring-Software (z. B. PRTG, Checkmk, Zabbix) sicherstellt. Es fungiert als **Signalfeuer (Beacon)**, indem es einen spezifischen Port öffnet, sobald ein zu überwachender Prozess aktiv ist.

### 🎯 Einsatzzweck
Viele Monitoring-Lösungen prüfen die Verfügbarkeit von Software über TCP-Port-Abfragen. Wenn ein Programm:
* Selbst keinen Netzwerk-Port öffnet,
* Nur sporadisch läuft,
* Hinter einer restriktiven lokalen Firewall liegt,

...kann es vom Netzwerk-Monitoring nicht zuverlässig getrackt werden. **ProcPort** löst dies, indem es den Status des Prozesses überwacht und bei Aktivität einen "Dummy-Port" öffnet sowie die passende Firewall-Regel schaltet.

### 🚀 Kernfunktionen
* **Prozess-zu-Port Mapping:** Verknüpft die Existenz eines Windows-Prozesses (z.B. `backup-tool.exe`) mit einem frei wählbaren TCP-Port (z.B. `9001`).
* **Automatisierter TCP-Listener:** Startet einen ressourcenschonenden Socket-Server, der auf Anfragen von Monitoring-Software reagiert.
* **Dynamic Firewall Punching:** Erstellt und entfernt automatisch die notwendigen allow-Regeln in der Windows-Firewall via `netsh`.
* **System-Integration:** Kann als persistenter Hintergrunddienst (Backend) installiert werden, der unabhängig von der Benutzeranmeldung läuft.
* **Status-Visualisierung:** Ein Tray-Icon informiert den lokalen Nutzer über den aktuellen Tracking-Status (**Grün** = Prozess aktiv / Port offen).

### 📖 Installation & Nutzung
**Voraussetzungen:**
> [!CAUTION]
WICHTIG: Nur die kompilierte .exe verwenden:
Für den Betrieb muss zwingend die im Repo unter Releases bereitgestellte, mit PyInstaller generierte .exe verwendet werden. Da der Code interne Abfragen auf den "Frozen"-Status nutzt, sind die Installations-Routinen und Hintergrund-Dienste im Skript-Modus (.py) deaktiviert und funktionieren dort nicht.
* Windows 10/11 oder Windows Server.
* Administratorrechte (zur Steuerung der Firewall und Installation von Diensten).

**Schnellstart (GUI):**
Starte die `.exe`, um die grafische Oberfläche zu öffnen.

> [!IMPORTANT]
> **ACHTUNG: Im Falle von fester Installation von Regeln auf dem System:**
> Aus Gründen der Einfachheit kopiert sich die `.exe` bei der erstmaligen Installation einer festen Regel selbstständig nach `PROGRAM_FILES\ProcPort` (normalerweise `C:\Programme\ProcPort`).
>
> Außerdem wird pro fest installierter Überwachung Folgendes angelegt (kann per "Deinstallieren"-Button im GUI wieder entfernt werden):
> * **Backend-Task:** `\Microsoft\Windows\TaskScheduler\ProcPort_Backend_...` (Windows Aufgabenplanung)
> * **Autostart-Key:** `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
> * **Status-Flags:** `C:\ProgramData\[Name der App]\...`

**Hinweis:** Dieses Tool ist als Brücke für Monitoring-Zwecke konzipiert und sollte nicht dazu verwendet werden, Sicherheitsrichtlinien des Netzwerks ohne Rücksprache mit der IT-Administration zu umgehen.
