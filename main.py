from fastapi import FastAPI

from dotenv import load_dotenv
from models.paciente import Dentista, Consulta, Dentista, Usuario
load_dotenv()
import os
app = FastAPI()
from api.router_usuario import auth_routes
from api.pacientes import pacientes_routes
from api.dentistas import dentista_routes
app.include_router(auth_routes)
app.include_router(pacientes_routes)
app.include_router(dentista_routes)
from database import Base, engine
Base.metadata.create_all(bind=engine)
