# Instalation
```sh
git clone https://github.com/TheJordanDev/360-Schedule-Exporter

cd 360-Schedule-Exporter

python -m pip install -r requirements.txt
```

# Setup

Pensez à renommer `.example.env` en `.env` et à modifier vos identifiants à l'intérieur

Installer geckodriver [ici](https://github.com/mozilla/geckodriver/releases) et mettez le dans le dossier du projet

# Usage
```sh
python main.py

# Si c'est la première fois que vous lancez le programme le scrapping ce feras automatiquement.
# Sinon vous aurez le choix avec S: Scraper (pour mettre à jour le fichier .ics) ou C pour compiler le fichier json en .ics si vous n'avez plus le fichier.
```
