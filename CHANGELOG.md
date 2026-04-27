# Changelog

Toutes les modifications importantes du projet sont suivies ici.

Format conseille :

- `MAJOR` : changement important ou rupture de compatibilite.
- `MINOR` : nouvelle fonctionnalite.
- `PATCH` : correction ou petite amelioration.

## [1.3.3] - 2026-04-27

### Ajoute

- Script `lancer.bat` pour creer/reutiliser le venv `MOAvenv`, installer les dependances et lancer `main.py`.

## [1.3.2] - 2026-04-26

### Corrige

- Rafraichissement des changements de portee et d'unite centralise.
- Recalcul complet effectue avant le repositionnement du schema et des cercles.
- Nettoyage des anciennes valeurs quand aucune valeur MOA valide n'est saisie.

## [1.3.1] - 2026-04-26

### Modifie

- Boutons de navigation des silhouettes deplaces depuis l'en-tete vers l'image.
- Fleches gauche/droite affichees en bas de l'image.
- Numero de silhouette affiche directement sur l'image.

## [1.3.0] - 2026-04-26

### Ajoute

- Selecteur d'image dans la frame droite avec boutons gauche/droite.
- Navigation circulaire entre les silhouettes `M_01.png` a `M_08.png`.

### Modifie

- Le changement d'image conserve le calcul MOA courant et repositionne les cercles sur la nouvelle silhouette.

## [1.2.1] - 2026-04-26

### Modifie

- Champ de saisie MOA reduit pour rester proportionne aux valeurs attendues.
- Selecteurs de systeme et de portee ranges sur deux lignes alignees.
- Legende sous l'image simplifiee en libelles courts `Tete` et `Coeur`.
- Nom du createur affiche avec la version dans une zone lisible de la barre laterale.
- Couleur de la distance 20 remplacee par du violet pour eviter la confusion avec le cercle jaune de reference.

### Verifie

- Calcul MOA confirme avec la formule angulaire reelle : `tan(MOA / 60 degres) x distance`.
- Les cercles de la silhouette restent en echelle reelle par rapport a la hauteur de tete de reference.

## [1.2.0] - 2026-04-26

### Ajoute

- Selecteur de portee avec deux modes :
  - `Courte portee` : 20, 50 et 100 yards/metres.
  - `Longue portee` : 100, 200 et 300 yards/metres.

### Modifie

- Le calcul, la legende, le schema et les cercles sur la silhouette utilisent uniquement les distances de la portee active.
- Le schema se recale automatiquement sur la distance maximale active : 100 en courte portee, 300 en longue portee.

## [1.1.0] - 2026-04-26

### Ajoute

- Selecteur de systeme de distance : `Imperial system` en yards et `Metric system` en metres.
- Calcul reel selon l'unite selectionnee, sans conversion d'affichage approximative.
- Distances courtes 20 et 50 ajoutees au calcul, au schema et aux cercles sur la silhouette.
- Legende dynamique adaptee au systeme de distance actif.

### Corrige

- Formule MOA alignee sur la valeur angulaire reelle : environ 2,66 cm a 100 yards et 2,91 cm a 100 metres pour 1 MOA.

## [1.0.0] - 2026-04-26

Version initiale stabilisee du MOA Visualiseur.

### Ajoute

- Interface CustomTkinter sombre avec navigation Accueil / Explication.
- Calcul du diametre de dispersion en MOA a 100, 200 et 300 yards.
- Visualisation de l'ouverture angulaire sur un schema.
- Projection des cercles MOA sur une silhouette de reference.
- Zone principale fixe sur la tete.
- Zone secondaire mobile avec la souris.
- Page d'explication detaillee sur le MOA, ses limites et ses conditions d'interpretation.
- Tableau comparatif des valeurs MOA moyennes par categorie d'arme.
- Script de build PyInstaller en mode `--onefile`.
- Packaging automatique dans `Visualisateur/` et `Visualisateur.zip`.
- Nettoyage automatique de `dist/` et du fichier `.spec` apres creation du package.
- README projet remis au propre.

### Notes

- L'executable n'est pas signe par un certificat officiel.
- `requirements.txt` reste a maintenir selon les dependances reellement utilisees.
