from flask import Flask, render_template, url_for, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'nasTajniKljuc'

konekcija = mysql.connector.connect(
    passwd='root',
    user='phpmyadmin',
    database='evidencija_studenata',
    port=3306
)

kursor = konekcija.cursor(dictionary=True)

def ulogovan():
    if 'ulogovani_korisnik' in session:
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        forma = request.form
        upit = "SELECT * FROM korisnici WHERE email=%s"
        vrednost = (forma['email'],)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        print(korisnik)
        if check_password_hash(korisnik['lozinka'], forma['lozinka']):
            session['ulogovani_korisnik'] = str(korisnik)
            return redirect(url_for('studenti'))
        else:
            return render_template('login.html') 

@app.route('/logout')
def logout():
    session.pop('ulogovani_korisnik', None)      
    return redirect(url_for('login'))      

@app.route('/studenti')
def studenti():
    if ulogovan():
        return render_template('studenti.html')
    else:
        return redirect(url_for('login'))

@app.route('/student_novi')
def student_novi():
    return render_template('student_novi.html')

@app.route('/student_izmena')
def student_izmena():
    return render_template('student_izmena.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/predmeti')
def predmeti():
    return render_template('predmeti.html')

@app.route('/predmet_novi')
def predmet_novi():
    return render_template('predmet_novi.html')

@app.route('/predmet_izmena')
def predmet_izmena():
    return render_template('predmet_izmena.html')

@app.route('/korisnici')
def korisnici():
    if ulogovan():
        upit = "SELECT * FROM korisnici"
        kursor.execute(upit)
        korisnici = kursor.fetchall()
        return render_template('korisnici.html', korisnici=korisnici)
    else:
        return redirect(url_for('login'))

@app.route('/korisnik_novi', methods=['GET', 'POST'])
def korisnik_novi():
    if request.method == 'GET':
        return render_template('korisnik_novi.html')
    elif request.method == 'POST':
        forma = request.form
        upit = """ INSERT INTO 
                    korisnici(ime,prezime,email,lozinka)
                    VALUES (%s, %s, %s, %s)    
                 """
        hesovana_lozinka = generate_password_hash(forma['lozinka'])
        vrednosti = (forma['ime'],forma['prezime'],forma['email'],hesovana_lozinka)
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('korisnici'))

@app.route('/korisnik_izmena/<id>', methods=['GET', 'POST'])
def korisnik_izmena(id):
    if request.method == 'GET':
        upit = "SELECT * FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        return render_template('korisnik_izmena.html', korisnik=korisnik)
    elif request.method == 'POST':
        upit = """UPDATE korisnici SET 
                    ime=%s,
                    prezime=%s,
                    email=%s,
                    lozinka=%s
                    WHERE id=%s    
                """
        forma = request.form
        vrednosti = (forma['ime'],forma['prezime'],forma['email'],forma['lozinka'], id)
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('korisnici'))       

@app.route('/korisnik_brisanje/<id>', methods=['POST'])
def korisnik_brisanje(id):
    upit = """
        DELETE FROM korisnici WHERE id=%s
    """
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for('korisnici'))

app.run(debug=True)