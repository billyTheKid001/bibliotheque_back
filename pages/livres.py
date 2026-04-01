import tkinter as tk
from tkinter import ttk, messagebox
from config.connexion import get_connexion

BG    = "#F4F6F9"
GOLD  = "#C9973A"
DARK  = "#1A1512"
BLUE  = "#2E74B5"


class PageLivres(tk.Frame):
    """
    Onglet CRUD complet des livres.
    Hérite de tk.Frame — conteneur Tkinter.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._creer_interface()
        self.charger_livres()

    # ── Interface ────────────────────────────────────────────────
    def _creer_interface(self):
        # Formulaire
        frame_form = tk.LabelFrame(
            self, text=" Détails du livre ",
            bg=BG, fg=DARK, font=("Arial", 11, "bold"),
            padx=10, pady=8, relief="groove"
        )
        frame_form.pack(fill="x", padx=14, pady=(12, 4))

        champs = [("ISBN", 15), ("Titre", 28), ("Auteur", 20), ("Genre", 14), ("Année", 7)]
        self.vars = {}
        for i, (champ, w) in enumerate(champs):
            tk.Label(frame_form, text=champ, bg=BG, fg="#444",
                     font=("Arial", 10)).grid(row=0, column=i*2, padx=(10,2), sticky="e")
            var = tk.StringVar()
            tk.Entry(frame_form, textvariable=var, width=w,
                     font=("Arial", 10), relief="solid", bd=1).grid(
                row=0, column=i*2+1, padx=(2,10), pady=6)
            self.vars[champ.lower()] = var

        # Boutons
        frame_btn = tk.Frame(self, bg=BG)
        frame_btn.pack(pady=6)
        for texte, cmd, couleur in [
            ("➕ Ajouter",    self.ajouter_livre,    "#27AE60"),
            ("✏️ Modifier",   self.modifier_livre,   BLUE),
            ("🗑️ Supprimer", self.supprimer_livre,  "#E74C3C"),
            ("🔄 Actualiser", self.charger_livres,   "#7F8C8D"),
            ("🧹 Vider",      self._vider,           "#95A5A6"),
        ]:
            tk.Button(frame_btn, text=texte, command=cmd,
                      bg=couleur, fg="white", font=("Arial", 10, "bold"),
                      padx=14, pady=6, relief="flat", cursor="hand2",
                      activebackground=couleur).pack(side="left", padx=5)

        # Tableau
        frame_tab = tk.Frame(self, bg=BG)
        frame_tab.pack(fill="both", expand=True, padx=14, pady=(4, 10))

        cols = ("id","isbn","titre","auteur","genre","annee","dispo")
        self.tableau = ttk.Treeview(frame_tab, columns=cols, show="headings", height=18)
        largeurs = {"id":45,"isbn":130,"titre":230,"auteur":160,"genre":90,"annee":65,"dispo":80}
        labels   = {"id":"ID","isbn":"ISBN","titre":"Titre","auteur":"Auteur",
                    "genre":"Genre","annee":"Année","dispo":"Dispo"}
        for c in cols:
            self.tableau.heading(c, text=labels[c])
            anc = "center" if c in ("id","annee","dispo") else "w"
            self.tableau.column(c, width=largeurs[c], anchor=anc)

        self.tableau.tag_configure("pair",   background="#FFFFFF")
        self.tableau.tag_configure("impair", background="#F0F4F8")

        sb = ttk.Scrollbar(frame_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscroll=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tableau.bind("<<TreeviewSelect>>", self._remplir)

    # ── BDD ──────────────────────────────────────────────────────
    def charger_livres(self):
        for r in self.tableau.get_children(): self.tableau.delete(r)
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_livre, isbn, titre, auteur, genre, annee_publication, disponible
                FROM livres ORDER BY titre
            """)
            for i, ligne in enumerate(cur.fetchall()):
                dispo = "✅ Oui" if ligne[6] == 1 else "❌ Non"
                tag = "pair" if i % 2 == 0 else "impair"
                self.tableau.insert("", "end", values=(*ligne[:6], dispo), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def ajouter_livre(self):
        isbn   = self.vars["isbn"].get().strip()
        titre  = self.vars["titre"].get().strip()
        auteur = self.vars["auteur"].get().strip()
        genre  = self.vars["genre"].get().strip()
        annee  = self.vars["année"].get().strip()
        if not isbn or not titre or not auteur:
            messagebox.showwarning("Attention", "ISBN, Titre et Auteur sont obligatoires.")
            return
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO livres (isbn, titre, auteur, genre, annee_publication)
                VALUES (%s, %s, %s, %s, %s)
            """, (isbn, titre, auteur, genre or None, annee or None))
            conn.commit()
            messagebox.showinfo("Succès", f"'{titre}' ajouté !")
            self._vider(); self.charger_livres()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def modifier_livre(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un livre.")
            return
        id_livre = self.tableau.item(sel[0])["values"][0]
        titre  = self.vars["titre"].get().strip()
        auteur = self.vars["auteur"].get().strip()
        genre  = self.vars["genre"].get().strip()
        annee  = self.vars["année"].get().strip()
        if not titre or not auteur:
            messagebox.showwarning("Attention", "Titre et Auteur sont obligatoires.")
            return
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE livres
                SET titre=%s, auteur=%s, genre=%s, annee_publication=%s
                WHERE id_livre=%s
            """, (titre, auteur, genre or None, annee or None, id_livre))
            conn.commit()
            messagebox.showinfo("Succès", "Livre modifié !")
            self.charger_livres()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def supprimer_livre(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un livre.")
            return
        id_livre = self.tableau.item(sel[0])["values"][0]
        titre    = self.tableau.item(sel[0])["values"][2]
        if not messagebox.askyesno("Confirmation", f"Supprimer '{titre}' définitivement ?"):
            return
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM livres WHERE id_livre = %s", (id_livre,))
            conn.commit()
            messagebox.showinfo("Succès", "Livre supprimé.")
            self._vider(); self.charger_livres()
        except Exception:
            messagebox.showerror("Erreur", "Impossible : ce livre est peut-être emprunté.")
        finally:
            conn.close()

    # ── Utilitaires ───────────────────────────────────────────────
    def _remplir(self, event):
        sel = self.tableau.selection()
        if not sel: return
        v = self.tableau.item(sel[0])["values"]
        self.vars["isbn"].set(v[1])
        self.vars["titre"].set(v[2])
        self.vars["auteur"].set(v[3])
        self.vars["genre"].set(v[4] if v[4] else "")
        self.vars["année"].set(v[5] if v[5] else "")

    def _vider(self):
        for var in self.vars.values(): var.set("")
