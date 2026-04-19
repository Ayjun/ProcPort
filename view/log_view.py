import tkinter as tk
import os
from tkinter import scrolledtext
from tkinter import font as tkfont

class LogView:
    def __init__(self, controller, onclick_log_callback):
        self.controller = controller
        self.onclick_log_callback = onclick_log_callback

        self.root = tk.Tk()
        self.root.title("ProcPort Monitor")
        # Pfad zum Icon definieren
        icon_path = r"C:\Users\ericv\PycharmProjects\ProcPort\style\icon.ico"

        # Prüfen, ob die Datei existiert, um Fehler zu vermeiden
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # --- ABFANGEN DES SCHLIEßEN-BUTTONS ---
        # Statt das Fenster zu zerstören, rufen wir self.hide auf
        self.root.protocol("WM_DELETE_WINDOW", self.hide)

        # --- HACKER THEME KONFIGURATION ---
        self.bg_color = "#000000"  # Tiefschwarz
        self.fg_color = "#00FF00"  # Klassisches Matrix-Grün
        self.insert_color = "#00FF00"  # Farbe des Cursors

        # Versuche eine coole Monospace-Schriftart zu laden
        # 'Consolas' ist auf Windows super, 'Courier' ist der Klassiker.
        self.terminal_font = tkfont.Font(family="Consolas", size=10, weight="normal")

        # Fensterhintergrund setzen
        self.root.configure(bg=self.bg_color)
        self.root.geometry("800x400")  # Etwas größer für Terminal-Feeling

        # Option: Titelleiste entfernen für volles Fullscreen-Terminal-Feeling (ESC zum Schließen)
        # self.root.overrideredirect(True)

        # --- LOG TEXTFELD (TERMINAL) ---
        # Wir passen Farben, Schriftart und Relief an.
        self.log_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state="disabled",
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.insert_color,  # Cursor-Farbe
            font=self.terminal_font,
            relief="flat",  # Kein 3D-Rahmen
            borderwidth=0,
            highlightthickness=0  # Kein Fokus-Rahmen
        )


        # Padding hinzufügen, damit der Text nicht am Rand klebt
        self.log_area.pack(expand=True, fill="both", padx=10, pady=10)

    def write_log(self, text):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, f"{text}\n")
        self.log_area.configure(state="disabled")
        self.log_area.see(tk.END)

    def run(self):
        self.root.after(200, self.check_exit)
        self.root.mainloop()
        self.root.destroy()

    def stop(self):
        self.root.quit()

    def toggle(self):
        print("View toggles!")
        if self.root.state() == "normal":
            self.hide()
        else:
            self.show()

    def show(self):
        self.root.deiconify()
        self.root.lift()

    def hide(self):
        self.root.withdraw()

    def check_exit(self):
        if self.controller.check_exit():
            self.root.quit() # beendet mainloop sauber
            return
        self.root.after(200, self.check_exit)

if __name__ == '__main__':
    frontend_monitor_window = LogView(None)
    frontend_monitor_window.onclick_log_callback = lambda : frontend_monitor_window.write_log("Test")
    # Option: Wenn overrideredirect aktiv ist, brauchen wir einen Weg zum Schließen
    # frontend_monitor_window.root.bind("<Escape>", lambda e: frontend_monitor_window.root.destroy())
    frontend_monitor_window.root.mainloop()