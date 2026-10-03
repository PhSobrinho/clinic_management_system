from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from models.paciente import Usuario, Paciente
from dependencies.verify import pegar_sessao, verificar_token
from schemas.schemas_routes import UsuarioSchema, adminSchema, LoginSchema, PacienteSchema, PacienteResponse
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

@pacientes_routes.get("/listar_pacientes", response_model=list[PacienteResponse])
async def listar_pacientes(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="você não tem autorização para fazer essa ação")
    
    pacientes = session.query(Paciente).filter_by(ativo=True).all()
    return pacientes


@pacientes_routes.get("/buscar_paciente/{id_paciente}", response_model=PacienteResponse)
async def buscar_paciente(id_paciente: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem autorização para fazer essa modificação")
    paciente = session.query(Paciente).filter(Paciente.id == id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="paciente não encontrado")
    
    return paciente

@pacientes_routes.delete("/remover_paciente/{id_paciente}")
async def remover_paciente(id_paciente: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem autorização para fazer essa modificação")
    paciente = session.query(Paciente).filter(Paciente.id == id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="paciente não encontrado")
    paciente.ativo = False
    session.commit()
    return {"mensagem": f"sucesso, paciente de id {id_paciente} foi removido"}

@pacientes_routes.put("/atualizar_paciente/{id_paciente}", response_model=PacienteResponse)
async def atualizar_paciente(id_paciente: int, paciente_schema: PacienteSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem autorização para fazer essa modificação")
    paciente = session.query(Paciente).filter(Paciente.id == id_paciente).first()
    if not paciente: raise HTTPException(status_code=404, detail="Paciente não encontrado")
    paciente.nome = paciente_schema.nome
    paciente.email = paciente_schema.email
    paciente.telefone = paciente_schema.telefone
    session.commit()
    session.refresh(paciente)

    return paciente
