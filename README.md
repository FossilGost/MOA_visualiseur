# MOA Visualiseur

Application Windows/Python qui calcule et affiche le diametre theorique d'un groupement en MOA a 20, 50, 100, 200 et 300 yards ou metres.

Version actuelle : `1.3.1`

Createur : `FOSSILGOST`

L'interface est faite avec CustomTkinter. Elle affiche :

- un schema de dispersion par distance ;
- une projection sur une silhouette de reference ;
- une zone principale sur la tete ;
- une zone secondaire mobile avec la souris.

## Lancer le projet en Python

### 1. Creer l'environnement virtuel

```powershell
python -m venv MOAvenv
```

### 2. Activer l'environnement

```powershell
MOAvenv\Scripts\activate
```

### 3. Installer les dependances

```powershell
pip install -r requirements.txt
```

### 4. Lancer l'application

```powershell
python main.py
```

## Creer l'executable Windows

Le build complet passe par :

```powershell
python build.py
```

Ce script appelle `build_exe.py`, puis :

1. nettoie les anciens dossiers `build/`, `dist/` et l'ancien `.spec` ;
2. lance PyInstaller en mode `--onefile` ;
3. embarque les images de `gui/assets` dans l'executable ;
4. prepare le dossier `Visualisateur/` ;
5. cree `Visualisateur.zip`.

Le resultat final est :

```text
Visualisateur.zip
Visualisateur/
    MOA_Visualiseur.exe
    readme.txt
```

## Note Windows

L'executable n'est pas signe par un certificat officiel. Windows SmartScreen ou certains antivirus peuvent donc afficher un avertissement au premier lancement.

Pour distribuer l'application, envoie plutot `Visualisateur.zip` que le fichier `.exe` seul.

## Fichiers importants

```text
main.py                         Point d'entree de l'application
app_info.py                     Version actuelle et createur du logiciel
build.py                        Lance le script de build
build_exe.py                    Cree et package l'executable
requirements.txt                Dependances Python
gui/fenetre_principale.py       Interface, calculs et affichage
gui/assets/M_01.png             Image de reference
gui/assets/ico_exe.ico          Icone de l'executable
```

## Reglage de l'echelle

La projection sur l'image utilise la hauteur de tete comme reference.

Dans `gui/fenetre_principale.py` :

```python
self.head_height_cm = 26
self.head_left_px = 100
self.head_right_px = 164
self.head_top_px = 22
self.head_bottom_px = 110
```

Les quatre valeurs `head_*_px` placent le cercle de reference sur la tete de l'image `M_01.png`.

Le calcul d'echelle est :

```python
self.pixel_per_cm = (self.head_reference_height_px * self.image_scale) / self.head_height_cm
```

## Nettoyage

Ces fichiers sont generes automatiquement et ne doivent pas etre gardes dans le dossier source :

```text
build/
dist/
Visualisateur/
Visualisateur.zip
MOA_Visualiseur.spec
__pycache__/
```

Ils sont ignores par `.gitignore` et peuvent etre recrees avec :

```powershell
python build.py
```

## Version et historique

La version du logiciel est definie dans `app_info.py` :

```python
APP_VERSION = "1.3.1"
APP_CREATOR = "FOSSILGOST"
```

Les modifications sont suivies dans `CHANGELOG.md`.
