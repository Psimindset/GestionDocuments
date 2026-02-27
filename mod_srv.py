import os
import requests
import subprocess, sys, time
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from mod_convert import convertir_word_pdf, convertir_pptx_pdf
from mod_merge   import fusionner_pdf
from mod_sign    import signer_pdf

# Démarrage automatique du DAO
subprocess.Popen([sys.executable, 'mod_dao.py'])
time.sleep(2)
print('DAO démarré sur http://127.0.0.1:5600')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'cle-secrete-documents-2024'
app.config['SECRET_KEY']     = 'cle-session-web'
jwt = JWTManager(app)

URL_DAO = 'http://127.0.0.1:5600/v1/dao'

# Utilitaire : lister les fichiers
def lister_pdfs():
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    outputs = [{'nom': f, 'chemin': f'outputs/{f}'}
               for f in os.listdir('outputs') if f.endswith('.pdf')]
    uploads = [{'nom': f, 'chemin': f'uploads/{f}'}
               for f in os.listdir('uploads') if f.endswith('.pdf')]
    return outputs + uploads

#  ROUTES WEB

@app.route('/', methods=['GET', 'POST'])
def page_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            token = create_access_token(identity=username)
            session['token'] = token
            return redirect(url_for('page_accueil'))
        return render_template('login.html', erreur='Identifiants invalides')
    return render_template('login.html')

@app.route('/accueil')
def page_accueil():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def page_upload():
    # AJOUT : liste des PDFs déjà dans outputs/
    os.makedirs('outputs', exist_ok=True)
    convertis = [{'nom': f, 'chemin': f'outputs/{f}'}
                 for f in os.listdir('outputs') if f.endswith('.pdf')]

    if request.method == 'POST':
        fichier  = request.files['fichier']
        type_src = request.form['type_source']
        os.makedirs('uploads', exist_ok=True)
        chemin = f'uploads/{fichier.filename}'
        fichier.save(chemin)
        token   = session.get('token')
        headers = {'Authorization': f'Bearer {token}'}
        data    = {'chemin': chemin, 'type_source': type_src, 'id_document': 1}
        r       = requests.post('http://127.0.0.1:5800/v1/convert',
                                json=data, headers=headers)
        resultat = r.json()
        if 'chemin_pdf' in resultat:
            nom_pdf = os.path.basename(resultat['chemin_pdf'])
            doc = {'nom': nom_pdf, 'type_fichier': 'pdf',
                   'chemin': resultat['chemin_pdf'], 'proprietaire': 'admin'}
            requests.post('http://127.0.0.1:5800/v1/documents',
                          json=doc, headers=headers)
        return render_template('resultat.html', resultat=resultat)

    return render_template('upload.html', convertis=convertis)

@app.route('/fusion', methods=['GET', 'POST'])
def page_fusion():
    fichiers_dispo = lister_pdfs()
    upload_ok      = None

    # nom auto-généré basé sur la date/heure
    from datetime import datetime
    nom_auto = f'fusion_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

    if request.method == 'POST':
        chemins_selec = request.form.getlist('chemins')
        nom_base   = request.form['nom_sortie'].replace('.pdf', '').strip()
        nom_sortie = f'{nom_base}.pdf'

        if len(chemins_selec) < 2:
            erreur = 'Veuillez sélectionner au moins 2 fichiers PDF.'
            return render_template('fusion.html', fichiers=fichiers_dispo,
                                   erreur=erreur, upload_ok=None,
                                   nom_auto=nom_auto)
        chemin_final = fusionner_pdf(chemins_selec, nom_sortie)
        return render_template('resultat.html',
                               resultat={'message': 'Fusion réussie',
                                         'chemin': chemin_final})
    return render_template('fusion.html', fichiers=fichiers_dispo,
                           erreur=None, upload_ok=upload_ok,
                           nom_auto=nom_auto)

# upload d'un PDF directement depuis la page fusion
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    os.makedirs('uploads', exist_ok=True)
    fichier = request.files.get('fichier_pdf')
    if fichier and fichier.filename.endswith('.pdf'):
        chemin = f'uploads/{fichier.filename}'
        fichier.save(chemin)
        upload_ok = f'{fichier.filename} uploadé avec succès.'
    else:
        upload_ok = 'Erreur : sélectionnez un fichier PDF valide.'
    fichiers_dispo = lister_pdfs()
    return render_template('fusion.html', fichiers=fichiers_dispo,
                           erreur=None, upload_ok=upload_ok)

