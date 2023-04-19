import atexit
import csv
import hashlib
import io
import os
import smtplib
import sqlite3
import uuid
import xml.etree.ElementTree as eT
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, g, jsonify, make_response, \
    json, session, Response, redirect, flash, url_for, abort
from jsonschema.exceptions import SchemaError, ValidationError
from jsonschema.validators import validate
from werkzeug.utils import secure_filename

from database import Database

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# configuration de l'application pour le téléversement de fichier
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'Images')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'png'}


# fonction de validation du format de fichier
def allowed_file(filename):
    return any(
        filename.endswith(ext) for ext in app.config['ALLOWED_EXTENSIONS'])


# E1 : schema JSON
schema = {
    "type": "object",
    "properties": {
        "nom": {
            "type": "string",
            "minLength": 2,
            "maxLength": 50
        },
        "email": {
            "type": "string",
            "format": "email",
            "minLength": 5,
            "maxLength": 255
        },
        "password": {
            "type": "string",
            "minLength": 8,
            "maxLength": 50
        },
        "etablissements": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
        "nom",
        "email",
        "password",
        "etablissements"
    ]
}


def get_db():
    with app.app_context():
        db = getattr(g, '_database', None)
        if db is None:
            g.database = Database()
        return g.database


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)

    return decorated


def is_authenticated(session):
    return "id" in session


def send_unauthorized():
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials.', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


# Load configuration from config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)


def send_notification(email, etablissement):
    user = get_db().get_user(email)

    # message de notification
    message = MIMEMultipart()
    message['From'] = 'do-not-reply@villedemontreal.com'
    message['To'] = email
    message['Subject'] = f'Nouveau contrevenant : {etablissement}'

    text = f'Bonjour {user[1]},\n\n'
    text += f'Un nouveau contrevenant a été détecté : {etablissement} \n'
    text += f'Veuillez prendre les mesures nécessaires.\n\n'
    text += 'Cordialement,\n'
    text += 'Votre équipe de surveillance'

    message.attach(MIMEText(text))
    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.sendmail('do-not-reply@villedemontreal.com',
                             email, message.as_string())
        smtp_server.quit()
        print(f'Notification envoyée à {email}')
    except smtplib.SMTPException as e:
        print(f'Erreur lors de l\'envoi de la notification à {email}: {e}')

def check_for_new_contraventions():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    today_data = get_db().get_contraventions_by_date(today)
    yesterday_data = get_db().get_contraventions_by_date(yesterday)
    today_etablissements = set(today_data)
    yesterday_etablissements = set(yesterday_data)
    new_etablissements = today_etablissements - yesterday_etablissements
    if len(new_etablissements) > 0:
        destinataire_email = config['recipient_email']
        for etab in new_etablissements:
            # B1 : envoi à l'email dans la configuration YAML une notification
            # pour chaque nouveau contrevenant
            send_notification(destinataire_email, etab)
            users_email = get_db().get_users_by_etablissement(etab)
            for user_email in users_email:
                send_notification(user_email, etab)
    return new_etablissements

def check_for_new_etablissements():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    today_data = get_db().get_etablissements_by_date(today)
    yesterday_data = get_db().get_etablissements_by_date(yesterday)
    today_etablissements = set(today_data)
    yesterday_etablissements = set(yesterday_data)
    new_etablissements = today_etablissements - yesterday_etablissements
    if len(new_etablissements) > 0:
        destinataire_email = config['recipient_email']
        for etab in new_etablissements:
            # B1 : envoi à l'email dans la configuration YAML une notification
            # pour chaque nouveau contrevenant
            send_notification(destinataire_email, etab)
            users_email = get_db().get_users_by_etablissement(etab)
            for user_email in users_email:
                send_notification(user_email, etab)
    return new_etablissements


# Création et démarrage du scheduler
scheduler = BackgroundScheduler()
# mise à jour des données une fois par jour
scheduler.add_job(func=get_db().update_data, trigger="interval", days=1)
# B1 : check une fois par jour s'il y a de nouvelles contraventions
scheduler.add_job(func=check_for_new_contraventions,
                  trigger="interval", days=1)
