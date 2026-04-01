import tkinter as tk
from tkinter import ttk, messagebox
from config.connexion import get_connexion

BG   = "#F4F6F9"
DARK = "#1A1512"


class PageRetours(tk.Frame):
    """
    Onglet de validation des retours de livres.
    Affiche tous les emprunts en cours avec indicateurs de retard.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._creer_interface()
        self.charger_retours()

    def _creer_interface(self):
        # En-tête
        frame_haut = tk.Frame(self, bg=BG)
        frame_haut.pack(fill="x", padx=14, pady=(12, 4))

        tk.Label(frame_haut, text="Emprunts en cours",
                 font=("Georgia", 14, "bold"), bg=BG, fg=DARK).pack(side="left")

        frame_btn = tk.Frame(self, bg=BG)
        frame_btn.pack(pady=6)
        tk.Button(frame_btn, text="✅  Valider le retour sélectionné",
                  command=self.valider_retour,
                  bg="#27AE60", fg="white", font=("Arial", 11, "bold"),
                  padx=18, pady=8, relief="flat", cursor="hand2").pack(side="left", padx=6)
        tk.Button(frame_btn, text="🔄  Actualiser",
                  command=self.charger_retours,
                  bg="#7F8C8D", fg="white", font=("Arial", 11, "bold"),
                  padx=14, pady=8, relief="flat", cursor="hand2").pack(side="left", padx=6)

        # Légende
        frame_leg = tk.Frame(self, bg=BG)
        frame_leg.pack(pady=2)
        tk.Label(frame_leg, text="🟥 En retard",     bg=BG, fg="#C0392B", font=("Arial", 9)).pack(side="left", padx=12)
        tk.Label(frame_leg, text="🟧 < 3 jours",     bg=BG, fg="#E67E22", font=("Arial", 9)).pack(side="left", padx=12)
        tk.Label(frame_leg, text="🟩 Dans les délais",bg=BG, fg="#27AE60", font=("Arial", 9)).pack(side="left", padx=12)

        # Tableau
        frame_tab = tk.Frame(self, bg=BG)
        frame_tab.pack(fill="both", expand=True, padx=14, pady=(4, 6))

        cols = ("id","titre","emprunteur","date_emprunt","retour_prevu","jours")
        self.tableau = ttk.Treeview(frame_tab, columns=cols, show="headings", height=20)
        largeurs = {"id":50,"titre":230,"emprunteur":160,"date_emprunt":120,"retour_prevu":120,"jours":130}
        labels   = {"id":"ID","titre":"Titre","emprunteur":"Emprunteur",
                    "date_emprunt":"Emprunté le","retour_prevu":"Retour prévu","jours":"Jours restants"}
        for c in cols:
            self.tableau.heading(c, text=labels[c])
            self.tableau.column(c, width=largeurs[c], anchor="center" if c in ("id","jours") else "w")

        self.tableau.tag_configure("retard", background="#FDECEA", foreground="#C0392B")
        self.tableau.tag_configure("urgent", background="#FEF9E7", foreground="#E67E22")
        self.tableau.tag_configure("ok_p",   background="#FFFFFF")
        self.tableau.tag_configure("ok_i",   background="#F0F4F8")

        sb = ttk.Scrollbar(frame_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscroll=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Barre de stats
        self.label_stats = tk.Label(self, text="", bg="#E8ECF0",
                                    font=("Arial", 10), fg="#444", pady=5)
        self.label_stats.pack(fill="x", padx=14, pady=(2, 8))

    def charger_retours(self):
        for r in self.tableau.get_children(): self.tableau.delete(r)
        conn = get_connexion()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    e.id_emprunt,
                    l.titre,
                    CONCAT(u.prenom, ' ', u.nom),
                    e.date_emprunt,
                    e.date_retour_prevue,
                    DATEDIFF(e.date_retour_prevue, CURDATE())
                FROM emprunts e
                JOIN livres       l ON e.id_livre       = l.id_livre
                JOIN utilisateurs u ON e.id_utilisateur = u.id_utilisateur
                WHERE e.date_retour_effective IS NULL
                ORDER BY e.date_retour_prevue ASC
            """)
            lignes = cur.fetchall()
            nb_retard = nb_urgent = nb_ok = ok_i = 0

            for ligne in lignes:
                j = ligne[5]
                if j is not None and j < 0:
                    texte = f"⚠️ {abs(j)} jour(s) de retard"
                    tag = "retard"; nb_retard += 1
                elif j is not None and j <= 3:
                    texte = f"⏰ {j} jour(s)"
                    tag = "urgent"; nb_urgent += 1
                else:
                    texte = f"{j} jour(s)" if j is not None else "—"
                    tag = "ok_p" if ok_i % 2 == 0 else "ok_i"
                    nb_ok += 1; ok_i += 1

                self.tableau.insert("", "end", values=(
                    ligne[0], ligne[1], ligne[2],
                    ligne[3], ligne[4], texte
                ), tags=(tag,))

            total = len(lignes)
            self.label_stats.config(
                text=f"Total : {total} emprunt(s)  |  "
                     f"✅ {nb_ok} dans les délais  |  "
                     f"⏰ {nb_urgent} urgent(s)  |  "
                     f"⚠️ {nb_retard} en retard"
            )
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()

    def valider_retour(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un emprunt.")
            return
        id_emprunt = self.tableau.item(sel[0])["values"][0]
        titre      = self.tableau.item(sel[0])["values"][1]
        emprunteur = self.tableau.item(sel[0])["values"][2]

        if not messagebox.askyesno("Confirmation",
                f"Valider le retour de '{titre}'\nemprunté par {emprunteur} ?"):
            return

        conn = get_connexion()
        if not conn: return
        try:
            conn.start_transaction()
            cur = conn.cursor()

            # 1. Enregistrer la date de retour
            cur.execute("""
                UPDATE emprunts
                SET date_retour_effective = CURDATE()
                WHERE id_emprunt = %s
            """, (id_emprunt,))

            # 2. Remettre le livre disponible
            cur.execute("""
                UPDATE livres SET disponible = 1
                WHERE id_livre = (
                    SELECT id_livre FROM emprunts WHERE id_emprunt = %s
                )
            """, (id_emprunt,))

            conn.commit()
            messagebox.showinfo("Succès", f"Retour de '{titre}' enregistré !")
            self.charger_retours()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erreur", str(e))
        finally:
            conn.close()
