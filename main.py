
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE = "database.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS zlecenia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imie TEXT,
            telefon TEXT,
            adres TEXT,
            urzadzenie TEXT,
            usterka TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT DEFAULT "Nowe"
        )''')
        conn.commit()

init_db()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM zlecenia ORDER BY id DESC")
        zlecenia = c.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "zlecenia": zlecenia})

@app.post("/api/zgloszenie")
def zgloszenie(imie: str = Form(...), telefon: str = Form(...), adres: str = Form(...),
               urzadzenie: str = Form(...), usterka: str = Form(...)):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO zlecenia (imie, telefon, adres, urzadzenie, usterka, start_time, end_time) VALUES (?, ?, ?, ?, ?, '', '')",
                  (imie, telefon, adres, urzadzenie, usterka))
        conn.commit()
    print(f"SMS TEST: Nowe zlecenie od {imie}, tel: {telefon}, sprzęt: {urzadzenie}")
    return {"status": "success"}

@app.post("/api/start/{zlecenie_id}")
def start_zlecenie(zlecenie_id: int):
    now = datetime.datetime.now().isoformat()
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("UPDATE zlecenia SET start_time = ?, status = 'W trakcie' WHERE id = ?", (now, zlecenie_id))
        conn.commit()
    return {"status": "started"}

@app.post("/api/stop/{zlecenie_id}")
def stop_zlecenie(zlecenie_id: int):
    now = datetime.datetime.now().isoformat()
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("UPDATE zlecenia SET end_time = ?, status = 'Zakończone' WHERE id = ?", (now, zlecenie_id))
        conn.commit()
    return {"status": "stopped"}
