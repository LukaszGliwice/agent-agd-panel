
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def db_connection():
    return sqlite3.connect("baza.db")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/formularz", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/zgloszenie")
async def zgloszenie(imie: str = Form(...), telefon: str = Form(...), adres: str = Form(...), sprzet: str = Form(...), opis: str = Form(...)):
    con = db_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO zlecenia (imie, telefon, adres, sprzet, opis) VALUES (?, ?, ?, ?, ?)", (imie, telefon, adres, sprzet, opis))
    con.commit()
    con.close()
    return RedirectResponse("/", status_code=302)

@app.get("/panel", response_class=HTMLResponse)
async def panel(request: Request):
    con = db_connection()
    cur = con.cursor()
    zlecenia = cur.execute("SELECT * FROM zlecenia").fetchall()
    con.close()
    return templates.TemplateResponse("panel.html", {"request": request, "zlecenia": zlecenia})