# E3 : check une fois par jour s'il y a de nouveaux contrevenants
scheduler.add_job(func=check_for_new_etablissements,
                  trigger="interval", days=1)

scheduler.start()

# Arrêt du scheduler à la fermeture de l'application Flask
atexit.register(lambda: scheduler.shutdown())


# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('home.html')


# Route pour la page de résultats
@app.route('/search', methods=['GET', 'POST'])
def search():
    search_term = request.form['search_term']
    search_type = request.form['search_type']

    results = get_db().search_violations(search_term, search_type)

    return render_template('results.html', results=results,
                           search_term=search_term)


@app.route('/contrevenants', methods=['GET'])
def search_violations_by_date():
    du_str = request.args.get('du')
    au_str = request.args.get('au')

    # Vérification que les deux dates sont présentes dans la requête
    if du_str is None or au_str is None:
        return jsonify({'error': 'Veuillez renseigner les deux dates'}), 400

    # Conversion des dates en objets datetime
    try:
        du = datetime.fromisoformat(du_str)
        au = datetime.fromisoformat(au_str)
    except ValueError:
        return jsonify(
            {'error': 'Invalid date format (should be ISO 8601)'}), 400

    # Recherche des contrevenants entre les deux dates
    results = get_db().search_violations_by_date(du, au)

    # Renvoi des résultats en format JSON
    return jsonify({'results': results}), 200


@app.route('/api/violations/etablissements_json')
def etablissements():
    results = get_db().get_etablissements_violations_count()
    return jsonify(results)


@app.route('/api/violations/etablissements_xml')
def etablissements_xml():
    results = get_db().get_etablissements_violations_count()

    # Création de l'arbre XML
    root = eT.Element("establishments")
    for result in results:
        etab = eT.SubElement(root, "establishment")
        eT.SubElement(etab, "etablissement").text = \
            result["etablissement"]
        eT.SubElement(etab, "nb_violations").text = \
            str(result["nb_violations"])

    # Conversion de l'arbre XML en chaîne de caractères
    xml_string = eT.tostring(root, encoding="utf8", method="xml")

    # Création de la réponse Flask avec la chaîne de caractères XML
    response = make_response(xml_string)
    response.headers.set('Content-Type', 'application/xml')
    response.headers.set('Content-Disposition', 'attachment',
                         filename='violations.xml')

    return response


@app.route('/api/violations/etablissements_csv')
def etablissements_csv():
    results = get_db().get_etablissements_violations_count()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['etablissement', 'nb_violations'])
    for etab in results:
        writer.writerow([etab['etablissement'], etab['nb_violations']])
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = \
        'attachment; filename=violations_etablissements.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


@app.route('/etablissements')
def etablissements_list():
    etablissements = get_db().get_etablissements()
    return \
        render_template('etablissements.html', etablissements=etablissements)


@app.route('/api/violations/etablissement/<etablissement_id>', methods=['GET'])
def get_violations_for_etablissement(etablissement_id):
    results = get_db().get_violations_for_etablissement(etablissement_id)
    return jsonify({'results': results}), 200


