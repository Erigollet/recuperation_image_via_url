Description

Cette application permet de télécharger automatiquement des images produits à partir d’un catalogue CSV accessible en HTTP.
Elle fournit une petite interface graphique (Tkinter) pour saisir des références produits et sélectionner les images à télécharger.

⚙️ Installation

Cloner le dépôt

git clone https://github.com/ton-compte/ton-repo.git
cd ton-repo


Créer un environnement virtuel (recommandé)

python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows


Installer les dépendances

pip install -r requirements.txt

🔑 Configuration

Copier le fichier .env.example → .env

cp .env.example .env


Éditer .env et renseigner les variables :

HTTP_URL : URL du fichier CSV contenant les produits (ex : http://www.exemple.com/catalogue.csv)

SEP : séparateur du CSV (, ; ou \t)

DOSSIER_SORTIE : chemin local où enregistrer les images

REFERENCE_PRODUIT : nom de la colonne identifiant unique (ex : Identifiant_DJ)

URL_IMAGE : nom de la colonne principale contenant l’URL de l’image (ex : Url_image)

⚠️ Ne jamais versionner votre .env : gardez-le local et utilisez .env.example comme modèle.

▶️ Utilisation

Lancer l’application avec :

python app.py


Une fenêtre s’ouvre :

Entrez une ou plusieurs références produit (séparées par des virgules).

Sélectionnez les images à télécharger (Image 1, Image 2, …).

Cliquez sur Télécharger.

Les fichiers téléchargés seront enregistrés dans le dossier défini par DOSSIER_SORTIE.

📂 Exemple d’entrée CSV
Identifiant_DJ|Url_image|Url_image_2|Url_image_3
7445845410039|http://exemple.com/img1.jpg|http://exemple.com/img2.jpg|
7444044382455|http://exemple.com/imgA.jpg||

📄 Fichiers importants

app.py → code principal

.env → variables d’environnement (non versionné)

.env.example → modèle de configuration

requirements.txt → dépendances Python

.gitignore → ignore fichiers sensibles / temporaires