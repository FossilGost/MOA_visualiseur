import os
import shutil
import subprocess
import sys
from pathlib import Path

from app_info import APP_CREATOR, APP_VERSION


PROJECT_DIR = Path(__file__).resolve().parent
APP_NAME = "MOA_Visualiseur"
PACKAGE_NAME = "Visualisateur"
ICON_PATH = PROJECT_DIR / "gui" / "assets" / "ico_exe.ico"
ASSETS_PATH = PROJECT_DIR / "gui" / "assets"
ENTRYPOINT = PROJECT_DIR / "main.py"
PACKAGE_DIR = PROJECT_DIR / PACKAGE_NAME
ZIP_PATH = PROJECT_DIR / f"{PACKAGE_NAME}.zip"


def remove_path(path):
    """Supprime un fichier ou dossier genere par le build precedent."""
    if path.exists():
        print(f"Suppression : {path.name}")
        if path.is_dir():
            shutil.rmtree(path, onerror=handle_remove_readonly)
        else:
            os.chmod(path, 0o700)
            path.unlink()


def handle_remove_readonly(func, path, _exc_info):
    os.chmod(path, 0o700)
    func(path)


def create_package(exe_path):
    """Prepare le dossier distribue et l'archive zip a donner aux utilisateurs."""
    remove_path(PACKAGE_DIR)
    remove_path(ZIP_PATH)

    PACKAGE_DIR.mkdir()
    shutil.copy2(exe_path, PACKAGE_DIR / exe_path.name)
    (PACKAGE_DIR / "readme.txt").write_text(
        "MOA Visualiseur\n"
        "================\n\n"
        f"Version : {APP_VERSION}\n\n"
        f"Createur : {APP_CREATOR}\n\n"
        "Pour lancer l'application :\n"
        "1. Decompressez le fichier Visualisateur.zip.\n"
        "2. Ouvrez le dossier Visualisateur.\n"
        "3. Double-cliquez sur MOA_Visualiseur.exe.\n\n"
        "Notes :\n"
        "- Aucun Python n'est necessaire.\n"
        "- Windows peut afficher un avertissement au premier lancement, car\n"
        "  l'application n'est pas signee par un certificat officiel.\n",
        encoding="utf-8",
    )

    shutil.make_archive(str(ZIP_PATH.with_suffix("")), "zip", PROJECT_DIR, PACKAGE_NAME)


def main():
    """Point d'entree du build complet : PyInstaller puis packaging."""
    if not ENTRYPOINT.exists():
        raise FileNotFoundError(f"Fichier introuvable : {ENTRYPOINT}")
    if not ASSETS_PATH.exists():
        raise FileNotFoundError(f"Dossier introuvable : {ASSETS_PATH}")
    if not ICON_PATH.exists():
        raise FileNotFoundError(f"Icone introuvable : {ICON_PATH}")

    remove_path(PROJECT_DIR / "build")
    remove_path(PROJECT_DIR / "dist")
    remove_path(PROJECT_DIR / f"{APP_NAME}.spec")

    # --onefile cree un seul .exe ; --add-data embarque les images/icones.
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "--icon",
        str(ICON_PATH),
        "--add-data",
        f"{ASSETS_PATH};gui/assets",
        str(ENTRYPOINT),
    ]

    print("Generation de l'executable...")
    subprocess.run(command, cwd=PROJECT_DIR, check=True)

    exe_path = PROJECT_DIR / "dist" / f"{APP_NAME}.exe"
    create_package(exe_path)
    remove_path(PROJECT_DIR / "dist")
    remove_path(PROJECT_DIR / f"{APP_NAME}.spec")

    print()
    print("Build termine.")
    print(f"Executable : {PACKAGE_DIR / exe_path.name}")
    print(f"Archive : {ZIP_PATH}")


if __name__ == "__main__":
    main()
