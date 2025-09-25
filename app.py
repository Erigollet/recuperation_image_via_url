import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import mimetypes

# =========================
# Chargement env
# =========================
load_dotenv()

HTTP_URL       = os.getenv("HTTP_URL")  
SEP_RAW        = os.getenv("SEP", ",") 
DOSSIER_SORTIE = os.getenv("DOSSIER_SORTIE")
REFERENCE_PRODUIT = os.getenv("REFERENCE_PRODUIT")
URL_IMAGE = os.getenv("URL_IMAGE")


if not HTTP_URL or not SEP_RAW or not DOSSIER_SORTIE:
    raise ValueError("Variables manquantes : HTTP_URL, SEP ou DOSSIER_SORTIE")

# Décoder les échappements (permet "\t" -> tabulation)
SEP = SEP_RAW.encode("utf-8").decode("unicode_escape")

# =========================
# LECTURE du catalogue
# =========================
DF = pd.read_csv(HTTP_URL, sep=SEP)

if REFERENCE_PRODUIT not in DF.columns:
    raise ValueError("Le catalogue doit contenir la colonne 'votre ref produit'.")

# Normaliser Identifiant_DJ en int (en écartant le bruit)
DF[REFERENCE_PRODUIT] = pd.to_numeric(DF[REFERENCE_PRODUIT], errors="coerce")
DF = DF.dropna(subset=[REFERENCE_PRODUIT]).copy()
DF[REFERENCE_PRODUIT] = DF[REFERENCE_PRODUIT].astype("int64")
DF = DF.drop_duplicates(subset=[REFERENCE_PRODUIT], keep="first")

print("HTTP:", DF.shape)
print(DF.head())

# =========================
# Dossier destination
# =========================
home = Path.home()
destination_folder = home / DOSSIER_SORTIE
destination_folder = destination_folder.expanduser().resolve()
destination_folder.mkdir(parents=True, exist_ok=True)

# =========================
# Session HTTP pour images
# =========================
session = requests.Session()
session.headers.update({"User-Agent": "DownloadImageDL/1.0 (+python requests)"})

def _extension_from_response(resp, url_fallback: str) -> str:
    ctype = (resp.headers.get("Content-Type") or "").partition(";")[0].strip()
    if ctype:
        ext = mimetypes.guess_extension(ctype)
        if ext:
            return ".jpg" if ext == ".jpe" else ext
    # fallback sur l'URL
    ext2 = os.path.splitext(urlparse(url_fallback).path)[1]
    return ext2 if ext2 else ".jpg"

# =========================
# UI Tkinter
# =========================
root = tk.Tk()
root.title("Téléchargement d'images (HTTP)")

# Références
frame_reference = tk.Frame(root)
frame_reference.pack(padx=12, pady=8)
tk.Label(frame_reference, text="references (séparés par des virgules) : ").grid(row=0, column=0, sticky="w")
entry_reference = tk.Entry(frame_reference, width=60)
entry_reference.grid(row=0, column=1, padx=6)

# Cases à cocher images
frame_images = tk.Frame(root)
frame_images.pack(padx=12, pady=8)
vars_images = []
for i in range(1, 11):
    var = tk.BooleanVar(value=(i == 1))  # coche la 1 par défaut
    vars_images.append(var)
    tk.Checkbutton(frame_images, text=f"Image {i}", variable=var)\
      .grid(row=(i-1)//5, column=(i-1)%5, sticky="w", padx=4, pady=2)

def telecharger_images():
    required_cols = {REFERENCE_PRODUIT, URL_IMAGE}
    missing = required_cols - set(DF.columns)
    if missing:
        messagebox.showerror("Erreur", f"Colonnes manquantes : {missing}")
        return

    references_input = entry_reference.get().strip()
    if not references_input:
        messagebox.showerror("Erreur", "Saisis au moins une référence (séparées par des virgules).")
        return

    images_selected = [i + 1 for i, var in enumerate(vars_images) if var.get()]
    if not images_selected:
        messagebox.showerror("Erreur", "Sélectionne au moins une image à télécharger.")
        return

    # Parse références
    try:
        references = [int(ref.strip()) for ref in references_input.split(",") if ref.strip()]
    except ValueError:
        messagebox.showerror("Erreur", "Chaque référence doit être un entier.")
        return

    n_ok, n_ko = 0, 0
    refs_introuvables = []

    for ref in references:
        rows = DF.loc[DF[REFERENCE_PRODUIT] == ref]
        if rows.empty:
            refs_introuvables.append(ref)
            continue

        row = rows.iloc[0]

        for i in images_selected:
            col = f"Url_image_{i}" if i > 1 else URL_IMAGE
            if col not in DF.columns:
                print(f"[{ref}] Colonne {col} absente → ignorée.")
                continue

            image_url = row[col]
            if not (isinstance(image_url, str) and image_url.startswith("http")):
                print(f"[{ref}] URL invalide pour {col} → ignorée.")
                continue

            try:
                resp = session.get(image_url, timeout=20)
                if resp.status_code == 200:
                    ext = _extension_from_response(resp, image_url)
                    filename = f"{ref}_{i}{ext}"
                    filepath = destination_folder / filename
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    print(f"[OK] {filename}")
                    n_ok += 1
                else:
                    print(f"[KO] {ref} image {i} HTTP {resp.status_code}")
                    n_ko += 1
            except requests.RequestException as e:
                print(f"[KO] {ref} image {i} erreur réseau : {e}")
                n_ko += 1

    message = [
        f"Téléchargement visuels → OK: {n_ok} / KO: {n_ko}",
        f"Dossier : {destination_folder}"
    ]
    if refs_introuvables:
        message.append(f"Introuvables : {', '.join(map(str, refs_introuvables))}")

    messagebox.showinfo("Terminé", "\n".join(message))

btn_telecharger = tk.Button(root, text="Télécharger", command=telecharger_images)
btn_telecharger.pack(pady=12)

root.mainloop()
