# Contrôle d'accès restaurant scolaire

Application Tkinter de reconnaissance faciale pour contrôler l'accès au restaurant scolaire et gérer l'ajout d'étudiants.

## Installation

`powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
`

Les paquets ace_recognition et dlib nécessitent les bibliothèques de build Visual C++ ainsi que CMake.

## Lancement

`powershell
python app.py
`

## Fonctionnalités
- Authentification administrateur
- Ajout d'étudiants avec capture/import photo
- Reconnaissance faciale et décrément solde
- Fallback par sélection d'image de test si la caméra n'est pas disponible

## Structure
- pp.py : point d'entrée Tkinter
- models/ : objets métiers
- services/ : stockage, auth, caméra, reconnaissance
- ui/ : composants Tkinter
- data/ : fichiers JSON + images
