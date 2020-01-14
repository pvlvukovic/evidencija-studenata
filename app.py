from flask import Flask, render_template, url_for, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "nasTajniKljuc"

konekcija = mysql.connector.connect(
    passwd="root", user="phpmyadmin", database="evidencija_studenata", port=3306, auth_plugin='mysql_native_password'
)

kursor = konekcija.cursor(dictionary=True)


def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        forma = request.form
        upit = "SELECT * FROM korisnici WHERE email=%s"
        vrednost = (forma["email"],)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        print(korisnik)
        if check_password_hash(korisnik["lozinka"], forma["lozinka"]):
            session["ulogovani_korisnik"] = str(korisnik)
            return redirect(url_for("studenti"))
        else:
            return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("ulogovani_korisnik", None)
    return redirect(url_for("login"))


@app.route("/studenti")
def studenti():
    if ulogovan():
        upit = "SELECT * FROM studenti"
        kursor.execute(upit)
        studenti = kursor.fetchall()
        return render_template("studenti.html", studenti=studenti)
    else:
        return redirect(url_for("login"))


@app.route("/student_novi", methods=["GET", "POST"])
def student_novi():
    if ulogovan():
        if request.method == 'GET':
            return render_template("student_novi.html")
        elif request.method == 'POST':
            upit = """
                INSERT INTO studenti
                (ime, ime_roditelja, prezime, broj_indeksa, godina_studija, jmbg, datum_rodjenja, espb, prosek_ocena, broj_telefona, email)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            forma = request.form
            vrednosti = (
                forma['ime'], 
                forma['ime_roditelja'], 
                forma['prezime'], 
                forma['broj_indeksa'],
                forma['godina_studija'],
                forma['jmbg'],
                forma['datum_rodjenja'],
                0,
                0,
                forma['broj_telefona'],
                forma['email']
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for('studenti'))
    else:
        return redirect(url_for('login'))

@app.route("/student_izmena/<id>", methods=["GET", "POST"])
def student_izmena(id):
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM studenti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            student = kursor.fetchone()
            return render_template("student_izmena.html", student=student)
        elif request.method == "POST":
            upit = """
                UPDATE studenti SET
                ime=%s,
                ime_roditelja=%s,
                prezime=%s,
                broj_indeksa=%s,
                godina_studija=%s,
                jmbg=%s,
                datum_rodjenja=%s,
                broj_telefona=%s,
                email=%s
                WHERE id=%s
            """
            forma = request.form
            vrednosti = (
                forma['ime'], 
                forma['ime_roditelja'], 
                forma['prezime'], 
                forma['broj_indeksa'],
                forma['godina_studija'],
                forma['jmbg'],
                forma['datum_rodjenja'],
                forma['broj_telefona'],
                forma['email'],
                id
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for('studenti'))
    else:
        return redirect(url_for('login'))


@app.route("/student/<id>")
def student(id):
    if ulogovan():
        upit = "SELECT * FROM studenti WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        student = kursor.fetchone()
        upit = "SELECT * FROM predmeti"
        kursor.execute(upit)
        predmeti = kursor.fetchall()
        upit = """
            SELECT *
            FROM predmeti
            JOIN ocene 
            ON predmeti.id=ocene.predmet_id
            WHERE ocene.student_id=%s
        """
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        ocene = kursor.fetchall()
        return render_template("student.html", student=student, predmeti=predmeti, ocene=ocene)
    else:
        return redirect(url_for('login'))

@app.route("/student_brisanje/<id>")
def student_brisanje(id):
    if ulogovan():
        upit = "DELETE FROM studenti WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()
        return redirect(url_for("studenti"))
    else:
        return redirect(url_for("login"))

@app.route("/predmeti")
def predmeti():
    if ulogovan():
        upit = "SELECT * FROM predmeti"
        kursor.execute(upit)
        predmeti = kursor.fetchall()
        return render_template("predmeti.html", predmeti=predmeti)
    else:
        return redirect(url_for("login"))


@app.route("/predmet_novi", methods=["GET", "POST"])
def predmet_novi():
    if ulogovan():
        if request.method == "GET":
            return render_template("predmet_novi.html")
        elif request.method == "POST":
            forma = request.form
            vrednosti = (
                forma["sifra"],
                forma["naziv"],
                forma["espb"],
                forma["godina_studija"],
                forma["obavezni_izborni"],
            )
            upit = """
                INSERT INTO predmeti
                (sifra, naziv, espb, godina_studija, obavezni_izborni)
                VALUES
                (%s, %s, %s, %s, %s)
            """
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("predmeti"))
    else:
        return redirect(url_for("login"))


@app.route("/predmet_izmena/<id>", methods=["GET", "POST"])
def predmet_izmena(id):
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM predmeti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            predmet = kursor.fetchone()
            return render_template("predmet_izmena.html", predmet=predmet)
        elif request.method == "POST":
            forma = request.form
            vrednosti = (
                forma["sifra"],
                forma["naziv"],
                forma["espb"],
                forma["godina_studija"],
                forma["obavezni_izborni"],
                id,
            )
            upit = """
                UPDATE predmeti 
                SET
                sifra=%s,
                naziv=%s,
                espb=%s,
                godina_studija=%s,
                obavezni_izborni=%s
                WHERE
                id=%s
            """
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("predmeti"))
    else:
        return redirect(url_for("login"))


@app.route("/predmet_brisanje/<id>")
def predmet_brisanje(id):
    if ulogovan():
        upit = "DELETE FROM predmeti WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()
        return redirect(url_for("predmeti"))
    else:
        return redirect(url_for("login"))


@app.route("/korisnici")
def korisnici():
    if ulogovan():
        upit = "SELECT * FROM korisnici"
        kursor.execute(upit)
        korisnici = kursor.fetchall()
        return render_template("korisnici.html", korisnici=korisnici)
    else:
        return redirect(url_for("login"))


@app.route("/korisnik_novi", methods=["GET", "POST"])
def korisnik_novi():
    if ulogovan():
        if request.method == "GET":
            return render_template("korisnik_novi.html")
        elif request.method == "POST":
            forma = request.form
            upit = """ INSERT INTO 
                        korisnici(ime,prezime,email,lozinka)
                        VALUES (%s, %s, %s, %s)    
                    """
            hesovana_lozinka = generate_password_hash(forma["lozinka"])
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                hesovana_lozinka,
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for("login"))


@app.route("/korisnik_izmena/<id>", methods=["GET", "POST"])
def korisnik_izmena(id):
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM korisnici WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            korisnik = kursor.fetchone()
            return render_template("korisnik_izmena.html", korisnik=korisnik)
        elif request.method == "POST":
            upit = """UPDATE korisnici SET 
                        ime=%s,
                        prezime=%s,
                        email=%s,
                        lozinka=%s
                        WHERE id=%s    
                    """
            forma = request.form
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                forma["lozinka"],
                id,
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for("login"))


@app.route("/korisnik_brisanje/<id>", methods=["POST"])
def korisnik_brisanje(id):
    if ulogovan():
        upit = """
            DELETE FROM korisnici WHERE id=%s
        """
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()
        return redirect(url_for("korisnici"))
    else:
        return redirect(url_for("login"))

@app.route("/ocena_nova/<id>", methods=["POST"])
def ocena_nova(id):
    if ulogovan():
        # Dodavanje ocene u tabelu ocene
        upit = """
            INSERT INTO ocene(student_id, predmet_id, ocena, datum)
            VALUES(%s, %s, %s, %s)
        """
        forma = request.form
        vrednosti = (id, forma['predmet_id'], forma['ocena'], forma['datum'])
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        # Racunanje proseka ocena
        upit = "SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        prosek_ocena = kursor.fetchone()
        # Racunanje ukupno espb
        upit = "SELECT SUM(espb) AS rezultat FROM predmeti WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        espb = kursor.fetchone()
        # Update tabele student
        upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
        vrednosti = (espb['rezultat'], prosek_ocena['rezultat'], id)
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('student', id=id))
    else:
        return redirect(url_for('login'))

@app.route('/ocena_brisanje/<student_id>/<ocena_id>')
def ocena_brisanje(student_id, ocena_id):
    if ulogovan():
        upit = "DELETE FROM ocene WHERE id=%s"
        vrednost=(ocena_id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()
        # Racunanje proseka ocena
        upit = "SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s"
        vrednost = (student_id,)
        kursor.execute(upit, vrednost)
        prosek_ocena = kursor.fetchone()
        # Racunanje ukupno espb
        upit = "SELECT SUM(espb) AS rezultat FROM predmeti WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"
        vrednost = (student_id,)
        kursor.execute(upit, vrednost)
        espb = kursor.fetchone()
        # Update tabele student
        upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
        vrednosti = (espb['rezultat'], prosek_ocena['rezultat'], id)
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('student', id=student_id))
    else:
        return redirect(url_for('login'))

app.run(debug=True)
