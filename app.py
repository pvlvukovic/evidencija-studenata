from flask import Flask, render_template, url_for

app = Flask(__name__)

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
    return render_template('korisnici.html')

@app.route('/korisnik_novi')
def korisnik_novi():
    return render_template('korisnik_novi.html')

@app.route('/korisnik_izmena')
def korisnik_izmena():
    return render_template('korisnik_izmena.html')

app.run(debug=True)