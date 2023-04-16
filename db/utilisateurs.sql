CREATE TABLE utilisateurs
(
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_complet    TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    etablissements TEXT NOT NULL,
    photo          TEXT,
    mot_de_passe   TEXT NOT NULL,
    salt           TEXT NOT NULL
);