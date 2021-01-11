from flask import Flask, render_template, url_for, request, redirect, session, Response
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import io
import csv
import ast
from flask_mail import Mail, Message

app = Flask(__name__)

app.secret_key = "nasTajniKljuc"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "evidencija.atvss@gmail.com"
app.config["MAIL_PASSWORD"] = "atvss123loz"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

konekcija = mysql.connector.connect(
    passwd="rootroot",
    user="root",
    database="evidencija_studenata",
    port=3306,
    auth_plugin="mysql_native_password",
)

kursor = konekcija.cursor(dictionary=True)

UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False


def rola():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).pop("rola")


def send_email(ime, prezime, email, lozinka):
    msg = Message(
        subject="Korisnički nalog",
        sender="ATVSS Evidencija studenata",
        recipients=["pvl.vkvc@gmail.com"],
    )
    msg.html = render_template("email.html", ime=ime, prezime=prezime, lozinka=lozinka)
    mail.send(msg)
    return "Sent"


@app.route("/", methods=["GET"])
def home():
    if ulogovan():
        return redirect(url_for("studenti"))
    else:
        return redirect(url_for("login"))


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
        args = request.args.to_dict()

        strana = request.args.get("page", "1")
        offset = int(strana) * 10 - 10

        s_ime = "%%"
        s_prezime = "%%"
        s_broj_indeksa = "%%"
        s_godina_studija = "%%"
        s_espb_od = "0"
        s_espb_do = "180"
        s_prosek_ocena_od = "0"
        s_prosek_ocena_do = "10"

        order_by = "id"
        order_type = "asc"

        if "order_by" in args:
            order_by = args["order_by"].lower()
            if (
                "prethodni_order_by" in args
                and args["prethodni_order_by"] == args["order_by"]
            ):
                if args["order_type"] == "asc":
                    order_type = "desc"

        if "ime" in args:
            s_ime = "%" + args["ime"] + "%"
            s_prezime = "%" + args["prezime"] + "%"
            s_broj_indeksa = "%" + args["broj_indeksa"] + "%"
            s_godina_studija = "%" + args["godina_studija"] + "%"

        if "espb_od" in args and args["espb_od"] != "":
            s_espb_od = args["espb_od"]

        if "espb_do" in args and args["espb_do"] != "":
            s_espb_do = args["espb_do"]

        if "prosek_ocena_od" in args and args["prosek_ocena_od"] != "":
            s_prosek_ocena_od = args["prosek_ocena_od"]

        if "prosek_ocena_do" in args and args["prosek_ocena_do"] != "":
            s_prosek_ocena_do = args["prosek_ocena_do"]

        vrednosti = (
            s_ime,
            s_prezime,
            s_broj_indeksa,
            s_godina_studija,
            s_espb_od,
            s_espb_do,
            s_prosek_ocena_od,
            s_prosek_ocena_do,
            order_by,
            order_type,
            offset,
        )

        upit = """
                SELECT * FROM studenti
                WHERE ime LIKE "%s" AND
                prezime LIKE "%s" AND
                broj_indeksa LIKE "%s" AND
                godina_studija LIKE "%s" AND
                espb >= %s AND espb <= %s AND
                prosek_ocena >= %s AND prosek_ocena <= %s
                ORDER BY %s %s
                LIMIT 10 OFFSET %s
                """

        kursor.execute(upit % vrednosti)
        studenti = kursor.fetchall()

        prethodna_strana = ""
        sledeca_strana = "/studenti?page=2"
        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            del split_path[-1]
            sledeca_strana = "=".join(split_path) + "=" + str(int(strana) + 1)
            prethodna_strana = "=".join(split_path) + "=" + str(int(strana) - 1)

        return render_template(
            "studenti.html",
            studenti=studenti,
            rola=rola(),
            strana=strana,
            sledeca_strana=sledeca_strana,
            prethodna_strana=prethodna_strana,
            order_type=order_type,
            args=args,
        )
    else:
        return redirect(url_for("login"))


