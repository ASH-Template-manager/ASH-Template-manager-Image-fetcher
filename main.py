from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import requests
from bs4 import BeautifulSoup

# Use a service account
cred = credentials.Certificate('./service-account-firestore.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)


@app.route('/api/metas/sync')
def hello_world():
    db = firestore.client()
    users_ref = db.collection(u'templates')
    docs = users_ref.stream()

    for idx, doc in enumerate(docs):
        doc_dict = doc.to_dict()
        res = requests.get(doc_dict['refLink'])
        soup = BeautifulSoup(res.text)
        preview_container = soup.find('div', {'class': 'item-preview'})
        preview_soup = BeautifulSoup(str(preview_container))
        img = preview_soup.find('img')
        payload = {
            'img': img.attrs['src'],
            'tags': []
        }
        tags_container = soup.find('span', {'class': 'meta-attributes__attr-tags'})
        tags = BeautifulSoup(str(tags_container)).findAll('a')
        for t in tags:
            payload['tags'].append(t.text) if t.text not in payload['tags'] else None
        doc_ref = db.collection('templates').document(doc.id)
        doc_ref.set(payload, merge=True)
        print('{} treated'.format(idx + 1))
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run()
