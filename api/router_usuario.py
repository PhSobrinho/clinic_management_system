from fastapi import APIRouter, Depends, HTTPException
from models.paciente import Usuario
from dependencies.verify import pegar_sessao# verificar_token
from security import ph
from schemas.schemas_routes import UsuarioSchema, adminSchema #LoginSchema
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta, timezone
auth_routes = APIRouter(prefix="/auth", tags=["auth"])
from fastapi.security import OAuth2PasswordRequestForm

@auth_routes.get("/")
async def home():
    return {"mensagem": "você acessou a rota padrão de autenticação", "autenticado": False}

@auth_routes.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Email do usúario já cadastrado")
    else:
        senha_criptografada = ph.hash(usuario_schema.senha)
        novo_usuario = Usuario(nome=usuario_schema.nome,email=usuario_schema.email , senha=senha_criptografada)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuario criado {usuario_schema.email}"}