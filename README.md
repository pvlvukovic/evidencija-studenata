# Evidencija studenata

### Cilj projekta

Izrada ovog projekta ima za cilj da student nauči koncepte, veštine i upotrebu alata za kreiranje osnovnih funkcionalnosti veb aplikacije korišćenjem sledećih veb tehnologija:
- Python - programski jezik za izradu backend-a
- mysql - baziran na sql-u, služi za kreiranje i upravljanje bazom podataka
- phpmyadmin - alat za upravljanje bazom podataka
- Flask - radni okvir koji služi za lakše kreiranje backend funkcionalnosti
- Jinja - Flask biblioteka za kreiranje šablona (html stranica)
- Bootstrap - najpopularniji framework za kreiranje responsive html stranica
- FontAwesome - biblioteka ikonica

### Instalacija

Za pokretanje projekta potrebno je imati instaliran MySQL server, PHP i phpMyAdmin.

### Pokretanje projekta

Potrebno je preuzeti (klonirati) projekat na svom računaru i instalirati potrebne python biblioteke. 

```sh
$ git clone https://github.com/pvlvukovic/evidencija_studenata.git
$ cd evidencija_studenata
$ pip3 install Flask
$ pip3 install mysql-connector-python
$ python3 app.py
```