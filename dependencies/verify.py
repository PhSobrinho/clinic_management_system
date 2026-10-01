from database import SessionLocal
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import os
from sqlalchemy.orm import Session, sessionmaker
from models.paciente import Usuario
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
Oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

def pegar_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verificar_token(token: str = Depends(Oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(dic_info.get("sub"))
    except PyJWTError:
        raise HTTPException(status_code=401, detail="acesso negado, verifique a validade do token")
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="acesso inválido")
    return usuario
