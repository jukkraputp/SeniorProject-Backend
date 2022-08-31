import firebase_admin
from firebase_admin import credentials, db, firestore, auth

# Fetch the service account key JSON file contents
cred = credentials.Certificate('serviceAccountKey.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://seniorproject-3df90-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# As an admin, the app has access to read and write all data, regardless of Security Rules
realtime_database: db
firebase_firestore = firestore.client()
firebase_auth = auth
