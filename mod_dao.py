import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# Connexion
def get_connection():
    conn    = sqlite3.connect('documents.sdb')
    curseur = conn.cursor()
    return conn, curseur

def fermer_close(conn):
    conn.close()

def creer_tables():
    conn, curseur = get_connection()
    curseur.execute('''CREATE TABLE IF NOT EXISTS document(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT, type_fichier TEXT,
        chemin TEXT, proprietaire TEXT)''')
    curseur.execute('''CREATE TABLE IF NOT EXISTS conversion(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_document INTEGER, type_source TEXT,
        type_cible TEXT, chemin_resultat TEXT)''')
    curseur.execute('''CREATE TABLE IF NOT EXISTS signature(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_document INTEGER, signataire TEXT,
        date_signature TEXT, chemin_signe TEXT)''')
    conn.commit()
    fermer_close(conn)

# CRUD Document
@app.route('/v1/dao/documents', methods=['POST'])
def inserer_document():
    data = request.get_json()
    conn, curseur = get_connection()
    curseur.execute(
        'INSERT INTO document(nom,type_fichier,chemin,proprietaire) VALUES(?,?,?,?)',
        [data['nom'], data['type_fichier'], data['chemin'], data['proprietaire']])
    conn.commit()
    pid = curseur.lastrowid
    fermer_close(conn)
    return jsonify({'message': 'document inséré', 'id': pid}), 201

@app.route('/v1/dao/documents', methods=['GET'])
def get_documents():
    listing = []
    conn, curseur = get_connection()
    curseur.execute('SELECT id,nom,type_fichier,chemin,proprietaire FROM document')
    for rec in curseur:
        listing.append({'id': rec[0], 'nom': rec[1],
                        'type_fichier': rec[2], 'chemin': rec[3],
                        'proprietaire': rec[4]})
    fermer_close(conn)
    return jsonify({'documents': listing}), 200

@app.route('/v1/dao/documents/<int:did>', methods=['DELETE'])
def supprimer_document(did):
    conn, curseur = get_connection()
    curseur.execute('DELETE FROM document WHERE id=?', [did])
    conn.commit()
    fermer_close(conn)
    return jsonify({'message': 'document supprimé'}), 200

# Conversions
@app.route('/v1/dao/conversions', methods=['POST'])
def inserer_conversion():
    data = request.get_json()
    conn, curseur = get_connection()
    curseur.execute(
        'INSERT INTO conversion(id_document,type_source,type_cible,chemin_resultat) VALUES(?,?,?,?)',
        [data['id_document'], data['type_source'], data['type_cible'], data['chemin_resultat']])
    conn.commit()
    cid = curseur.lastrowid
    fermer_close(conn)
    return jsonify({'message': 'conversion enregistrée', 'id': cid}), 201

# Signatures
@app.route('/v1/dao/signatures', methods=['POST'])
def inserer_signature():
    data = request.get_json()
    conn, curseur = get_connection()
    curseur.execute(
        'INSERT INTO signature(id_document,signataire,date_signature,chemin_signe) VALUES(?,?,?,?)',
        [data['id_document'], data['signataire'], data['date_signature'], data['chemin_signe']])
    conn.commit()
    sid = curseur.lastrowid
    fermer_close(conn)
    return jsonify({'message': 'signature enregistrée', 'id': sid}), 201

if __name__ == '__main__':
    creer_tables()
    app.run(debug=True, port=5600, use_reloader=False)