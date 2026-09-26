from fastapi import FastAPI
from dotenv import load_dotenv
from models.paciente import Paciente, Consulta, Dentista
load_dotenv()
import os
app = FastAPI()
from api.router_usuario import auth_routes
app.include_router(auth_routes)
from database import Base, engine
Base.metadata.create_all(bind=engine)
