
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("templates"):
    os.makedirs("templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def init_db():
    conn = sqlite3.connect("baza.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS zgloszenia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imie TEXT,
        telefon TEXT,
        adres TEXT,
        sprzet TEXT,
        opis TEXT,
        status TEXT DEFAULT 'oczekujące'
    )''')
    conn.commit()
    conn.close()

init_db()

@app.get("/formularz", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("formularz.html", {"request": request})

@app.post("/zgloszenie")
async def submit_form(imie: str = Form(...), telefon: str = Form(...), adres: str = Form(...), sprzet: str = Form(...), opis: str = Form(...)):
    conn = sqlite3.connect("baza.db")
    c = conn.cursor()
    c.execute("INSERT INTO zgloszenia (imie, telefon, adres, sprzet, opis) VALUES (?, ?, ?, ?, ?)",
              (imie, telefon, adres, sprzet, opis))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/formularz", status_code=303)

@app.get("/panel", response_class=HTMLResponse)
async def panel(request: Request):
    conn = sqlite3.connect("baza.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM zgloszenia ORDER BY id DESC")
    zgloszenia = c.fetchall()
    conn.close()
    return templates.TemplateResponse("panel.html", {"request": request, "zgloszenia": zgloszenia})
