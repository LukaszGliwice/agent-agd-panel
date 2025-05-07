
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def init_db():
    conn = sqlite3.connect("zgloszenia.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS zgloszenia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imie TEXT,
        telefon TEXT,
        adres TEXT,
        urzadzenie TEXT,
        usterka TEXT,
        status TEXT,
        czas TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/wyslij")
def wyslij(
    request: Request,
    imie: str = Form(...),
    telefon: str = Form(...),
    adres: str = Form(...),
    urzadzenie: str = Form(...),
    usterka: str = Form(...)
):
    conn = sqlite3.connect("zgloszenia.db")
    c = conn.cursor()
    c.execute("INSERT INTO zgloszenia (imie, telefon, adres, urzadzenie, usterka, status, czas) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (imie, telefon, adres, urzadzenie, usterka, "nowe", datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return RedirectResponse("/panel", status_code=303)

@app.get("/panel")
def panel(request: Request):
    conn = sqlite3.connect("zgloszenia.db")
    c = conn.cursor()
    c.execute("SELECT * FROM zgloszenia")
    zgloszenia = c.fetchall()
    conn.close()
    return templates.TemplateResponse("panel.html", {"request": request, "zgloszenia": zgloszenia})

@app.post("/zgloszenie/{id}/status")
def zmien_status(id: int, status: str = Form(...)):
    conn = sqlite3.connect("zgloszenia.db")
    c = conn.cursor()
    c.execute("UPDATE zgloszenia SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    conn.close()
    return RedirectResponse("/panel", status_code=303)
