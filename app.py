from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib


import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_a_personnaliser'  # indispensable pour les sessions

# Dossier pour enregistrer les images
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Vérifie l’extension du fichier
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('tailleur.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/galerie')
def galerie():
    conn = get_db_connection()
    realisations = conn.execute("SELECT * FROM realisations").fetchall()
    conn.close()
    return render_template('galerie.html', realisations=realisations)

# --- Ajouter une réalisation avec image uploadée ---
@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db_connection()
            conn.execute("INSERT INTO realisations (titre, image_url, description) VALUES (?, ?, ?)",
                         (titre, filename, description))
            conn.commit()
            conn.close()
            return redirect(url_for('galerie'))
        else:
            return "Erreur : Veuillez choisir une image au format .jpg, .jpeg, .png ou .gif"
    return render_template('ajouter.html')

# --- Modifier une réalisation (sans changer l'image pour l'instant) ---
@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    conn = get_db_connection()
    realisation = conn.execute("SELECT * FROM realisations WHERE id = ?", (id,)).fetchone()
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        conn.execute("UPDATE realisations SET titre = ?, description = ? WHERE id = ?",
                     (titre, description, id))
        conn.commit()
        conn.close()
        return redirect(url_for('galerie'))
    conn.close()
    return render_template('modifier.html', realisation=realisation)

# --- Supprimer une réalisation ---
@app.route('/supprimer/<int:id>')
def supprimer(id):
    conn = get_db_connection()
    realisation = conn.execute("SELECT * FROM realisations WHERE id = ?", (id,)).fetchone()

    # Supprimer l'image liée
    if realisation and realisation["image_url"]:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], realisation["image_url"])
        if os.path.exists(image_path):
            os.remove(image_path)

    conn.execute("DELETE FROM realisations WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('galerie'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        conn.execute("INSERT INTO messages (nom, email, message) VALUES (?, ?, ?)",
                     (nom, email, message))
        conn.commit()
        conn.close()

        return render_template('contact.html', success=True)
    return render_template('contact.html')


@app.route('/temoignages')
def temoignages():
    conn = get_db_connection()
    temoignages = conn.execute("SELECT * FROM temoignages").fetchall()
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
        admin = conn.execute("SELECT * FROM admin WHERE username = ? AND password = ?", 
                             (username, password_hashed)).fetchone()
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
    messages = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/messages/supprimer/<int:id>')
def supprimer_message(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM messages WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_messages'))

@app.route('/admin/temoignages')
def admin_temoignages():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    temoignages = conn.execute("SELECT * FROM temoignages ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin_temoignages.html', temoignages=temoignages)

@app.route('/admin/temoignages/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_temoignage(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    temoignage = conn.execute("SELECT * FROM temoignages WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        nom = request.form['nom']
        message = request.form['message']
        photo = request.files['photo']

        photo_filename = temoignage['photo_url']
        if photo and photo.filename != "":
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        conn.execute("UPDATE temoignages SET nom = ?, message = ?, photo_url = ? WHERE id = ?",
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
    conn.execute("DELETE FROM temoignages WHERE id = ?", (id,))
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
        conn.execute("INSERT INTO temoignages (nom, message, photo_url) VALUES (?, ?, ?)",
                     (nom, message, photo_filename))
        conn.commit()
        conn.close()

        return render_template('ajouter_temoignage.html', success=True)
    
    return render_template('ajouter_temoignage.html')




if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

