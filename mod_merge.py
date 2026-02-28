import os
import PyPDF2

OUTPUT_DIR = 'outputs'
def _assurer_dossier():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
# Fusion de PDFs
def fusionner_pdf(chemins: list, nom_sortie: str = 'fusion.pdf') -> str:

    _assurer_dossier()

    chemin_final = os.path.join(OUTPUT_DIR, nom_sortie)
    fusionneur = PyPDF2.PdfMerger()

    for chemin in chemins:
        if not os.path.exists(chemin):
            print(f'Fichier introuvable : {chemin}')
            continue
        if not chemin.lower().endswith('.pdf'):
            print(f'Fichier ignoré (pas un PDF) : {chemin}')
            continue

        fusionneur.append(chemin)
        print(f'Ajouté : {chemin}')

    # Écrire le PDF fusionné
    with open(chemin_final, 'wb') as f:
        fusionneur.write(f)

    fusionneur.close()
    print(f'PDF fusionné : {chemin_final}')
    return chemin_final

# Extraire des pages spécifiques
def extraire_pages(chemin_pdf: str, pages: list, nom_sortie: str = 'extrait.pdf') -> str:

    _assurer_dossier()

    chemin_final = os.path.join(OUTPUT_DIR, nom_sortie)

    with open(chemin_pdf, 'rb') as f:
        lecteur = PyPDF2.PdfReader(f)
        ecrivain = PyPDF2.PdfWriter()

        for num_page in pages:
            if num_page < len(lecteur.pages):
                ecrivain.add_page(lecteur.pages[num_page])
                print(f'Page {num_page + 1} ajoutée')
            else:
                print(f'Page {num_page + 1} inexistante, ignorée')

        with open(chemin_final, 'wb') as sortie:
            ecrivain.write(sortie)

    print(f'Extraction terminée : {chemin_final}')
    return chemin_final
# Test local
if __name__ == '__main__':
    print('1. Fusionner des PDFs')
    print('2. Extraire des pages')
    choix = input('Choix : ')

    if choix == '1':
        chemins_str = input('Chemins PDF séparés par virgule : ')
        chemins = [c.strip() for c in chemins_str.split(',')]
        nom = input('Nom du fichier de sortie (ex: fusion.pdf) : ')
        print(fusionner_pdf(chemins, nom))

    elif choix == '2':
        chemin = input('Chemin du PDF source : ')
        pages_str = input('Numéros de pages séparés par virgule (commence à 1) : ')
        pages = [int(p.strip()) - 1 for p in pages_str.split(',')]
        nom = input('Nom du fichier de sortie : ')
        print(extraire_pages(chemin, pages, nom))