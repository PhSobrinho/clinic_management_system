from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import  relationship
#from sqlalchemy_utils.types import ChoiceType
from database import Base
from sqlalchemy.dialects.mysql import TIMESTAMP
from enum import Enum
from datetime import datetime
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
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id"),
        nullable=False,
        index=True
    )
    dentista_id = Column(
        Integer,
        ForeignKey("dentistas.id"),
        nullable=False,
        index=True
    )
    data_hora = Column(
        TIMESTAMP,
        nullable=False,
        index=True
    )
    status = Column(
        String(20),
        nullable=False,
        default="agendado"
    )
    descricao_consulta = Column(String(200), nullable=False)

    paciente = relationship(
        "Paciente",
        back_populates="consultas"
    )
    dentista = relationship(
        "Dentista",
        back_populates="consultas"
    )
    __table_args__ = (
        Index(
            "idx_dentista_data",
            "dentista_id",
            "data_hora"
        ),
    )

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(80), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(500), nullable=False)
    admin = Column(Boolean, default=False)