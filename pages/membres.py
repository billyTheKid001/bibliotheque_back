import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from config.connexion import get_connexion

BG   = "#F4F6F9"
DARK = "#1A1512"
BLUE = "#2E74B5"


class PageMembres(tk.Frame):
    """
    Onglet CRUD des membres (adhérents + bibliothécaires).
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._creer_interface()
        self.charger_membres()

    def _creer_interface(self):
        frame_form = tk.LabelFrame(
            self, text=" Détails du membre ",
            bg=BG, fg=DARK, font=("Arial", 11, "bold"),
            padx=10, pady=8, relief="groove"
        )
        frame_form.pack(fill="x", padx=14, pady=(12, 4))

        champs = [("Nom", 14), ("Prénom", 14), ("Email", 24), ("Mot de passe", 14), ("Rôle", 14)]
        self.vars = {}
        for i, (champ, w) in enumerate(champs):
            tk.Label(frame_form, text=champ, bg=BG, fg="#444",
                     font=("Arial", 10)).grid(row=0, column=i*2, padx=(10,2), sticky="e")
            var = tk.StringVar()
            if champ == "Rôle":
                widget = ttk.Combobox(frame_form, textvariable=var,
                                      values=["adherent","bibliothecaire"],
                                      width=w, state="readonly", font=("Arial", 10))
                var.set("adherent")
            elif champ == "Mot de passe":
                widget = tk.Entry(frame_form, textvariable=var, width=w,
                                  show="*", font=("Arial", 10), relief="solid", bd=1)
            else:
                widget = tk.Entry(frame_form, textvariable=var, width=w,
                                  font=("Arial", 10), relief="solid", bd=1)
            widget.grid(row=0, column=i*2+1, padx=(2,10), pady=6)
            self.vars[champ.lower()] = var

        frame_btn = tk.Frame(self, bg=BG)
        frame_btn.pack(pady=6)
        for texte, cmd, couleur in [
            ("➕ Ajouter",    self.ajouter_membre,    "#27AE60"),
            ("✏️ Modifier",   self.modifier_membre,   BLUE),
            ("🚫 Désactiver", self.desactiver_membre, "#E74C3C"),
            ("🔄 Actualiser", self.charger_membres,   "#7F8C8D"),
            ("🧹 Vider",      self._vider,            "#95A5A6"),
        ]:
            tk.Button(frame_btn, text=texte, command=cmd,
                      bg=couleur, fg="white", font=("Arial", 10, "bold"),
                      padx=14, pady=6, relief="flat", cursor="hand2").pack(side="left", padx=5)

        frame_tab = tk.Frame(self, bg=BG)
        frame_tab.pack(fill="both", expand=True, padx=14, pady=(4, 10))

        cols = ("id","nom","prenom","email","role","inscription","statut")
        self.tableau = ttk.Treeview(frame_tab, columns=cols, show="headings", height=18)
        largeurs = {"id":45,"nom":110,"prenom":110,"email":190,"role":110,"inscription":110,"statut":80}
        labels   = {"id":"ID","nom":"Nom","prenom":"Prénom","email":"Email",
                    "role":"Rôle","inscription":"Inscription","statut":"Statut"}
        for c in cols:
            self.tableau.heading(c, text=labels[c])
            self.tableau.column(c, width=largeurs[c], anchor="center" if c in ("id","statut") else "w")

        self.tableau.tag_configure("pair",    background="#FFFFFF")
        self.tableau.tag_configure("impair",  background="#F0F4F8")
        self.tableau.tag_configure("inactif", foreground="#AAAAAA")

        sb = ttk.Scrollbar(frame_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscroll=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tableau.bind("<<TreeviewSelect>>", self._remplir)

    def charger_membres(self):
        for r in self.tableau.get_children(): self.tableau.delete(r)
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_utilisateur, nom, prenom, email, role, date_inscription, actif
                FROM utilisateurs ORDER BY nom, prenom
            """)
            for i, ligne in enumerate(cur.fetchall()):
                statut = "✅ Actif" if ligne[6] == 1 else "🚫 Inactif"
                tag = "inactif" if ligne[6] == 0 else ("pair" if i % 2 == 0 else "impair")
                self.tableau.insert("", "end", values=(*ligne[:6], statut), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def ajouter_membre(self):
        nom    = self.vars["nom"].get().strip()
        prenom = self.vars["prénom"].get().strip()
        email  = self.vars["email"].get().strip()
        mdp    = self.vars["mot de passe"].get().strip()
        role   = self.vars["rôle"].get().strip()
        if not nom or not prenom or not email or not mdp:
            messagebox.showwarning("Attention", "Tous les champs sont obligatoires.")
            return
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (nom, prenom, email, mdp_hash, role))
            conn.commit()
            messagebox.showinfo("Succès", f"Membre '{prenom} {nom}' ajouté !")
            self._vider(); self.charger_membres()
        except Exception:
            messagebox.showerror("Erreur", "Email déjà utilisé ou erreur de saisie.")
        finally:
            conn.close()

    def modifier_membre(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un membre.")
            return
        id_user = self.tableau.item(sel[0])["values"][0]
        nom    = self.vars["nom"].get().strip()
        prenom = self.vars["prénom"].get().strip()
        email  = self.vars["email"].get().strip()
        role   = self.vars["rôle"].get().strip()
        if not nom or not prenom or not email:
            messagebox.showwarning("Attention", "Nom, Prénom et Email sont obligatoires.")
            return
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE utilisateurs SET nom=%s, prenom=%s, email=%s, role=%s
                WHERE id_utilisateur=%s
            """, (nom, prenom, email, role, id_user))
            conn.commit()
            messagebox.showinfo("Succès", "Membre modifié !")
            self.charger_membres()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def desactiver_membre(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un membre.")
            return
        id_user = self.tableau.item(sel[0])["values"][0]
        prenom  = self.tableau.item(sel[0])["values"][2]
        nom     = self.tableau.item(sel[0])["values"][1]
        if not messagebox.askyesno("Confirmation", f"Désactiver le compte de '{prenom} {nom}' ?"):
            return
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("UPDATE utilisateurs SET actif=0 WHERE id_utilisateur=%s", (id_user,))
            conn.commit()
            messagebox.showinfo("Succès", f"Compte de '{prenom} {nom}' désactivé.")
            self.charger_membres()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def _remplir(self, event):
        sel = self.tableau.selection()
        if not sel: return
        v = self.tableau.item(sel[0])["values"]
        self.vars["nom"].set(v[1])
        self.vars["prénom"].set(v[2])
        self.vars["email"].set(v[3])
        self.vars["rôle"].set(v[4])
        self.vars["mot de passe"].set("")

    def _vider(self):
        for k, var in self.vars.items():
            var.set("adherent" if k == "rôle" else "")
