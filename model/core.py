import time

from model.monitors import FileMonitor, ProcessMonitor, DummyListener, PortController
import re
import os
from threading import Thread

from model.tools.system_tools import SystemTools
from model.tools.text_tools import TextTools


class Core:

    def __init__(self, proc, port, mode, proc_state_change_callback=None):
        self.mode = mode
        self.modes = {
            "standalone": self.run_standalone,
            "frontend": self.run_frontend,
            "backend": self.run_backend,
        }
        if mode not in self.modes.keys():
            raise ValueError("Invalid mode")

        self.proc_state_change_callback = proc_state_change_callback
        self._proc = proc
        self._port = port
        self._id = TextTools.generate_id(self._proc, self._port)
        self._monitor = None
        self._port_controller = None
        self._file_controller = None
        self._loop_running = False

    def run(self):
        print("Starting Core...")
        self._loop_running = True
        action = self.modes[self.mode]
        action()

    def run_standalone(self):
        print("Core standalone!")
        self._monitor = ProcessMonitor(self._proc)
        self._port_controller = PortController(self._port, self._id)
        self._standalone_loop()

    def run_frontend(self):
        print("Core frontend!")
        self._monitor = FileMonitor(TextTools.get_stat_file_path(self._proc, self._port)) #Filepath
        self._frontend_loop()

    def run_backend(self):
        print("Core backend!")
        self._monitor = ProcessMonitor(self._proc)
        self._port_controller = PortController(self._port, self._id)
        self._file_controller = FileMonitor(TextTools.get_stat_file_path(self._proc, self._port))
        self._backend_loop()

    def _backend_loop(self):
        print("Core backend loop started!")
        last_known_status = None
        while self._loop_running:
            status = self._monitor.get_state()
            if status != last_known_status:
                self._port_controller.control_port(status)
                self._file_controller.write_status_file(status)
                last_known_status = status
            time.sleep(2)
        print("Core backend loop ended!")

    def _standalone_loop(self):
        last_known_status = None
        while self._loop_running:
            status = self._monitor.get_state()
            if status != last_known_status:
                self.proc_state_change_callback(status)
                self._port_controller.control_port(status)
                last_known_status = status
            time.sleep(2)
        print("Core standalone loop ended!")

    def _frontend_loop(self):
        last_known_status = None
        while self._loop_running:
            #print("Checking status file: " + TextTools.get_stat_file_path(self._proc, self._port))
            status = self._monitor.get_state()
            if status != last_known_status:
                self.proc_state_change_callback(status)
                last_known_status = status
            time.sleep(2)
        print("Core frontend loop ended!")

    def stop(self):
        print("Stopping Core...")
        self._loop_running = False
        if self._port_controller:
            self._port_controller.stop()
        self._monitor = None
        self._port_controller = None
