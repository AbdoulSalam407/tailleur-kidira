import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

conn = sqlite3.connect('tailleur.db')
cursor = conn.cursor()

# Table réalisations
cursor.execute('''
CREATE TABLE IF NOT EXISTS realisations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    image_url TEXT NOT NULL,
    description TEXT NOT NULL
)
''')

# Table messages contact
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL
)
''')

# Table témoignages clients
cursor.execute('''
CREATE TABLE IF NOT EXISTS temoignages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    message TEXT NOT NULL,
    photo_url TEXT
)
''')

# Table admin (un seul admin pour commencer)
cursor.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Insertion d'un admin par défaut (username: admin, password: admin123)
admin_username = 'admin'
admin_password_hashed = hash_password('admin123')

cursor.execute("SELECT * FROM admin WHERE username = ?", (admin_username,))
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)",
                   (admin_username, admin_password_hashed))
    print("Admin par défaut créé : admin / admin123")

conn.commit()
conn.close()
print("Base de données initialisée avec succès.")
