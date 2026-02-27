import requests
from mod_modele import Document


BASE = 'http://127.0.0.1:5800'

def login():
    reponse = requests.post(f'{BASE}/login',
                json={'username': 'admin', 'password': 'admin123'})
    token = reponse.json()['access_token']
    print('=== Autorisation accordée ===')
    print(f'Token : {token}')
    print('==============================\n')
    return {'Authorization': f'Bearer {token}'}

def main():
    headers = login()

    print('1. Lister documents')
    print('2. Convertir Word/PPTX → PDF')
    print('3. Fusionner PDFs')
    print('4. Signer un PDF')
    print('5. Supprimer un document')
    choix = input('Choix : ')

    if choix == '1':
        r = requests.get(f'{BASE}/v1/documents', headers=headers)
        for doc in r.json()['documents']:
            print(f"[{doc['id']}] {doc['nom']} ({doc['type_fichier']})")

    elif choix == '2':
        chemin     = input('Chemin du fichier (docx ou pptx) : ')
        type_src   = input('Type source (docx/pptx) : ')
        id_doc     = int(input('ID document : '))
        data = {'chemin': chemin, 'type_source': type_src, 'id_document': id_doc}
        r = requests.post(f'{BASE}/v1/convert', json=data, headers=headers)
        print(r.json())

    elif choix == '3':
        chemins    = input('Chemins PDF séparés par virgule : ').split(',')
        nom_sortie = input('Nom du fichier de sortie : ')
        data = {'chemins': [c.strip() for c in chemins], 'nom_sortie': nom_sortie}
        r = requests.post(f'{BASE}/v1/merge', json=data, headers=headers)
        print(r.json())

    elif choix == '4':
        chemin     = input('Chemin du PDF à signer : ')
        signataire = input('Nom du signataire : ')
        date_sig   = input('Date (AAAA-MM-JJ) : ')
        id_doc     = int(input('ID document : '))
        data = {'chemin': chemin, 'signataire': signataire,
                'date_signature': date_sig, 'id_document': id_doc}
        r = requests.post(f'{BASE}/v1/sign', json=data, headers=headers)
        print(r.json())

    elif choix == '5':
        did = int(input('ID du document à supprimer : '))
        r = requests.delete(f'{BASE}/v1/documents/{did}', headers=headers)
        print(r.json())

    print('\nStatut :', r.status_code)

if __name__ == '__main__':
    main()