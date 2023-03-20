import csv
import sqlite3
import urllib.request


class Database:
    def __init__(self):
        self.connection = None

    # connexion à la bdd
    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/violations.db')
        return self.connection

    # déconexion de la bdd
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    # Lire le contenu CSV et l'insérer dans la base de données SQLite
    def insert_data_from_csv(self, csv_url):
        conn = self.get_connection()
        cursor = conn.cursor()
        filename, headers = urllib.request.urlretrieve(csv_url)
        with open(filename, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            next(csvreader)  # Ignorer la première ligne (en-tête)
            for row in csvreader:
                cursor.execute(
                    "INSERT INTO violations (id_poursuite, business_id, date, "
                    "description, adresse, date_jugement, etablissement, "
                    "montant, proprietaire, ville, statut, date_statut, "
                    "categorie) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    row)

        conn.commit()
        conn.close()

    # renvoie les résultats de la recherche
    def search_violations(self, search_term, search_type):
        # Connexion à la base de données
        conn = self.get_connection()
        c = conn.cursor()

        # Requête SQL en fonction du type de recherche
        if search_type == 'etablissement':
            query = "SELECT * FROM violations WHERE etablissement LIKE ?"
        elif search_type == 'proprietaire':
            query = "SELECT * FROM violations WHERE proprietaire LIKE ?"
        elif search_type == 'rue':
            query = "SELECT * FROM violations WHERE adresse LIKE ?"
        else:
            query = "SELECT * FROM violations"

        # Exécution de la requête SQL
        c.execute(query, ('%' + search_term + '%',))
        results = c.fetchall()
        conn.close()

        return results
