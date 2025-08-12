import mysql.connector
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Remplace ces valeurs par tes infos MySQL
conn = mysql.connector.connect(
    host='mysql-abdoul-salam-diallo.alwaysdata.net',
    user='405601',
    password='Asd781209169#',
    database='abdoul-salam-diallo_tailleur_db'
)
cursor = conn.cursor()

# Supprimer si tu veux repartir de zéro
cursor.execute("DROP TABLE IF EXISTS realisations")
cursor.execute("DROP TABLE IF EXISTS messages")
cursor.execute("DROP TABLE IF EXISTS temoignages")
cursor.execute("DROP TABLE IF EXISTS admin")

# Créer la table avec prix
cursor.execute('''
CREATE TABLE IF NOT EXISTS realisations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    prix FLOAT NOT NULL
)
''')

# Table messages contact
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL
)
''')

# Table témoignages clients
cursor.execute('''
CREATE TABLE IF NOT EXISTS temoignages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    photo_url VARCHAR(255)
)
''')

# Table admin (un seul admin pour commencer)
cursor.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
)
''')

# Insertion d'un admin par défaut (username: admin, password: admin123)
admin_username = 'admin'
admin_password_hashed = hash_password('admin123')

cursor.execute("SELECT * FROM admin WHERE username = %s", (admin_username,))
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)",
                   (admin_username, admin_password_hashed))
    print("Admin par défaut créé : admin / admin123")

conn.commit()
conn.close()
print("Base de données MySQL initialisée avec succès.")
