import argparse
import sys
import os
from threading import Thread, Event

from controller.callback_router import CallbackRouter
from controller.log_view_controller import LogViewController
from controller.main_view_controller import MainViewController
from controller.tray_view_controller import TrayViewController
from model.core import Core
from model.tools.system_tools import SystemTools
from model.tools.validate_tools import ValidateTools
import threading

class Main:
    version = "2.1"

    def __init__(self):
        self.proc = None
        self.port = None
        self.core = None
        self.log_view_controller = None
        self.main_view_controller = None
        self.tray_view_controller = None
        self.callback_router = None
        self.core_thread = None
        self.tray_view_thread = None
        self.exit_event = Event()

    def _controller_setup(self, proc, port):
        self.callback_router = CallbackRouter(self.exit_event)

        # 1 Controller Setup
        self.tray_view_controller = TrayViewController(proc, port, self.callback_router)
        self.callback_router.register_controller(tray=self.tray_view_controller)

        self.log_view_controller = LogViewController(proc, port, self.callback_router, self.exit_event)
        self.callback_router.register_controller(log=self.log_view_controller)

    def run_frontend(self, proc, port):
        self._controller_setup(proc, port)

        # 2 Core Setup
        self.core = Core(proc,
                    port,
                    "frontend",
                    proc_state_change_callback=self.callback_router.callback_proc_state_changed,)
        self.callback_router.register_controller(core=self.core)

        # 3 core im eigenen Thread
        self.core_thread = Thread(target=self.core.run, daemon=True)
        self.core_thread.start()

        self.tray_view_thread = Thread(target=self.tray_view_controller.run, daemon=True)
        self.tray_view_thread.start()

        self.log_view_controller.toggle()
        self.log_view_controller.run()
        print("Log View Controller ended")
        self.exit()


    def run_backend(self, proc, port):
        # 2 Core Setup
        self.core = Core(proc,
                         port,
                         "backend")
        #self.callback_router.register_controller(core=self.core)

        self.core.run()



    def run_standalone(self, proc, port):
        self._controller_setup(proc, port)

        #2 Core Setup
        self.core = Core(proc,
                    port,
                    "standalone",
                    proc_state_change_callback=self.callback_router.callback_proc_state_changed)
        self.callback_router.register_controller(core=self.core)

        #3 core im eigenen Thread
        core_thread = Thread(target=self.core.run, daemon=True)
        core_thread.start()

        tray_thread = Thread(target=self.tray_view_controller.run, daemon=True)
        tray_thread.start()

        self.log_view_controller.run()

        self.exit()

    def exit(self):
        self.tray_view_controller.stop()
        if self.tray_view_thread:
            self.tray_view_thread.join()
        self.core.stop()
        if self.core_thread:
            self.core_thread.join()
        print("ENDE")
        sys.exit(0)


    @staticmethod
    def run_gui():
        controller = MainViewController()
        controller.start()

if __name__ == '__main__':

    #argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action="store_true", help=argparse.SUPPRESS)
    parser.add_argument('--proc')
    parser.add_argument('--port')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--frontend", action="store_true", help=argparse.SUPPRESS)
    modes.add_argument("--backend", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.version:
        app = Main()
        print(app.version)
        sys.exit(0)

    if args.frontend and args.proc and ValidateTools.val_proc(args.proc) and args.port and ValidateTools.val_port(args.port):
        print("Starting frontend")
        app = Main()
        app.run_frontend(args.proc, args.port)

    if not SystemTools.is_admin():
        # ------> Adminstart
        # 1. Ermittle den Pfad zur ausführbaren Datei (Skript oder EXE)
        if getattr(sys, 'frozen', False):
            # Im EXE-Modus ist sys.executable der Pfad zur main.exe
            executable = sys.executable
            # Wir nehmen alle Argumente außer dem ersten (das ist der Dateiname selbst)
            arguments = sys.argv[1:]
        else:
            # Im Skript-Modus ist sys.executable der Python-Interpreter
            executable = sys.executable
            # Wir brauchen den Pfad zum Skript + die restlichen Argumente
            script_path = os.path.abspath(sys.modules['__main__'].__file__)
            arguments = [script_path] + sys.argv[1:]

        # 2. PARAMS zusammenbauen
        # Je nachdem, wie deine 'run_as_admin' Funktion aufgebaut ist,
        # erwartet sie meistens den Pfad zur EXE/Python und eine Liste an Strings.
        PARAMS = [executable] + arguments
        SystemTools.run_as_admin()

    elif args.backend and args.proc and ValidateTools.val_proc(args.proc) and args.port and ValidateTools.val_port(args.port):
        print("Starting backend")
        app = Main()
        app.run_backend(args.proc, args.port)

    elif args.proc and ValidateTools.val_proc(args.proc) and args.port and ValidateTools.val_port(args.port):
        print("Starting standalone")
        app = Main()
        app.run_standalone(args.proc, args.port)

    else:
        print("Starting GUI")
        Main.run_gui()