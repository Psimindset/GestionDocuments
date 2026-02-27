import unittest
import requests

BASE    = 'http://127.0.0.1:5800'
HEADERS = {}

class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Obtenir le token avant tous les tests"""
        r = requests.post(f'{BASE}/login',
                json={'username': 'admin', 'password': 'admin123'})
        token = r.json()['access_token']
        HEADERS['Authorization'] = f'Bearer {token}'

    def test_01_login_succes(self):
        r = requests.post(f'{BASE}/login',
                json={'username': 'admin', 'password': 'admin123'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('access_token', r.json())

    def test_02_login_echec(self):
        r = requests.post(f'{BASE}/login',
                json={'username': 'faux', 'password': 'faux'})
        self.assertEqual(r.status_code, 401)

    def test_03_creer_document(self):
        data = {'nom': 'rapport.docx', 'type_fichier': 'docx',
                'chemin': 'uploads/rapport.docx', 'proprietaire': 'admin'}
        r = requests.post(f'{BASE}/v1/documents', json=data, headers=HEADERS)
        self.assertEqual(r.status_code, 201)
        self.assertIn('id', r.json())

    def test_04_lister_documents(self):
        r = requests.get(f'{BASE}/v1/documents', headers=HEADERS)
        self.assertEqual(r.status_code, 200)
        self.assertIn('documents', r.json())

    def test_05_sans_token(self):
        r = requests.get(f'{BASE}/v1/documents')
        self.assertEqual(r.status_code, 401)

if __name__ == '__main__':
    unittest.main()