import os
import base64
import io
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image as PILImage

OUTPUT_DIR = 'outputs'

def _assurer_dossier():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def _creer_page_signature(nom: str, prenom: str,
                          date_signature: str,
                          signature_img: str = '') -> str:
    _assurer_dossier()
    chemin_temp = os.path.join(OUTPUT_DIR, '_signature_temp.pdf')
    c = canvas.Canvas(chemin_temp, pagesize=letter)
    largeur, hauteur = letter

    # Cadre de signature
    c.rect(30, 20, 380, 120, stroke=1, fill=0)

    # Image graphique du canvas
    if signature_img and signature_img.startswith('data:image'):
        try:
            header, data = signature_img.split(',', 1)
            img_bytes    = base64.b64decode(data)
            img_pil      = PILImage.open(io.BytesIO(img_bytes)).convert('RGBA')

            fond = PILImage.new('RGBA', img_pil.size, (255, 255, 255, 255))
            fond.paste(img_pil, mask=img_pil.split()[3])
            img_final = fond.convert('RGB')

            chemin_img = os.path.join(OUTPUT_DIR, '_sig_img_temp.png')
            img_final.save(chemin_img)

            c.drawImage(chemin_img, 35, 50, width=200, height=85,
                        preserveAspectRatio=True)
            os.remove(chemin_img)
        except Exception as e:
            print(f'Image signature ignorée : {e}')

    # nom / prénom / date
    c.setFont('Helvetica-Bold', 10)
    c.drawString(250, 115, 'Signé électroniquement par :')
    c.setFont('Helvetica', 10)
    c.drawString(250, 100, f'{prenom} {nom}')
    c.drawString(250, 85,  f'Date : {date_signature}')

    # Ligne séparation
    c.line(240, 130, 240, 25)

    c.save()
    return chemin_temp
# signature sur tous les pages du pdf
def signer_pdf(chemin_pdf: str, nom: str, prenom: str,
               date_signature: str, signature_img: str = '') -> str:
    _assurer_dossier()
    nom_base     = os.path.splitext(os.path.basename(chemin_pdf))[0]
    chemin_signe = os.path.join(OUTPUT_DIR, f'{nom_base}_signe.pdf')

    chemin_sig = _creer_page_signature(nom, prenom, date_signature, signature_img)

    with open(chemin_pdf, 'rb') as f_orig, \
         open(chemin_sig,  'rb') as f_sig:

        lecteur_orig = PyPDF2.PdfReader(f_orig)
        lecteur_sig  = PyPDF2.PdfReader(f_sig)
        ecrivain     = PyPDF2.PdfWriter()
        page_sig     = lecteur_sig.pages[0]

        for page in lecteur_orig.pages:
            page.merge_page(page_sig)
            ecrivain.add_page(page)

        with open(chemin_signe, 'wb') as f_out:
            ecrivain.write(f_out)

    os.remove(chemin_sig)
    print(f'PDF signé : {chemin_signe}')
    return chemin_signe
# Test local
if __name__ == '__main__':
    chemin = input('Chemin du PDF : ')
    nom    = input('Nom : ')
    prenom = input('Prénom : ')
    date   = input('Date (AAAA-MM-JJ) : ')
    print(signer_pdf(chemin, nom, prenom, date))