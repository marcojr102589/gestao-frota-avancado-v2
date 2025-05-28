from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from database.database import criar_tabelas, SessionLocal
from models.models import Veiculo, Reserva

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="segredo_super_seguro")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def gestor_autenticado(request: Request):
    return request.session.get("autenticado") == True

@app.on_event("startup")
def startup():
    criar_tabelas()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/cadastro", response_class=HTMLResponse)
async def salvar_veiculo(request: Request, modelo: str = Form(...), placa: str = Form(...), db: Session = Depends(get_db)):
    novo = Veiculo(modelo=modelo, placa=placa)
    db.add(novo)
    db.commit()
    return templates.TemplateResponse("cadastro_veiculo.html", {
        "request": request,
        "mensagem": "Veículo cadastrado com sucesso"
    })

@app.get("/reserva", response_class=HTMLResponse)
async def reserva(request: Request):
    return templates.TemplateResponse("reserva.html", {"request": request})

@app.post("/reserva", response_class=HTMLResponse)
async def reservar_veiculo(request: Request, nome_usuario: str = Form(...), veiculo_id: int = Form(...), db: Session = Depends(get_db)):
    nova = Reserva(nome_usuario=nome_usuario, veiculo_id=veiculo_id)
    db.add(nova)
    db.commit()
    return templates.TemplateResponse("reserva.html", {
        "request": request,
        "mensagem": "Reserva registrada com sucesso"
    })

@app.get("/devolucao", response_class=HTMLResponse)
async def devolucao(request: Request):
    return templates.TemplateResponse("devolucao.html", {"request": request})

@app.get("/prereservas", response_class=HTMLResponse)
async def prereservas(request: Request, db: Session = Depends(get_db)):
    if not gestor_autenticado(request):
        return RedirectResponse("/login")
    reservas = db.query(Reserva).all()
    return templates.TemplateResponse("listar_prereservas.html", {
        "request": request,
        "reservas": reservas
    })

@app.get("/prereservas/editar", response_class=HTMLResponse)
async def editar(request: Request):
    if not gestor_autenticado(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("editar_prereserva.html", {"request": request})

@app.post("/devolucao", response_class=HTMLResponse)
async def confirmar_devolucao(request: Request, reserva_id: int = Form(...), db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter_by(id=reserva_id).first()
    if reserva:
        reserva.devolvido = True
        db.commit()
        msg = "Devolução confirmada com sucesso."
    else:
        msg = "Reserva não encontrada."
    return templates.TemplateResponse("devolucao.html", {"request": request, "mensagem": msg})

@app.post("/prereservas/editar", response_class=HTMLResponse)
async def editar_reserva(request: Request, reserva_id: int = Form(...), novo_nome: str = Form(...), db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter_by(id=reserva_id).first()
    if reserva:
        reserva.nome_usuario = novo_nome
        db.commit()
        msg = "Reserva atualizada com sucesso."
    else:
        msg = "Reserva não encontrada."
    return templates.TemplateResponse("editar_prereserva.html", {"request": request, "mensagem": msg})

from models.models import Usuario
from passlib.hash import bcrypt

@app.get("/usuarios/novo", response_class=HTMLResponse)
async def form_cadastro_usuario(request: Request):
    return templates.TemplateResponse("cadastro_usuario.html", {"request": request})

@app.post("/usuarios/novo", response_class=HTMLResponse)
async def criar_usuario(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    existe = db.query(Usuario).filter(Usuario.email == email).first()
    if existe:
        return templates.TemplateResponse("cadastro_usuario.html", {"request": request, "erro": "E-mail já cadastrado."})
    senha_hash = bcrypt.hash(senha)
    usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash)
    db.add(usuario)
    db.commit()
    return RedirectResponse("/login", status_code=302)

@app.post("/login", response_class=HTMLResponse)
async def login_usuario(request: Request, email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not bcrypt.verify(senha, usuario.senha_hash):
        return templates.TemplateResponse("login.html", {"request": request, "erro": "Usuário ou senha inválidos."})
    request.session["usuario_id"] = usuario.id
    return RedirectResponse("/dashboard", status_code=302)

def usuario_logado(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
from datetime import datetime

@app.get("/prereservas", response_class=HTMLResponse)
async def prereservas(request: Request, data_inicio: str = "", data_fim: str = "", db: Session = Depends(get_db)):
    if not gestor_autenticado(request):
        return RedirectResponse("/login")

    query = db.query(Reserva)
    if data_inicio:
        query = query.filter(Reserva.data_reserva >= datetime.strptime(data_inicio, "%Y-%m-%d"))
    if data_fim:
        query = query.filter(Reserva.data_reserva <= datetime.strptime(data_fim, "%Y-%m-%d"))

    reservas = query.order_by(Reserva.data_reserva.desc()).all()

    return templates.TemplateResponse("listar_prereservas.html", {
        "request": request,
        "reservas": reservas,
        "data_inicio": data_inicio,
        "data_fim": data_fim
    })

@app.get("/exportar")
async def exportar_reservas(db: Session = Depends(get_db)):
    reservas = db.query(Reserva).all()
    data = [{
        "ID": r.id,
        "Usuário": r.nome_usuario,
        "Veículo": r.veiculo_id,
        "Data Reserva": r.data_reserva.strftime("%Y-%m-%d %H:%M"),
        "Devolvido": "Sim" if r.devolvido else "Não"
    } for r in reservas]

    df = pd.DataFrame(data)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reservas')
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=reservas.xlsx"
    })

@app.get("/reserva", response_class=HTMLResponse)
async def reserva(request: Request, db: Session = Depends(get_db)):
    subquery = db.query(Reserva.veiculo_id).filter(Reserva.devolvido == False).subquery()
    veiculos_disponiveis = db.query(Veiculo).filter(Veiculo.id.notin_(subquery), Veiculo.ativo == True).all()

    if not veiculos_disponiveis:
        return templates.TemplateResponse("reserva.html", {"request": request, "veiculos_disponiveis": []})

    return templates.TemplateResponse("reserva.html", {
        "request": request,
        "veiculos_disponiveis": veiculos_disponiveis
    })

@app.post("/devolucao", response_class=HTMLResponse)
async def confirmar_devolucao(
    request: Request,
    placa: str = Form(...),
    problema: str = Form(...),
    limpo: str = Form(...),
    abastecido: str = Form(...),
    observacao: str = Form(...),
    db: Session = Depends(get_db)
):
    veiculo = db.query(Veiculo).filter(Veiculo.placa == placa).first()
    if not veiculo:
        return templates.TemplateResponse("devolucao.html", {
            "request": request,
            "mensagem": "Placa não encontrada."
        })

    reserva = db.query(Reserva).filter(Reserva.veiculo_id == veiculo.id, Reserva.devolvido == False).first()
    if reserva:
        reserva.devolvido = True
        db.commit()
        msg = "Devolução registrada com sucesso. Checklist: " + f"Problema: {problema}, Limpo: {limpo}, Abastecido: {abastecido}, Obs: {observacao}"
    else:
        msg = "Nenhuma reserva ativa para esta placa."

    return templates.TemplateResponse("devolucao.html", {
        "request": request,
        "mensagem": msg
    })