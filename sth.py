# if ulogovan...

# unos u tabelu ocene
forma = request.form
upit = """
    INSERT INTO ocene(student_id, predmet_id, datum, ocena)
    VALUES (%s, %s, %s, %s)
"""
vrednosti = (id, forma["predmet_id"], forma["datum"], forma["ocena"])
kursor.execute(upit, vrednosti)
konekcija.commit()

# resavanje espb
# prvo trazim stari espb
upit = "SELECT espb FROM studenti WHERE id=%s"
vrednosti = (id,)
kursor.execute(upit, vrednosti)
stari_espb = kursor.fetchone()
# trazim espb za odabrani predmet
upit = "SELECT espb FROM predmeti WHERE id=%s"
vrednosti = (forma["predmet_id"],)
kursor.execute(upit, vrednosti)
predmet_espb = kursor.fetchone()
# dobijanje novog espb
novi_espb = stari_espb + predmet_espb

# resavanje prosecne ocene
# napomena: vec smo uneli novu ocenu u bazu
upit = "SELECT AVG(ocena) FROM ocene WHERE student_id=%s"
vrednosti = (id,)
kursor.execute(upit, vrednosti)
novi_prosek = (
    kursor.fetchone()
)  # valjda ce da radi sa fetchone, trebalo bi, nisam probao

# unos novih u bazu
upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
vrednosti = (novi_espb, novi_prosek, id)
kursor.execute(upit, vrednosti)
konekcija.commit()

# else nije ulogova...

