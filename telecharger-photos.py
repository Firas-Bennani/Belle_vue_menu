#!/usr/bin/env python3
"""
Télécharge une photo pour chacun des 171 articles de la carte Belle Vue.

Source : Pexels — licence gratuite, usage commercial autorisé, sans attribution
obligatoire. https://www.pexels.com/license/

Usage :
    pip install requests pillow
    export PEXELS_API_KEY="votre_cle"        # gratuite sur pexels.com/api
    python telecharger-photos.py

Options :
    --seulement froides-0.jpg,pizzas-3.jpg   ne retélécharge que ces fichiers
    --force                                  écrase les photos déjà présentes
    --largeur 900                            largeur de sortie en pixels

Le script est relançable sans risque : il saute les fichiers déjà téléchargés.
"""

import argparse, csv, io, os, sys, time
from pathlib import Path

try:
    import requests
    from PIL import Image
except ImportError:
    sys.exit("Installez les dépendances :  pip install requests pillow")

DOSSIER = Path(__file__).parent / "photos"
MANIFEST = DOSSIER / "manifest.csv"
API = "https://api.pexels.com/v1/search"


def chercher(cle, requete, essai=0):
    """Renvoie l'URL de la meilleure photo pour cette requête, ou None."""
    try:
        r = requests.get(
            API,
            headers={"Authorization": cle},
            params={"query": requete, "per_page": 5, "orientation": "landscape"},
            timeout=20,
        )
    except requests.RequestException as e:
        print(f"    réseau : {e}")
        return None

    if r.status_code == 429:                      # quota par minute atteint
        if essai >= 3:
            return None
        attente = 20 * (essai + 1)
        print(f"    quota atteint, pause de {attente}s")
        time.sleep(attente)
        return chercher(cle, requete, essai + 1)

    if r.status_code == 401:
        sys.exit("Clé API refusée. Vérifiez PEXELS_API_KEY.")
    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return None

    photos = r.json().get("photos", [])
    if not photos:
        return None
    return photos[0]["src"]["large"]


def enregistrer(url, chemin, largeur):
    """Télécharge, recadre en 4/3, redimensionne et écrit en JPEG."""
    img = Image.open(io.BytesIO(requests.get(url, timeout=30).content)).convert("RGB")

    cible = 4 / 3
    l, h = img.size
    if l / h > cible:                              # trop large : on rogne les côtés
        neuf = int(h * cible)
        img = img.crop(((l - neuf) // 2, 0, (l + neuf) // 2, h))
    else:                                          # trop haut : on rogne haut et bas
        neuf = int(l / cible)
        img = img.crop((0, (h - neuf) // 2, l, (h + neuf) // 2))

    img = img.resize((largeur, int(largeur / cible)), Image.LANCZOS)
    img.save(chemin, "JPEG", quality=82, optimize=True, progressive=True)
    return chemin.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seulement", default="", help="liste de fichiers séparés par des virgules")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--largeur", type=int, default=900)
    args = ap.parse_args()

    cle = os.environ.get("PEXELS_API_KEY")
    if not cle:
        sys.exit("Définissez PEXELS_API_KEY (clé gratuite sur https://www.pexels.com/api/).")
    if not MANIFEST.exists():
        sys.exit(f"Manifeste introuvable : {MANIFEST}")

    filtre = {f.strip() for f in args.seulement.split(",") if f.strip()}
    lignes = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    if filtre:
        lignes = [l for l in lignes if l["fichier"] in filtre]

    faits = sautes = echecs = 0
    manquants = []

    for i, l in enumerate(lignes, 1):
        chemin = DOSSIER / l["fichier"]
        if chemin.exists() and not args.force:
            sautes += 1
            continue

        print(f"[{i}/{len(lignes)}] {l['plat']}  ←  « {l['recherche']} »")
        url = chercher(cle, l["recherche"])
        if not url:                                # repli : la requête large de la catégorie
            repli = l["recherche"].split()[-2:]
            print(f"    aucun résultat, second essai sur « {' '.join(repli)} »")
            url = chercher(cle, " ".join(repli))

        if not url:
            echecs += 1
            manquants.append(l["fichier"])
            continue

        try:
            poids = enregistrer(url, chemin, args.largeur)
            print(f"    → {l['fichier']}  ({poids // 1024} Ko)")
            faits += 1
        except Exception as e:
            print(f"    échec écriture : {e}")
            echecs += 1
            manquants.append(l["fichier"])

        time.sleep(0.4)                            # on reste poli avec l'API

    print(f"\n{faits} téléchargées · {sautes} déjà présentes · {echecs} en échec")
    if manquants:
        print("\nÀ traiter à la main (le placeholder or s'affichera en attendant) :")
        for m in manquants:
            print("  ", m)
    print("\nRelisez chaque photo avant publication : une image qui ne ressemble pas")
    print("au plat servi déçoit le client plus qu'une absence d'image.")


if __name__ == "__main__":
    main()
