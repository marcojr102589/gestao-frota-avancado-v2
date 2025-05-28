from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime

# Banco de dados local SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./banco.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos
class Veiculo(Base):
    __tablename__ = "veiculos"
    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String)
    placa = Column(String, unique=True)
    ativo = Column(Boolean, default=True)
    em_manutencao = Column(Boolean, default=False)

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    nome_usuario = Column(String)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"))
    data_reserva = Column(DateTime)
    data_retirada = Column(DateTime, nullable=True)
    data_devolucao = Column(DateTime, nullable=True)
    devolvido = Column(Boolean, default=False)
    origem = Column(String, nullable=True)
    destino = Column(String, nullable=True)

# App e rotas
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# Rota de exemplo protegida
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Adicione aqui outras rotas (login, reserva, devolucao, dashboard, manutencao, etc.)