@app.route('/signature', methods=['GET', 'POST'])
def page_signature():
    tous_pdfs = lister_pdfs()
    if request.method == 'POST':
        chemin        = request.form['chemin']
        nom           = request.form['nom']
        prenom        = request.form['prenom']
        date_sig      = request.form['date_signature']
        signature_img = request.form.get('signature_img', '')

        if not os.path.exists(chemin):
            erreur = f'Fichier introuvable : {chemin}'
            return render_template('signature.html',
                                   fichiers=tous_pdfs, erreur=erreur)

        # AJOUT : passer nom, prenom et image à mod_sign
        chemin_signe = signer_pdf(chemin, nom, prenom, date_sig, signature_img)
        return render_template('resultat.html',
                               resultat={'message': 'Signature apposée',
                                         'chemin': chemin_signe})
    return render_template('signature.html', fichiers=tous_pdfs, erreur=None)

@app.route('/documents')
def page_documents():
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    fichiers_uploads = [{'nom': f, 'dossier': 'uploads', 'chemin': f'uploads/{f}'}
                        for f in os.listdir('uploads')]
    fichiers_outputs = [{'nom': f, 'dossier': 'outputs', 'chemin': f'outputs/{f}'}
                        for f in os.listdir('outputs')]
    return render_template('documents.html',
                           documents=fichiers_uploads + fichiers_outputs)

# téléchargement de fichier
@app.route('/telecharger/<path:chemin>')
def telecharger(chemin):
    dossier     = os.path.dirname(chemin)
    nom         = os.path.basename(chemin)
    dossier_abs = os.path.join(os.getcwd(), dossier)
    return send_file(os.path.join(dossier_abs, nom),
                     as_attachment=True, download_name=nom)

# visualisation dans le navigateur
@app.route('/visualiser/<path:chemin>')
def visualiser(chemin):
    dossier     = os.path.dirname(chemin)
    nom         = os.path.basename(chemin)
    dossier_abs = os.path.join(os.getcwd(), dossier)
    return send_file(os.path.join(dossier_abs, nom),
                     as_attachment=False, download_name=nom)

@app.route('/supprimer/<int:did>', methods=['POST'])
def supprimer_web(did):
    token   = session.get('token', '')
    headers = {'Authorization': f'Bearer {token}'}
    requests.delete(f'http://127.0.0.1:5800/v1/documents/{did}', headers=headers)
    return redirect(url_for('page_documents'))

#  ROUTES API REST

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        token = create_access_token(identity=data['username'])
        return jsonify(access_token=token), 200
    return jsonify({'message': 'Identifiants invalides'}), 401

@app.route('/v1/documents', methods=['POST'])
@jwt_required()
def creer_document():
    data    = request.get_json()
    reponse = requests.post(f'{URL_DAO}/documents', json=data)
    return jsonify(reponse.json()), 201

@app.route('/v1/documents', methods=['GET'])
@jwt_required()
def get_documents():
    reponse = requests.get(f'{URL_DAO}/documents')
    return jsonify(reponse.json()), 200

@app.route('/v1/documents/<int:did>', methods=['DELETE'])
@jwt_required()
def supprimer_document(did):
    reponse = requests.delete(f'{URL_DAO}/documents/{did}')
    return jsonify(reponse.json()), 200

@app.route('/v1/convert', methods=['POST'])
@jwt_required()
def convertir():
    data        = request.get_json()
    chemin_src  = data['chemin']
    type_source = data['type_source']
    if type_source == 'docx':
        chemin_pdf = convertir_word_pdf(chemin_src)
    elif type_source == 'pptx':
        chemin_pdf = convertir_pptx_pdf(chemin_src)
    else:
        return jsonify({'error': 'Type non supporté'}), 415
    conv = {'id_document': data['id_document'], 'type_source': type_source,
            'type_cible': 'pdf', 'chemin_resultat': chemin_pdf}
    requests.post(f'{URL_DAO}/conversions', json=conv)
    return jsonify({'message': 'Conversion réussie', 'chemin_pdf': chemin_pdf}), 200

@app.route('/v1/merge', methods=['POST'])
@jwt_required()
def fusionner():
    data         = request.get_json()
    chemin_final = fusionner_pdf(data['chemins'], data.get('nom_sortie', 'fusion.pdf'))
    return jsonify({'message': 'Fusion réussie', 'chemin': chemin_final}), 200

@app.route('/v1/sign', methods=['POST'])
@jwt_required()
def signer():
    data         = request.get_json()
    chemin_signe = signer_pdf(data['chemin'], data['signataire'], data['date_signature'])
    sig = {'id_document': data['id_document'], 'signataire': data['signataire'],
           'date_signature': data['date_signature'], 'chemin_signe': chemin_signe}
    requests.post(f'{URL_DAO}/signatures', json=sig)
    return jsonify({'message': 'Signature apposée', 'chemin': chemin_signe}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5800, debug=False, use_reloader=False)