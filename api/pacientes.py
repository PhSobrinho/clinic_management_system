from fastapi import APIRouter, Depends, HTTPException
from models.paciente import Usuario, Paciente
from dependencies.verify import pegar_sessao, verificar_token
from schemas.schemas_routes import UsuarioSchema, adminSchema, LoginSchema, PacienteSchema
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
pacientes_routes = APIRouter(prefix="/pacientes", tags=["pacientes"], dependencies=[Depends(verificar_token)])

@pacientes_routes.post("/cadastro_pacientes")
async def cadastrar_paciente(paciente_schema: PacienteSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin: 
        raise HTTPException(status_code=403,detail="Sem permissão, apenas administradores podem cadastrar novos pacientes")
    paciente = session.query(Paciente).filter(Paciente.nome==paciente_schema.nome).first()
    if paciente:
        raise HTTPException(status_code=409, detail="paciente já foi cadastrado")
   
    novo_paciente = Paciente(nome=paciente_schema.nome, email=paciente_schema.email, telefone=paciente_schema.telefone)
    session.add(novo_paciente)
    session.commit()
    session.refresh(novo_paciente)
    return {"mensagem": "Paciente cadastrado com sucesso"}
