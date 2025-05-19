from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="segredo_super_seguro")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Autenticação básica
def gestor_autenticado(request: Request):
    return request.session.get("autenticado") == True

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def validar_login(request: Request, senha: str = Form(...)):
    if senha == "admin123":
        request.session["autenticado"] = True
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "erro": "Senha incorreta"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not gestor_autenticado(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro_veiculo(request: Request):
    if not gestor_autenticado(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("cadastro_veiculo.html", {"request": request})

@app.get("/reserva", response_class=HTMLResponse)
async def reserva(request: Request):
    return templates.TemplateResponse("reserva.html", {"request": request})

@app.get("/devolucao", response_class=HTMLResponse)
async def devolucao(request: Request):
    return templates.TemplateResponse("devolucao.html", {"request": request})

@app.get("/prereservas", response_class=HTMLResponse)
async def prereservas(request: Request):
    if not gestor_autenticado(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("listar_prereservas.html", {"request": request})

@app.get("/prereservas/editar", response_class=HTMLResponse)
async def editar(request: Request):
    if not gestor_autenticado(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("editar_prereserva.html", {"request": request})