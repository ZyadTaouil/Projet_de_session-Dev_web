from flask import Flask, render_template, request, g
from database import Database

app = Flask(__name__)


def get_db():
    with app.app_context():
        db = getattr(g, '_database', None)
        if db is None:
            g.database = Database()
        return g.database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


# Télécharger le fichier CSV depuis l'URL
url = "https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/" \
      "resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv"

# Lire le contenu CSV et l'insérer dans la base de données SQLite
get_db().insert_data_from_csv(url)


# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('home.html')


# Route pour la page de résultats
@app.route('/search', methods=['GET', 'POST'])
def search():
    # Récupération des données de la recherche
    search_term = request.form['search_term']
    search_type = request.form['search_type']

    results = get_db().search_violations(search_term, search_type)

    # Rendu du template de la page de résultats avec les données
    return render_template('results.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)