@app.route("/student_novi", methods=["GET", "POST"])
def student_novi():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        if request.method == "GET":
            return render_template("student_novi.html", rola=rola())
        elif request.method == "POST":
            forma = request.form
            naziv_slike = ""
            if "slika" in request.files:
                file = request.files["slika"]
                if file.filename:
                    naziv_slike = forma["jmbg"] + file.filename
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))
            upit = """
                INSERT INTO studenti
                (ime, ime_roditelja, prezime, broj_indeksa, godina_studija, jmbg, datum_rodjenja, espb, prosek_ocena, broj_telefona, email, slika)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            vrednosti = (
                forma["ime"],
                forma["ime_roditelja"],
                forma["prezime"],
                forma["broj_indeksa"],
                forma["godina_studija"],
                forma["jmbg"],
                forma["datum_rodjenja"],
                0,
                0,
                forma["broj_telefona"],
                forma["email"],
                naziv_slike,
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("studenti"))
    else:
        return redirect(url_for("login"))


@app.route("/student_izmena/<id>", methods=["GET", "POST"])
def student_izmena(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM studenti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            student = kursor.fetchone()
            return render_template("student_izmena.html", student=student, rola=rola())
        elif request.method == "POST":
            forma = request.form
            naziv_slike = ""
            if "slika" in request.files:
                file = request.files["slika"]
                if file.filename:
                    naziv_slike = forma["jmbg"] + file.filename
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))
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
                email=%s,
                slika=%s
                WHERE id=%s
            """
            vrednosti = (
                forma["ime"],
                forma["ime_roditelja"],
                forma["prezime"],
                forma["broj_indeksa"],
                forma["godina_studija"],
                forma["jmbg"],
                forma["datum_rodjenja"],
                forma["broj_telefona"],
                forma["email"],
                naziv_slike,
                id,
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("studenti"))
    else:
        return redirect(url_for("login"))


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
        return render_template(
            "student.html", student=student, predmeti=predmeti, ocene=ocene, rola=rola()
        )
    else:
        return redirect(url_for("login"))


@app.route("/student_brisanje/<id>")
def student_brisanje(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
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
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        args = request.args.to_dict()

        strana = request.args.get("page", "1")
        offset = int(strana) * 10 - 10

        s_naziv = "%%"
        s_sifra = "%%"
        s_obavezni_izborni = "%%"
        s_godina_studija = "%%"
        s_espb_od = "0"
        s_espb_do = "180"

        order_by = "id"
        order_type = "asc"

        if "order_by" in args:
            order_by = args["order_by"].lower()
            if (
                "prethodni_order_by" in args
                and args["prethodni_order_by"] == args["order_by"]
            ):
                if args["order_type"] == "asc":
                    order_type = "desc"

        if "naziv" in args:
            s_naziv = "%" + args["naziv"] + "%"
            s_sifra = "%" + args["sifra"] + "%"
            s_obavezni_izborni = "%" + args["obavezni_izborni"] + "%"
            s_godina_studija = "%" + args["godina_studija"] + "%"

        if "espb_od" in args and args["espb_od"] != "":
            s_espb_od = args["espb_od"]

        if "espb_do" in args and args["espb_do"] != "":
            s_espb_do = args["espb_do"]

        vrednosti = (
            s_naziv,
            s_sifra,
            s_obavezni_izborni,
            s_godina_studija,
            s_espb_od,
            s_espb_do,
            order_by,
            order_type,
            offset,
        )

        upit = """
                SELECT * FROM predmeti
                WHERE naziv LIKE "%s" AND
                sifra LIKE "%s" AND
                obavezni_izborni LIKE "%s" AND
                godina_studija LIKE "%s" AND
                espb >= %s AND espb <= %s
                ORDER BY %s %s
                LIMIT 10 OFFSET %s
                """
        kursor.execute(upit % vrednosti)
        predmeti = kursor.fetchall()

        prethodna_strana = ""
        sledeca_strana = "/studenti?page=2"
        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            del split_path[-1]
            sledeca_strana = "=".join(split_path) + "=" + str(int(strana) + 1)
            prethodna_strana = "=".join(split_path) + "=" + str(int(strana) - 1)

        return render_template(
            "predmeti.html",
            predmeti=predmeti,
            rola=rola(),
            strana=strana,
            sledeca_strana=sledeca_strana,
            prethodna_strana=prethodna_strana,
            order_type=order_type,
            args=args,
        )
    else:
        return redirect(url_for("login"))


@app.route("/predmet_novi", methods=["GET", "POST"])
def predmet_novi():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        if request.method == "GET":
            return render_template("predmet_novi.html", rola=rola())
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
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM predmeti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            predmet = kursor.fetchone()
            return render_template("predmet_izmena.html", predmet=predmet, rola=rola())
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
    if rola() == "profesor":
        return redirect(url_for("studenti"))
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
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        args = request.args.to_dict()

        strana = request.args.get("page", "1")
        offset = int(strana) * 10 - 10

        s_ime = "%%"
        s_prezime = "%%"
        s_email = "%%"
        s_rola = "%%"

        order_by = "id"
        order_type = "asc"

        if "order_by" in args:
            order_by = args["order_by"].lower()
            if (
                "prethodni_order_by" in args
                and args["prethodni_order_by"] == args["order_by"]
            ):
                if args["order_type"] == "asc":
                    order_type = "desc"

        if "ime" in args:
            s_ime = "%" + args["ime"] + "%"
            s_prezime = "%" + args["prezime"] + "%"
            s_email = "%" + args["email"] + "%"
            s_rola = "%" + args["rola"] + "%"

        vrednosti = (s_ime, s_prezime, s_email, s_rola, order_by, order_type, offset)
        upit = """
                SELECT * FROM korisnici
                WHERE ime LIKE "%s" AND
                prezime LIKE "%s" AND
                email LIKE "%s" AND
                rola LIKE "%s"
                ORDER BY %s %s
                LIMIT 10 OFFSET %s
                """

        kursor.execute(upit % vrednosti)
        korisnici = kursor.fetchall()

        prethodna_strana = ""
        sledeca_strana = "/korisnici?page=2"
        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            del split_path[-1]
            sledeca_strana = "=".join(split_path) + "=" + str(int(strana) + 1)
            prethodna_strana = "=".join(split_path) + "=" + str(int(strana) - 1)

        return render_template(
            "korisnici.html",
            korisnici=korisnici,
            rola=rola(),
            strana=strana,
            sledeca_strana=sledeca_strana,
            prethodna_strana=prethodna_strana,
            order_type=order_type,
            args=args,
        )
    else:
        return redirect(url_for("login"))


@app.route("/korisnik_novi", methods=["GET", "POST"])
def korisnik_novi():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        if request.method == "GET":
            return render_template("korisnik_novi.html", rola=rola())
        elif request.method == "POST":
            forma = request.form
            upit = """ INSERT INTO 
                        korisnici(ime,prezime,email,rola,lozinka)
                        VALUES (%s, %s, %s, %s, %s)    
                    """
            hesovana_lozinka = generate_password_hash(forma["lozinka"])
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                forma["rola"],
                hesovana_lozinka,
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            send_email(forma["ime"], forma["prezime"], forma["email"], forma["lozinka"])
            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for("login"))


