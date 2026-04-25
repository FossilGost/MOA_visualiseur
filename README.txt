# 🖥️ Génération d’un exécutable (.exe) à partir d’un projet Python Tkinter

## 📌 Prérequis

* Python installé (version 3.x)
* Pip installé
* Accès au terminal (cmd / PowerShell)

---

## ⚙️ 1. Création d’un environnement virtuel (venv)

```bash
python -m venv venv
```

### Activation du venv

**Windows :**

```bash
venv\Scripts\activate
```

**Linux / Mac :**

```bash
source venv/bin/activate
```

---

## 📦 2. Installation des dépendances

Installer uniquement les bibliothèques nécessaires au projet :

```bash
pip install -r requirements.txt
```

Si aucun fichier requirements.txt :

```bash
pip install pyinstaller
pip install pillow
pip install requests
```

---

## 📋 3. Sauvegarde des dépendances (recommandé)

```bash
pip freeze > requirements.txt
```

---

## 🔨 4. Génération du fichier .exe

Commande de base :

```bash
pyinstaller --onefile --windowed main.py
```

### Options importantes :

* `--onefile` : génère un seul fichier exécutable
* `--windowed` : supprime la console (utile pour Tkinter)
* `--name` : nom de l’application

### Exemple :

```bash
pyinstaller --onefile --windowed --name MonApp main.py
```

---

## 📁 5. Récupération du fichier exécutable

Le fichier `.exe` est généré dans le dossier :

```bash
dist/
```

Exemple :

```bash
dist/MonApp.exe
```

---

## ⚠️ 6. Gestion des fichiers externes (images, config…)

Si le projet utilise des ressources (images, JSON, etc.) :

```bash
pyinstaller --onefile --windowed --add-data "images;images" main.py
```

⚠️ Séparateur :

* Windows → `;`
* Linux/Mac → `:`

---

## 🧩 7. Gestion des imports non détectés

Si une librairie n’est pas incluse automatiquement :

```bash
pyinstaller --hidden-import=nom_du_module main.py
```

---

## 🧪 8. Test

* Tester le `.exe` sur une autre machine
* Vérifier :

  * ouverture de l’interface
  * chargement des images
  * fonctionnement global

---

## 🧼 9. Nettoyage (optionnel)

Supprimer les dossiers inutiles après build :

```bash
build/
__pycache__/
```

---

## 🚀 10. Bonnes pratiques

* Utiliser un venv propre
* Éviter les dépendances inutiles
* Toujours tester hors environnement de dev
* Versionner `requirements.txt`

---

## 📌 Exemple de structure projet

```
mon_projet/
│
├── main.py
├── requirements.txt
├── images/
│
├── venv/
├── build/
├── dist/
```

---

## ✅ Résultat

Un fichier exécutable autonome :

```
dist/MonApp.exe
```

L’application peut être lancée sans installer Python.
