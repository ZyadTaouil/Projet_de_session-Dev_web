# INF5190-H23 - Projet de session

![Version](https://img.shields.io/badge/version-hiver2023-success?style=flat)
![License](https://img.shields.io/badge/license-Apache2.0-green?style=flat)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=Python&logoColor=white)
![Version](https://img.shields.io/badge/version-3.7|3.8|3.9-3776AB?style=flat&)
![JavaScript](https://img.shields.io/badge/AJAX-JavaScript-F7DF1E?style=flat&logo=JavaScript&logoColor=white)
![Flask](https://img.shields.io/badge/framework-Flask-000000?style=flat&logo=Flask&logoColor=white)
![SQLite3](https://img.shields.io/badge/db-SQLite3-003B57?style=flat&logo=SQLite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/CSS-Bootstrap-7952B3?style=flat&logo=Bootstrap&logoColor=white)

#### Auteur : Zyad TAOUIL

#### Code permanent : TAOZ79370100

#### Courriel : taouil.zyad@courriel.uqam.ca

## **📝 Titre et description du projet**

### Site Web de contraventions

Le projet consiste à récupérer un ensemble de données provenant de la ville de Montréal et d'offrir des services à partir de ces données. Il s'agit de données ouvertes à propos d'établissements ayant reçu des constats d'infraction lors d'inspections alimentaires.

### Crédits

- Les données ont été prise de : https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv
- Utilisation d'une balise HTML spéciale : multi-checkbox importée de : https://www.cssscript.com/multip-select-dropdown-checkbox/
- Jacques Berger

## **🎯 Fonctionnalités**

#### A1

**Script de téléchargement et d'insertion des données**: Un script Python qui télécharge les données des contraventions au format CSV à partir d'une URL spécifique et les insère dans une base de données SQLite.

#### A2

**Application Flask avec recherche de contraventions**: Permet de rechercher des contraventions par nom d'établissement, propriétaire et rue. Les résultats de la recherche s'affichent sur une nouvelle page, avec toutes les informations disponibles sur chaque contravention.

#### A3

**BackgroundScheduler pour la mise à jour des données**: Un BackgroundScheduler extrait les données de la ville de Montréal chaque jour à minuit et met à jour la base de données.

#### A4

**API REST pour obtenir la liste des contraventions entre deux dates**: Un service REST qui renvoie la liste des contraventions émises entre deux dates spécifiées en paramètre au format JSON. Une route `/doc` affiche la représentation HTML de la documentation RAML du service web.

#### A5

**Recherche rapide de contraventions entre deux dates**: Un formulaire sur la page d'accueil permet de rechercher rapidement des contraventions entre deux dates. Les résultats sont affichés dans un tableau avec le nom de l'établissement et le nombre de contraventions obtenues durant la période.

#### A6

**Recherche par nom de restaurant**: Un mode de recherche permet de sélectionner un restaurant dans une liste déroulante et d'afficher les informations sur ses différentes infractions.

#### B1

**Envoi de nouvelles contraventions par courriel**: Le système détecte les nouvelles contraventions depuis la dernière importation de données, en dresse une liste sans doublon et l'envoi par courriel automatiquement.

#### C1

**API REST pour obtenir la liste des établissements ayant commis des infractions**: Un service REST renvoyant la liste des établissements ayant commis une ou plusieurs infractions, triée par ordre décroissant du nombre d'infractions. Le service est documenté avec RAML sur `/doc`.

#### C2

**Service pour obtenir les données au format XML**: Un service qui renvoie les mêmes données que le point C1 au format XML avec un encodage UTF-8. Le service est documenté avec RAML sur `/doc`.

#### C3

**Service pour obtenir les données au format CSV**: Un service qui renvoie les mêmes données que le point C1 au format CSV avec un encodage UTF-8. Le service est documenté avec RAML sur `/doc`.

#### E1

**Service REST pour créer un profil d'utilisateur**: Un service REST permettant de créer un profil utilisateur avec des informations spécifiques. Le document JSON est validé avec json-schema et le service est documenté avec RAML sur `/doc`.

#### E2

**Page web d'authentification et de gestion du profil**: Une page web permettant d'invoquer le service de création de profil d'utilisateur et propose une option d'authentification.

#### E3

**Envoi automatique par courrier de nouveaux contrevenants**: Lorsqu'un nouveau contrevenant est détecté, un courriel est automatiquement envoyé à tous les
utilisateurs qui surveillent cet établissement.

## :cyclone: Clone du projet

1. Assurez-vous que Git est installé sur votre ordinateur. Si ce n'est pas le cas, vous pouvez le télécharger et l'installer depuis le site officiel de Git : [Git - Downloads](https://git-scm.com/downloads)
2. Ouvrez votre terminal ou votre invite de commande.
3. Accédez au répertoire dans lequel vous souhaitez cloner le projet en utilisant la commande "cd" (change directory) :
4. Clonez le projet en utilisant la commande "git clone" suivie de l'URL du dépôt :

```bash
git clone https://github.com/ZyadTaouil/Projet_de_session-Dev_web.git
```

5. Patientez jusqu'à ce que le clonage soit terminé.

Une fois que le clonage est terminé, vous devriez avoir une copie locale du projet sur votre ordinateur.

## :clipboard: Prérequis

Pour installer et exécuter cette application Flask, vous aurez besoin de :

- Python 3.9 ou version ultérieure
- Flask et ses dépendances :
  - Flask
  - APScheduler
  - PyYAML
  - jsonschema
  - Werkzeug 

## :wrench: Installation

### Activation de l'environnement virtuel

1. Ouvrez un terminal ou une invite de commande.

2. Accédez au répertoire de votre projet cloné en utilisant la commande `cd`

3. Assurez-vous d'avoir Python 3 installé sur votre machine en exécutant la commande suivante :
   
   ```bash
   python3 --version
   ```
   
   Si vous n'avez pas Python 3 installé, vous pouvez le télécharger à partir du site officiel : [Download Python | Python.org](https://www.python.org/downloads/)

4. Installez le package `virtualenv` si vous ne l'avez pas déjà. Cela vous permettra de créer des environnements virtuels. Exécutez la commande suivante :
   
   ```bash
   pip install virtualenv
   ```
   
   ou
   
   ```bash
   pip3 install virtualenv
   ```

5. Créez un nouvel environnement virtuel dans le répertoire de votre projet. Exécutez la commande suivante :
   
   ```bash
   python -m venv venv
   ```
   
   ou
   
   ```bash
   python3 -m venv venv
   ```
   
   Cela créera un nouvel environnement virtuel appelé "**venv**" dans votre dossier de projet.

6. Activez l'environnement virtuel. La méthode d'activation varie en fonction du système d'exploitation :
   
   - Sur Windows :
     
     ```powershell
     venv\Scripts\activate
     ```
   
   - Sur macOS et Linux :
     
     ```bash
     source venv/bin/activate
     ```
   
   Une fois l'environnement virtuel activé, votre invite de commande devrait indiquer le nom de l'environnement virtuel, par exemple `(venv)`.

### Installation des dépendances

Installez les dépendances du projet à l'aide du fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

Maintenant, votre environnement virtuel est prêt et vous pouvez commencer à développer ou à exécuter votre application Flask. N'oubliez pas de désactiver l'environnement virtuel lorsque vous avez terminé en exécutant la commande `deactivate`.

### Partir l'App

1. Assurez-vous que l'environnement virtuel que vous avez créé est activé. Si ce n'est pas le cas, activez-le en suivant les instructions précédente.

2. Définissez la variable d'environnement `FLASK_APP` pour indiquer à Flask le fichier qui contient votre application. Le fichier principal de mon application Flask est nommé `main.py`.
   
   * Sur Windows :
     
     ```powershell
     set FLASK_APP=main.py
     ```
   
   * Sur macOS et Linux :
     
     ```bash
     export FLASK_APP=main.py
     ```

3. Enfin, démarrez votre application Flask en exécutant la commande suivante :
   
   ```bash
   flask run
   ```

### Tests dans un fureteur

1. Flask démarrera un serveur de développement local et affichera l'URL à laquelle l'application est accessible, généralement `http://127.0.0.1:5000/` ou `http://localhost:5000/`.
2. Ouvrez un navigateur web et accédez à l'URL affichée pour voir l'application Flask en fonctionnement.

## 📄**Documentation de l'API**

Toute la documentation des services REST sera disponible à la route `/doc`.
