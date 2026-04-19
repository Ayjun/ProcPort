#4 Logik-Klassen
import socket
import threading

class DummyListener:
    def __init__(self, port):
        self.port = int(port)
        self.running = False
        self.sock = None

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        #print("DEBUG: run dummy listener")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.listen(5)
            while self.running:
                self.sock.settimeout(1.0)
                try:
                    client, _ = self.sock.accept()
                    client.close()
                except socket.timeout:
                    continue
                except OSError:
                    break
            self.sock = None
        except OSError as e:
            print("Port bereits belegt?")
            print(e)
        finally:
            self.running = False
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            self.sock = None


    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass