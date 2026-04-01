import tkinter as tk
from tkinter import ttk
from pages.livres  import PageLivres
from pages.membres import PageMembres
from pages.retours import PageRetours


class Application(tk.Tk):
    """
    Fenêtre principale de l'application.
    Hérite de tk.Tk — point d'entrée unique.
    """

    def __init__(self):
        super().__init__()
        self.title("Bibliothèque — Interface Bibliothécaire")
        self.geometry("1100x650")
        self.resizable(True, True)
        self.configure(bg="#F4F6F9")
        self._creer_interface()

    def _creer_interface(self):
        # Bandeau titre
        tk.Label(
            self,
            text="📚  Gestion de la Bibliothèque Municipale",
            font=("Georgia", 17, "bold"),
            bg="#1A1512", fg="#C9973A",
            pady=14
        ).pack(fill="x")

        # Système d'onglets
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",     background="#F4F6F9", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[18, 9],
                        font=("Arial", 11, "bold"),
                        background="#DDE3EA", foreground="#333")
        style.map("TNotebook.Tab",
                  background=[("selected", "#1A1512")],
                  foreground=[("selected", "#C9973A")])

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=10)

        notebook.add(PageLivres(notebook),  text="📖   Livres")
        notebook.add(PageMembres(notebook), text="👥   Membres")
        notebook.add(PageRetours(notebook), text="🔄   Retours")

        # Barre de statut
        tk.Label(
            self,
            text="BTS SIO SLAM — Session 2026  |  Bibliothèque Municipale de Paris",
            font=("Arial", 9), bg="#1A1512", fg="#6A5F55", pady=5
        ).pack(fill="x", side="bottom")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