# route pour la page de création de profil
@app.route('/api/utilisateurs', methods=['POST'])
def creation_utilisateur():
    # Valide le JSON envoyé par le client
    try:
        validate(instance=request.json, schema=schema)

        # données utilisateurs extraites de la requête JSON
        nom_complet = request.json['nom']
        email = request.json['email']
        etabs = request.json['etablissements']
        mot_de_passe = request.json['password']

        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(
            str(mot_de_passe + salt).encode("utf-8")).hexdigest()

        user_id = get_db().insert_user(nom_complet, email, etabs,
                                       hashed_password, salt)
        id_session = uuid.uuid4().hex
        get_db().save_session(id_session, email)
        session["id"] = id_session

        return jsonify(
            {"success": "Profil créé avec succès", "user_id": user_id}), 200

    except ValidationError:
        return jsonify({"error": "Document JSON invalide"}), 400
    except SchemaError as e:
        return jsonify({"error": str(e)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "L'adresse e-mail est déjà utilisée"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    etablissements = get_db().get_etablissements()
    return render_template('inscription.html', etablissements=etablissements)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # validation de l'authentification de l'utilisateur
        db_user = get_db().get_user(email)
        if db_user is not None:
            db_password = db_user[5]
            db_salt = db_user[6]
            hashed_password = hashlib.sha512(
                str(password + db_salt).encode("utf-8")).hexdigest()
            # Check si l'utilisateur et le mdp existent et sont correctes
            if db_user[2] == email and db_password == hashed_password:
                id_session = uuid.uuid4().hex
                get_db().save_session(id_session, email)
                session["id"] = id_session
                flash(f'Bienvenue {db_user[1]}', 'success')
                return redirect('/')
            else:
                flash('email ou mot de passe invalide', 'danger')
                return redirect(url_for('login'))
        else:
            flash("Cet email n'a pas de compte", 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if not is_authenticated(session):
        return redirect(url_for('login'))
    user_email = get_db().get_session(session['id'])
    user = get_db().get_user(user_email)
    if request.method == 'POST':
        new_etablissements = request.form.get('etablissements')
        etablissements_json = json.dumps(new_etablissements)
        get_db().update_etablissements(user[0], etablissements_json)

    user_etablissements = json.loads(user[3])
    return render_template('profil.html',
                           user_etablissements=user_etablissements,
                           user=user)


@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if not is_authenticated(session):
        return redirect(url_for('login'))
    user_email = get_db().get_session(session['id'])
    user = get_db().get_user(user_email)
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename != '':
            if not allowed_file(file.filename):
                flash('Le format de fichier doit être JPG ou PNG', 'error')
                return redirect(request.url)
            else:
                # sauvegarde de la photo au serveur
                filename = secure_filename(file.filename)
                file_content = file.read()
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                get_db().update_photo(user[0], filename)
                flash('La photo de profil a été téléchargée avec succès',
                      'success')
    return redirect(url_for('profil'))


@app.route('/ajouter_etablissement', methods=['GET', 'POST'])
def ajouter_etablissement():
    if not is_authenticated(session):
        return redirect(url_for('login'))
    user_email = get_db().get_session(session['id'])
    user = get_db().get_user(user_email)

    if request.method == 'POST':
        new_etablissement = request.form.get('etablissement')
        user_email = get_db().get_session(session['id'])
        user = get_db().get_user(user_email)
        ajout_etab = get_db().add_etablissement(user[0], new_etablissement)
        if ajout_etab:
            flash('établissement ajouté avec succès')
        else:
            flash(
                'Cet établissement est déjà dans votre liste de surveillances',
                'danger')
        return redirect(url_for('profil'))

    etabs = get_db().get_nonuser_etablissements(user[0])
    return render_template('ajouter_etablissement.html',
                           etablissements=etabs)


@app.route('/supprimer_etablissement/<etablissement>', methods=['GET', 'POST'])
def supprimer_etablissement(etablissement):
    if not is_authenticated(session):
        return redirect(url_for('login'))
    user_email = get_db().get_session(session['id'])
    user = get_db().get_user(user_email)
    etablissements = json.loads(user[3])
    if etablissement not in etablissements:
        abort(404)
    if len(etablissements) > 1:
        get_db().remove_user_etablissement(user[0], etablissement)
    else:
        flash('Vous devez avoir au minimum un établissement à surveiller',
              'danger')
    return redirect(url_for('profil'))


@app.route('/logout')
@authentication_required
def logout():
    id_session = session["id"]
    session.pop('id', None)
    get_db().delete_session(id_session)
    flash('Vous êtes maintenant déconnecté', 'success')
    return redirect('/')


@app.route('/doc')
def api_doc():
    return render_template('doc.html')


if __name__ == '__main__':
    app.run(debug=True)
