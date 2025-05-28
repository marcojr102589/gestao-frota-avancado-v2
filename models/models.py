from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Veiculo(Base):
    __tablename__ = 'veiculos'

    id = Column(Integer, primary_key=True)
    placa = Column(String, unique=True, nullable=False)
    modelo = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

class Reserva(Base):
    __tablename__ = 'reservas'

    id = Column(Integer, primary_key=True)
    veiculo_id = Column(Integer, ForeignKey('veiculos.id'))
    nome_usuario = Column(String, nullable=False)
    data_reserva = Column(DateTime, default=datetime.utcnow)
    devolvido = Column(Boolean, default=False)

    veiculo = relationship("Veiculo")