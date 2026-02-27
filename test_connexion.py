"""
Lancer ce fichier pour diagnostiquer le problème
python test_connexion.py
"""
import requests

print('=== Test 1 : Service sur port 5800 ===')
try:
    r = requests.get('http://127.0.0.1:5800/')
    print(f'Statut     : {r.status_code}')
    print(f'Réponse    : {r.text}')
except requests.exceptions.ConnectionError:
    print('ECHEC : rien ne tourne sur le port 5800')
    print('→ Lance python mod_srv.py dans un autre terminal')

print()
print('=== Test 2 : DAO sur port 5600 ===')
try:
    r = requests.get('http://127.0.0.1:5600/')
    print(f'Statut     : {r.status_code}')
    print(f'Réponse    : {r.text}')
except requests.exceptions.ConnectionError:
    print('ECHEC : rien ne tourne sur le port 5600')

print()
print('=== Test 3 : Login ===')
try:
    r = requests.post('http://127.0.0.1:5800/login',
                      json={'username': 'admin', 'password': 'admin123'})
    print(f'Statut     : {r.status_code}')
    print(f'Réponse    : {r.text}')
except requests.exceptions.ConnectionError:
    print('ECHEC : connexion refusée')

print()
print('=== Test 4 : Imports ===')
try:
    from mod_convert import convertir_word_pdf
    print('mod_convert  : OK')
except ImportError as e:
    print(f'mod_convert  : ERREUR → {e}')

try:
    from mod_merge import fusionner_pdf
    print('mod_merge    : OK')
except ImportError as e:
    print(f'mod_merge    : ERREUR → {e}')

try:
    from mod_sign import signer_pdf
    print('mod_sign     : OK')
except ImportError as e:
    print(f'mod_sign     : ERREUR → {e}')

try:
    from flask_jwt_extended import JWTManager
    print('flask-jwt    : OK')
except ImportError as e:
    print(f'flask-jwt    : ERREUR → {e}')

try:
    import PyPDF2
    print('PyPDF2       : OK')
except ImportError as e:
    print(f'PyPDF2       : ERREUR → {e}')

try:
    from docx import Document
    print('python-docx  : OK')
except ImportError as e:
    print(f'python-docx  : ERREUR → {e}')

try:
    from pptx import Presentation
    print('python-pptx  : OK')
except ImportError as e:
    print(f'python-pptx  : ERREUR → {e}')

try:
    from reportlab.pdfgen import canvas
    print('reportlab    : OK')
except ImportError as e:
    print(f'reportlab    : ERREUR → {e}')