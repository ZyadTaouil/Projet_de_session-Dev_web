CREATE TABLE violations (
    id_poursuite INTEGER PRIMARY KEY,
    business_id INTEGER,
    date TEXT,
    description TEXT,
    adresse TEXT,
    date_jugement TEXT,
    etablissement TEXT,
    montant REAL,
    proprietaire TEXT,
    ville TEXT,
    statut TEXT,
    date_statut TEXT,
    categorie TEXT
);