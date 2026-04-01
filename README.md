# Client Lourd — Bibliothèque Municipale de Paris
## BTS SIO SLAM — Session 2026

Application desktop Python/Tkinter destinée aux bibliothécaires.

## Prérequis
- Python 3.14+
- MAMP avec MySQL démarré
- Base de données `bibliotheque` importée

## Installation

```bash
cd client_lourd
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

## Lancement

```bash
python3 main.py
```

## Fonctionnalités
- **Onglet Livres** : CRUD complet (Ajouter, Modifier, Supprimer, Consulter)
- **Onglet Membres** : Gestion des adhérents et bibliothécaires

