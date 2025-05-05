from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from utils import generuj_numer_rachunku, generuj_pdf
from datetime import datetime
import sqlite3
import os
from jinja2 import Environment, FileSystemLoader

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DATABASE = "database.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS zlecenia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imie TEXT,
            telefon TEXT,
            adres TEXT,
            urzadzenie TEXT,
            usterka TEXT,
            kwota TEXT
        )""")
        conn.commit()

def dodaj_kwote_column():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("PRAGMA table_info(zlecenia)")
        kolumny = [row[1] for row in c.fetchall()]
        if "kwota" not in kolumny:
            c.execute("ALTER TABLE zlecenia ADD COLUMN kwota TEXT DEFAULT '250'")
        conn.commit()

init_db()
dodaj_kwote_column()

@app.get("/", response_class=HTMLResponse)
def odczyt_panelu(request: Request):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM zlecenia ORDER BY id DESC")
        zlecenia = c.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "zlecenia": zlecenia})

@app.post("/api/zgloszenie")
async def dodaj_zgloszenie(request: Request):
    form_data = await request.form()
    imie = form_data.get("imie")
    telefon = form_data.get("telefon")
    adres = form_data.get("adres")
    urzadzenie = form_data.get("urzadzenie")
    usterka = form_data.get("usterka")
    kwota = form_data.get("kwota", "250")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO zlecenia (imie, telefon, adres, urzadzenie, usterka, kwota) VALUES (?, ?, ?, ?, ?, ?)",
                   (imie, telefon, adres, urzadzenie, usterka, kwota))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=302)

@app.get("/api/rachunek/{zlecenie_id}", response_class=FileResponse)
def generuj_rachunek(zlecenie_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zlecenia WHERE id = ?", (zlecenie_id,))
    zlecenie = cursor.fetchone()
    conn.close()

    if not zlecenie:
        return {"error": "Nie znaleziono zlecenia"}

    numer = generuj_numer_rachunku(zlecenie_id)
    dane = {
        "numer": numer,
        "data": datetime.now().strftime("%Y-%m-%d"),
        "imie": zlecenie[1],
        "telefon": zlecenie[2],
        "adres": zlecenie[3],
        "urzadzenie": zlecenie[4],
        "usterka": zlecenie[5],
        "kwota": zlecenie[6]
    }

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("rachunek.html")
    html_output = template.render(dane)

    with open("rachunek_temp.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    pdf_path = f"rachunek_{numer}.pdf"
    generuj_pdf("rachunek_temp.html", pdf_path)

    return FileResponse(path=pdf_path, filename=pdf_path, media_type='application/pdf')
