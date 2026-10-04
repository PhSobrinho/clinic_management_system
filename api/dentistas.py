from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from models.paciente import Usuario, Dentista
from dependencies.verify import pegar_sessao, verificar_token
from schemas.schemas_routes import DentistaSchema, DentistaResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
dentista_routes = APIRouter(prefix="/dentistas", tags=["dentistas"], dependencies=[Depends(verificar_token)])

@dentista_routes.post("/cadastro_dentistas", response_model=DentistaResponse)
async def cadastrar_dentista(dentista_schema: DentistaSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin: 
        raise HTTPException(status_code=403,detail="Sem permissão, apenas administradores podem cadastrar novos dentistas")
    dentista = session.query(Dentista).filter(Dentista.cro==dentista_schema.cro).first()
    if dentista:
        raise HTTPException(status_code=409, detail="dentista já foi cadastrado")
   
    novo_dentista = Dentista(nome=dentista_schema.nome, email=dentista_schema.email,
                            telefone=dentista_schema.telefone,
                            cro=dentista_schema.cro, especialidade=dentista_schema.especialidade)
    session.add(novo_dentista)
    session.commit()
    session.refresh(novo_dentista)
    return novo_dentista

@dentista_routes.get("/listar_dentistas", response_model=list[DentistaResponse])
async def listar_dentista(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="você não tem autorização para fazer essa ação")
    
    dentistas = session.query(Dentista).filter_by(ativo=True).all()
    return dentistas


@dentista_routes.get("/buscar_dentista/{id_dentista}", response_model=DentistaResponse)
async def buscar_dentista(id_dentista: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem autorização para fazer essa modificação")
    dentista = session.query(Dentista).filter(Dentista.id == id_dentista, Dentista.ativo == True).first()
    if not dentista:
        raise HTTPException(status_code=404, detail="dentista não encontrado")
    
    return dentista

@dentista_routes.delete("/remover_dentista/{id_dentista}")
async def remover_dentista(id_dentista: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem autorização para fazer essa modificação")
    dentista = session.query(Dentista).filter(Dentista.id == id_dentista, Dentista.ativo == True).first()
    if not dentista:
        raise HTTPException(status_code=404, detail="dentista não encontrado")
    dentista.ativo = False
    session.commit()
    return {"mensagem": f"sucesso, dentista de id {id_dentista} foi removido"}

@dentista_routes.put("/atualizar_dentista/{id_dentista}", response_model=DentistaResponse)
async def atualizar_dentista(id_dentista: int, dentista_schema: DentistaSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem autorização para fazer essa modificação")
    dentista = session.query(Dentista).filter(Dentista.id == id_dentista, Dentista.ativo == True).first()
    if not dentista: raise HTTPException(status_code=404, detail="dentista não encontrado")
    dentista.nome = dentista_schema.nome
    dentista.email = dentista_schema.email
    dentista.telefone = dentista_schema.telefone
    dentista.cro = dentista_schema.cro
    dentista.especialidade = dentista_schema.especialidade
    session.commit()
    session.refresh(dentista)

    return dentista