@app.route("/korisnik_izmena/<id>", methods=["GET", "POST"])
def korisnik_izmena(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM korisnici WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            korisnik = kursor.fetchone()
            return render_template(
                "korisnik_izmena.html", korisnik=korisnik, rola=rola()
            )
        elif request.method == "POST":
            upit = """UPDATE korisnici SET 
                        ime=%s,
                        prezime=%s,
                        email=%s,
                        WHERE id=%s    
                    """
            forma = request.form
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                id,
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for("login"))


@app.route("/korisnik_brisanje/<id>", methods=["GET"])
def korisnik_brisanje(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
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
        vrednosti = (id, forma["predmet_id"], forma["ocena"], forma["datum"])
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
        vrednosti = (espb["rezultat"], prosek_ocena["rezultat"], id)
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("student", id=id))
    else:
        return redirect(url_for("login"))


@app.route("/ocena_brisanje/<student_id>/<ocena_id>")
def ocena_brisanje(student_id, ocena_id):
    if ulogovan():
        upit = "DELETE FROM ocene WHERE id=%s"
        vrednost = (ocena_id,)
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
        vrednosti = (espb["rezultat"], prosek_ocena["rezultat"], id)
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("student", id=student_id))
    else:
        return redirect(url_for("login"))


@app.route("/export/<tip>")
def export(tip):
    switch = {
        "studenti": "SELECT * FROM studenti",
        "korisnici": "SELECT * FROM korisnici",
        "predmeti": "SELECT * FROM predmeti",
    }
    upit = switch.get(tip)

    kursor.execute(upit)
    rezultat = kursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    for row in rezultat:
        red = []
        for value in row.values():
            red.append(str(value))
        writer.writerow(red)

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=" + tip + ".csv"},
    )


app.run()
# app.run(debug=True)
