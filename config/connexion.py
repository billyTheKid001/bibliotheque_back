import mysql.connector
from mysql.connector import Error

def get_connexion():
    """
    Retourne une connexion MySQL active.
    Port 8889 = MAMP | Port 3306 = XAMPP/WAMP
    """
    try:
        connexion = mysql.connector.connect(
            host     = "localhost",
            port     = 8889,
            database = "bibliotheque",
            user     = "root",
            password = "root"
        )
        return connexion
    except Error as e:
        print(f"Erreur de connexion : {e}")
        return None
