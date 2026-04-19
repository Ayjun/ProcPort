import re

class ValidateTools:
    @staticmethod
    def val_port(port):
        if re.match(r"^\d+$", port):
            if 0 <= int(port) <= 65535:
                return True
        return False  # Wichtig: immer ein explizites False am Ende

    @staticmethod
    def val_proc(proc):
        proc_pattern = r"^.+\.exe$"
        if re.match(proc_pattern, proc):
            return True
        return False