from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import  relationship
#from sqlalchemy_utils.types import ChoiceType
from database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    ativo = Column(Boolean, default=True)
    consultas = relationship(
        "Consulta",
        back_populates="paciente"
    )

class Dentista(Base):
    __tablename__ = "dentistas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    cro = Column(String(20), unique=True, nullable=False)
    especialidade = Column(String(100))
    ativo = Column(Boolean, default=True)
    consultas = relationship(
        "Consulta",
        back_populates="dentista"
    )

class Consulta(Base):
    __tablename__ =  "consultas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    dentista_id = Column(Integer, ForeignKey("dentistas.id"), nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(String(20))
    paciente = relationship(
        "Paciente",
        back_populates="consultas"
    )
    dentista = relationship(
        "Dentista",
        back_populates="consultas"
    )

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(80), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(500), nullable=False)
    admin = Column(Boolean, default=False)