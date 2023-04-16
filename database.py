import csv
import os
import sqlite3
import urllib.request
from datetime import datetime
from http.client import IncompleteRead
from flask import json, app


def update_last_import_date(date):
    log_file = 'update.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                lines[-1] = str(date)


def update_last_import_date(date):
    log_file = 'update.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                lines[-1] = str(date)


class Database:
    def __init__(self):
        self.connection = None

    # connexion à la bdd
    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/database.db')
        return self.connection

    # déconnexion de la bdd
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def empty_violations(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM violations")
        conn.commit()
        conn.close

    # Lire le contenu CSV et l'insérer dans la base de données SQLite
    def insert_data_from_csv(self, csv_url):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            filename, headers = urllib.request.urlretrieve(csv_url)
        except urllib.error.URLError as e:
            print("Failed to download the file:", e)
            return

        # Vider la table pour refaire une insertion
        self.empty_violations()

        with open(filename, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            next(csvreader)  # Ignorer la première ligne (en-tête)
            for row in csvreader:
                try:
                    cursor.execute(
                        "INSERT INTO violations (id_poursuite, business_id, "
                        "date, description, adresse, date_jugement, "
                        "etablissement, montant, proprietaire, ville, statut, "
                        "date_statut, categorie) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
                except IncompleteRead:
                    continue

        conn.commit()
        conn.close()

    # renvoie les résultats de la recherche
    def search_violations(self, search_term, search_type):
        # Connexion à la base de données
        conn = self.get_connection()
        c = conn.cursor()
        query = ""
        query2 = ""

        # Requête SQL en fonction du type de recherche
        if search_type == 'etablissement':
            query = "SELECT * FROM violations WHERE etablissement LIKE ?"
        elif search_type == 'proprietaire':
            query = "SELECT * FROM violations WHERE proprietaire LIKE ?"
        elif search_type == 'rue':
            query = "SELECT * FROM violations WHERE adresse LIKE ?"
        else:
            query2 = self.get_violations()

        # Exécution de la requête SQL
        if query != "":
            c.execute(query, ('%' + search_term + '%',))
        else:
            c.execute(query2)
        results = c.fetchall()
        conn.close()

        return results

    # Mettre à jour la base de données
    def update_data(self):
        # Télécharger le fichier CSV depuis l'URL et l'insérer dans la base de
        # données SQLite
        url = "https://data.montreal.ca/dataset/" \
              "05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/" \
              "7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv"
        self.insert_data_from_csv(url)

        # log the update time in a file
        now = datetime.datetime.now()
        log_file = open("update.log", "a")
        log_file.write("Données mise à jour à {}\n".format(now))
        log_file.close()

    def search_violations_by_date(self, du, au):
        # Connexion à la base de données
        conn = self.get_connection()
        c = conn.cursor()

        # Requête SQL pour récupérer les violations commises
        # entre les deux dates
        query = "SELECT etablissement, COUNT(*) as nb_violations " \
                "FROM violations WHERE date_jugement BETWEEN ? AND ? " \
                "GROUP BY etablissement ORDER BY nb_violations DESC"
        c.execute(query, (du, au))

        # Récupération des résultats
        results = []
        for row in c.fetchall():
            results.append({
                'etablissement': row[0],
                'nb_violations': row[1],
            })

        # Fermeture de la connexion à la base de données
        conn.close()

        return results

    def get_violations(self):
        conn = self.get_connection()
        c = conn.cursor()

        query = "SELECT * FROM violations"
        c.execute(query)
        results = c.fetchall()
        conn.close()

        return results

    def get_etablissements_by_date(self, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT etablissement FROM violations WHERE date=?",
                       (date,))
        results = cursor.fetchall()
        conn.close()

        return results

    def get_etablissements_violations_count(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT etablissement, COUNT(*) as nb_violations "
                       "FROM violations GROUP BY etablissement "
                       "ORDER BY nb_violations DESC")
        rows = cursor.fetchall()
        violations = []
        for row in rows:
            violations.append(
                {"etablissement": row[0], "nb_violations": row[1]})

        conn.close()

        return violations

    def get_violations_for_etablissement(self, etablissement):
        # Connexion à la base de données
        conn = self.get_connection()
        c = conn.cursor()

        # Requête SQL pour récupérer les violations de l'établissement
        query = "SELECT * FROM violations WHERE business_id = ?"
        c.execute(query, (etablissement,))

        # Récupération des résultats
        violations = []
        for row in c.fetchall():
            violations.append({
                'id_poursuite': row[0],
                'business_id': row[1],
                'date': row[2],
                'description': row[3],
                'adresse': row[4],
                'date_jugement': row[5],
                'etablissement': row[6],
                'montant': row[7],
                'proprietaire': row[8],
                'ville': row[9],
                'statut': row[10],
                'date_statut': row[11],
                'categorie': row[12]
            })

        conn.close()

        return violations

    def get_etablissements(self):
        conn = self.get_connection()
        c = conn.cursor()

        query = "SELECT business_id, etablissement FROM VIOLATIONS " \
                "GROUP BY business_id"
        c.execute(query)
        results = c.fetchall()

        conn.close()

        return results

    def get_nonuser_etablissements(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()

        query = "SELECT etablissement FROM VIOLATIONS " \
                "GROUP BY business_id"
        c.execute(query)
        etabs = c.fetchall()
        new_etabs = []
        for etab in etabs:
            new_etabs.append(etab[0])
        query2 = "SELECT etablissements FROM utilisateurs WHERE id = ?"
        c.execute(query2, (user_id,))
        user_etabs = c.fetchone()[0]
        user_etabs = user_etabs.strip("][").split(', ')
        results = list(set(new_etabs) - set(user_etabs))

        conn.close()

        return sorted(results)

    def add_etablissement(self, user_id, etablissement):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            'SELECT etablissements FROM utilisateurs WHERE id = ?',
            (user_id,)
        )
        user_etab = cursor.fetchone()[0]
        # renvoi une liste des etablissements
        etab = user_etab.strip('][').split(', ')

        if etablissement not in user_etab:
            etab.append('"' + etablissement + '"')
            etabs = '[' + ','.join(etab) + ']'
            cursor.execute(
                'UPDATE utilisateurs SET etablissements = ? WHERE id = ?',
                (etabs, user_id)
            )
            connection.commit()
            return True

        return False

    def update_etablissements(self, user_id, etablissements):
        connection = self.get_connection()
        cursor = connection.cursor()
        if etablissements is not None:
            cursor.execute(
                'UPDATE utilisateurs SET etablissements = ? WHERE id = ?',
                (etablissements, user_id)
            )
        connection.commit()

        return True

    def remove_user_etablissement(self, user_id, etablissement):
        connection = self.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            'SELECT etablissements FROM utilisateurs WHERE id = ?',
            (user_id,)
        )
        user_etablissements = cursor.fetchone()[0]

        if user_etablissements is not None:
            # renvoi une liste des etablissements
            user_etablissements = user_etablissements.strip('][').split(',')
            user_etablissements.remove('"' + etablissement + '"')
            etablissements = '[' + ','.join(user_etablissements) + ']'
            cursor.execute(
                'UPDATE utilisateurs SET etablissements = ? WHERE id = ?',
                (etablissements, user_id)
            )
            connection.commit()
            return True

        return False

    def get_user(self, email):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM utilisateurs WHERE email = ?",
            (email,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def get_etablissement_by_user(self, user_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            'SELECT etablissements FROM utilisateurs WHERE id = ?',
            (user_id,)
        )
        user_etablissements = cursor.fetchall()
        connection.commit()

        return user_etablissements

    def get_users_by_etablissement(self, etab):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            'SELECT email FROM utilisateurs WHERE etablissement = ?',
            (etab,)
        )
        users_email = cursor.fetchall()
        connection.commit()

        return users_email

    def insert_user(self, nom_complet, email, etablissements,
                    mot_de_passe, salt):

        conn = self.get_connection()
        c = conn.cursor()

        # Converti les etablissements au format JSON before avant d'insérer
        # dans la base de données
        etablissements_json = json.dumps(etablissements)
        photo = 'Images/profile.png'

        c.execute(
            "INSERT INTO utilisateurs (nom_complet, email, etablissements, "
            "photo, mot_de_passe, salt) VALUES (?, ?, ?, ?, ?, ?)",
            (
                nom_complet, email, etablissements_json, photo, mot_de_passe,
                salt))
        conn.commit()

        return c.lastrowid

    # à enlever
    def update_user(self, user_id, etablissements=None, photo=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        if etablissements is not None:
            etablissements = json.dumps(etablissements)
        if photo is not None:
            photo = os.path.relpath(photo, app.config['UPLOAD_FOLDER'])
        cursor.execute(
            'UPDATE utilisateurs SET etablissements = ?, photo = ? WHERE id = ?',
            (etablissements, photo, user_id)
        )
        connection.commit()

        return True

    def update_photo(self, user_id, filename):
        # connect to the database
        connection = self.get_connection()
        cursor = connection.cursor()

        # update the user's photo in the database
        cursor.execute('UPDATE utilisateurs SET photo = ? WHERE id = ?',
                       (filename, user_id))
        connection.commit()

        # close the database connection
        connection.close()

    # sessions

    def save_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(("insert into sessions(id_session, user) "
                            "values(?, ?)"), (id_session, username))
        connection.commit()

    def delete_session(self, id_session):
        connection = self.get_connection()
        connection.execute(("delete from sessions where id_session=?"),
                           (id_session,))
        connection.commit()

    def get_session(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute(("select user from sessions where id_session=?"),
                       (id_session,))
        data = cursor.fetchone()
        cursor.close()
        if data is None:
            return None
        else:
            return data[0]
