from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib

import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_a_personnaliser'  # indispensable pour les sessions

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Connexion à la base de données MySQL
def get_db_connection():
    conn = mysql.connector.connect(
        host='mysql-abdoul-salam-diallo.alwaysdata.net',
        user='405601',
        password='Asd781209169#',
        database='abdoul-salam-diallo_tailleur_db'
    )
    return conn

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/galerie')
def galerie():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM realisations")
    realisations = cursor.fetchall()
    conn.close()
    return render_template('galerie.html', realisations=realisations)

@app.route('/admin_galerie')
def admin_galerie():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM realisations")
    realisations = cursor.fetchall()
    conn.close()
    return render_template('admin_galerie.html', realisations=realisations)

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        prix = request.form['prix']
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO realisations (titre, image_url, description, prix) VALUES (%s, %s, %s, %s)",
                           (titre, filename, description, prix))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_galerie'))
        else:
            return "Erreur : Veuillez choisir une image au format .jpg, .jpeg, .png ou .gif"
    return render_template('ajouter.html')

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM realisations WHERE id = %s", (id,))
    realisation = cursor.fetchone()

    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        prix = request.form['prix']
        cursor.execute("UPDATE realisations SET titre = %s, description = %s, prix = %s WHERE id = %s",
                       (titre, description, prix, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_galerie'))
    
    conn.close()
    return render_template('modifier.html', realisation=realisation)

@app.route('/supprimer/<int:id>')
def supprimer(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM realisations WHERE id = %s", (id,))
    realisation = cursor.fetchone()

    if realisation and realisation["image_url"]:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], realisation["image_url"])
        if os.path.exists(image_path):
            os.remove(image_path)

    cursor.execute("DELETE FROM realisations WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_galerie'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (nom, email, message) VALUES (%s, %s, %s)",
                       (nom, email, message))
        conn.commit()
        conn.close()

        return render_template('contact.html', success=True)
    return render_template('contact.html')

@app.route('/temoignages')
def temoignages():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM temoignages")
    temoignages = cursor.fetchall()
    conn.close()
    return render_template('temoignages.html', temoignages=temoignages)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hashed = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", 
                       (username, password_hashed))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Identifiants incorrects", "danger")

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', username=session.get('admin_username'))

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/messages')
def admin_messages():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    messages = cursor.fetchall()
    conn.close()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/messages/supprimer/<int:id>')
def supprimer_message(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_messages'))

@app.route('/admin/temoignages')
def admin_temoignages():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM temoignages ORDER BY id DESC")
    temoignages = cursor.fetchall()
    conn.close()
    return render_template('admin_temoignages.html', temoignages=temoignages)

@app.route('/admin/temoignages/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_temoignage(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM temoignages WHERE id = %s", (id,))
    temoignage = cursor.fetchone()

    if request.method == 'POST':
        nom = request.form['nom']
        message = request.form['message']
        photo = request.files['photo']

        photo_filename = temoignage['photo_url']
        if photo and photo.filename != "":
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        cursor.execute("UPDATE temoignages SET nom = %s, message = %s, photo_url = %s WHERE id = %s",
                       (nom, message, photo_filename, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_temoignages'))

    conn.close()
    return render_template('modifier_temoignage.html', temoignage=temoignage)

@app.route('/admin/temoignages/supprimer/<int:id>')
def supprimer_temoignage(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM temoignages WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_temoignages'))


@app.route('/ajouter-temoignage', methods=['GET', 'POST'])
def ajouter_temoignage():
    if request.method == 'POST':
        nom = request.form['nom']
        message = request.form['message']
        photo = request.files['photo']

        photo_filename = ""
        if photo and photo.filename != "":
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO temoignages (nom, message, photo_url) VALUES (%s, %s, %s)",
                       (nom, message, photo_filename))
        conn.commit()
        conn.close()

        return render_template('ajouter_temoignage.html', success=True)
    
    return render_template('ajouter_temoignage.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

