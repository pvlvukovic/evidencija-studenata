from flask import Flask, render_template, url_for, request, redirect
import mysql.connector

app = Flask(__name__)

konekcija = mysql.connector.connect(
    passwd='root',
    user='phpmyadmin',
    database='evidencija_studenata',
    port=3306
)

kursor = konekcija.cursor(dictionary=True)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/studenti')
def studenti():
    return render_template('studenti.html')

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
    upit = "SELECT * FROM korisnici"
    kursor.execute(upit)
    korisnici = kursor.fetchall()
    return render_template('korisnici.html', korisnici=korisnici)

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
        vrednosti = (forma['ime'],forma['prezime'],forma['email'],forma['lozinka'])
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