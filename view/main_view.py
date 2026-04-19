import tkinter as tk
import os
from tkinter import messagebox
import weakref


class MainView:
    def __init__(self, main_view_controller, callback_start_button=None):
        self.main_view_controller = weakref.ref(main_view_controller) if main_view_controller else lambda: None
        self.callback_start_button = callback_start_button

        # --- SERIÖSE DARK-MODE FARBPALETTE (JETZT IN GRÜN) ---
        self.bg_main = "#1e1e1e"  # Dunkles Anthrazit
        self.bg_secondary = "#252526"  # Etwas helleres Grau für Felder
        self.fg_main = "#ffffff"  # Weiß für Texte
        self.accent_green = "#28a745"  # Sattes, seriöses Grün
        self.accent_red = "#f44747"  # Sanftes Rot
        self.font_main = ("Segoe UI", 10)
        self.font_bold = ("Segoe UI", 10, "bold")

        self.root = tk.Tk()
        # Pfad zum Icon definieren
        icon_path = r"C:\Users\ericv\PycharmProjects\ProcPort\style\icon.ico"

        # Prüfen, ob die Datei existiert, um Fehler zu vermeiden
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        self.root.title("ProcPort")
        self.root.geometry("620x330")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg=self.bg_main)

        # Main Container
        self.container = tk.Frame(self.root, bg=self.bg_main, padx=20, pady=15)
        self.container.pack(fill="both", expand=True)

        # --- OBEN: CONTENT (LINKS & RECHTS) ---
        self.content_frame = tk.Frame(self.container, bg=self.bg_main)
        self.content_frame.pack(fill="both", expand=True)

        # LINKE SEITE (Konfiguration)
        self.left_box = tk.Frame(self.content_frame, bg=self.bg_main)
        self.left_box.pack(side="left", anchor="n", padx=(0, 20))

        tk.Label(self.left_box, text="Prozess Name", bg=self.bg_main, fg=self.accent_green, font=self.font_bold).pack(
            anchor="w", pady=(0, 2))
        self.entry_process = tk.Entry(self.left_box, width=28, bg=self.bg_secondary, fg=self.fg_main,
                                      insertbackground=self.fg_main, borderwidth=0, font=self.font_main)
        self.entry_process.pack(pady=(0, 15), ipady=3)

        tk.Label(self.left_box, text="Port", bg=self.bg_main, fg=self.accent_green, font=self.font_bold).pack(
            anchor="w", pady=(0, 2))
        self.entry_port = tk.Entry(self.left_box, width=28, bg=self.bg_secondary, fg=self.fg_main,
                                   insertbackground=self.fg_main, borderwidth=0, font=self.font_main)
        self.entry_port.pack(pady=(0, 15), ipady=3)

        self.var_install = tk.BooleanVar()
        self.cb_install = tk.Checkbutton(
            self.left_box, text="Permanent installieren", variable=self.var_install,
            bg=self.bg_main, fg=self.fg_main, selectcolor=self.bg_secondary,
            activebackground=self.bg_main, activeforeground=self.accent_green,
            font=self.font_main, bd=0, highlightthickness=0
        )
        self.cb_install.pack(anchor="w")

        # RECHTE SEITE (Liste)
        self.right_box = tk.Frame(self.content_frame, bg=self.bg_main)
        self.right_box.pack(side="right", fill="both", expand=True)

        tk.Label(self.right_box, text="Installierte Überwachungen", bg=self.bg_main, fg=self.fg_main,
                 font=self.font_bold).pack(anchor="w", pady=(0, 5))

        self.list_frame = tk.Frame(self.right_box, bg=self.bg_secondary)
        self.list_frame.pack(fill="both", expand=True)

        # activestyle="none" entfernt die Unterstreichung des ausgewählten Elements
        self.installed_monitors_list = tk.Listbox(
            self.list_frame, bg=self.bg_secondary, fg=self.fg_main,
            borderwidth=0, highlightthickness=0, font=self.font_main,
            selectbackground=self.accent_green, selectforeground=self.fg_main,
            activestyle="none"
        )
        self.installed_monitors_list.pack(side="left", fill="both", expand=True)

        # --- UNTEN: BUTTONS ---
        self.button_bar = tk.Frame(self.container, bg=self.bg_main)
        self.button_bar.pack(side="bottom", fill="x", pady=(10, 0))

        self.btn_start = tk.Button(
            self.button_bar, text="Überwachung starten", width=20,
            bg=self.accent_green, fg=self.fg_main, relief="flat",
            activebackground="#218838", font=self.font_bold, cursor="hand2",
            command=self.handle_start_button
        )
        self.btn_start.pack(side="left")

        self.btn_uninstall = tk.Button(
            self.button_bar, text="Deinstallieren", width=20,
            bg=self.bg_secondary, fg=self.accent_red, relief="flat",
            activebackground=self.accent_red, activeforeground=self.fg_main,
            font=self.font_bold, cursor="hand2", command=self.handle_uninstall_button
        )
        self.btn_uninstall.pack(side="right")

    def run(self):
        controller = self.main_view_controller()
        if controller and hasattr(controller, 'update_installed_monitors_list_loop'):
            controller.update_installed_monitors_list_loop()
        self.root.mainloop()

    def handle_start_button(self):
        if self.callback_start_button:
            self.callback_start_button()

    def get_user_input(self):
        return {
            "proc": self.entry_process.get(),
            "port": self.entry_port.get(),
            "install": self.var_install.get(),
        }

    def clear_installed_monitors(self):
        self.installed_monitors_list.delete(0, tk.END)

    def set_installed_monitors(self, monitors):
        for monitor in monitors:
            self.installed_monitors_list.insert(tk.END, f"  {monitor}")

    def alarm(self, message):
        messagebox.showerror("Fehler", message)

    def askyesno(self, message):
        return messagebox.askyesno("Bestätigung", message)

    def handle_uninstall_button(self):
        controller = self.main_view_controller()
        controller.handle_uninstall_button()

    def get_list_selected_monitor(self):
        return self.installed_monitors_list.curselection()

    def select_list_selected_monitor(self, index):
        self.installed_monitors_list.selection_set(index)

if __name__ == '__main__':
    app = MainView(None)
    app.set_installed_monitors(["nginx.exe : 80", "node.exe : 3000"])
    app.run()