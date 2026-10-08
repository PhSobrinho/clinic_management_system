from fastapi import APIRouter, Depends, HTTPException, Query
from models.paciente import Usuario, Dentista, Consulta, Paciente
from dependencies.verify import pegar_sessao, verificar_token
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone, date, time
from schemas.schemas_routes import ConsultaResponse, ConsultaCreate

consultas_routes = APIRouter(prefix="/consultas", tags=["consultas"], dependencies=[Depends(verificar_token)])

@consultas_routes.get("/horarios_disponiveis", response_model=list[str])
async def listar_horarios_disponiveis(id_dentista: int,data_busca: date = Query(...),session: Session = Depends(pegar_sessao)):
    dentista = session.query(Dentista).filter(Dentista.id == id_dentista,Dentista.ativo == True).first()
    if not dentista:
        raise HTTPException(
            status_code=404,
            detail="dentista não encontrado"
        )
    if data_busca < date.today():
        raise HTTPException(
            status_code=400,
            detail="não é possível consultar datas passadas"
        )
    fuso_local = timezone(timedelta(hours=-3))
    inicio_dia_local = datetime.combine(
        data_busca,
        time.min,
        tzinfo=fuso_local
    )
    fim_dia_local = datetime.combine(
        data_busca,
        time.max,
        tzinfo=fuso_local
    )
    consultas_agendadas = session.query(Consulta).filter(
        Consulta.dentista_id == id_dentista,
        Consulta.data_hora >= inicio_dia_local.astimezone(timezone.utc),
        Consulta.data_hora <= fim_dia_local.astimezone(timezone.utc),
        Consulta.status != "cancelado").all()
    horarios_ocupados = {
        consulta.data_hora
        .replace(tzinfo=timezone.utc)
        .astimezone(fuso_local)
        .time()
        for consulta in consultas_agendadas
    }
    horarios_livres = []
    horario_atual = datetime.combine(data_busca,time(8, 0),tzinfo=fuso_local)
    limite_horario = datetime.combine(data_busca,time(18, 0),tzinfo=fuso_local)
    duracao_consulta = timedelta(minutes=30)
    while horario_atual < limite_horario:
        hora_atual = horario_atual.time()
        horario_almoco = (time(12, 0) <= hora_atual < time(14, 0))
        if not horario_almoco:
            if hora_atual not in horarios_ocupados:
                horarios_livres.append(horario_atual.isoformat())
        horario_atual += duracao_consulta
    return horarios_livres

@consultas_routes.post("/agendar", response_model=ConsultaResponse)
async def agendar_consulta(schema: ConsultaCreate, session: Session = Depends(pegar_sessao)):
    if schema.data_hora.tzinfo is None:
        raise HTTPException(status_code=400, detail="O horário deve incluir fuso horário local")
    horario_utc = schema.data_hora.astimezone(timezone.utc)
    fuso_local = timezone(timedelta(hours=-3))
    hora_local = schema.data_hora.astimezone(fuso_local).time()
    if horario_utc < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Não é possível agendar em horários passados")
    if time(12, 0) <= hora_local < time(14, 0):
        raise HTTPException(status_code=400, detail="Não é possível realizar agendamentos no horário de almoço (12:00 às 14:00)")
    if hora_local < time(8, 0) or hora_local >= time(18, 0):
        raise HTTPException(status_code=400, detail="Horário fora do expediente")
    dentista = session.query(Dentista).filter(Dentista.id == schema.dentista_id, Dentista.ativo == True).first()
    if not dentista:
        raise HTTPException(status_code=404, detail="Dentista não cadastrado ou inativo")
    paciente = session.query(Paciente).filter(Paciente.id == schema.paciente_id, Paciente.ativo == True).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não cadastrado ou inativo")
    conflito = session.query(Consulta).filter(Consulta.dentista_id == schema.dentista_id, Consulta.data_hora == horario_utc.replace(tzinfo=None), Consulta.status != "cancelado").first()
    if conflito:
        raise HTTPException(status_code=409, detail="Este dentista já possui uma consulta agendada para este horário")

    nova_consulta = Consulta(paciente_id=schema.paciente_id, dentista_id=schema.dentista_id, data_hora=horario_utc.replace(tzinfo=None), status="agendado", descricao_consulta=schema.descricao_consulta)
    session.add(nova_consulta)
    session.commit()
    session.refresh(nova_consulta)
    return nova_consulta

@consultas_routes.put("/reagendar/{id_consulta}", response_model=ConsultaResponse)
async def atualizar_consulta(id_consulta: int, schema: ConsultaCreate, session: Session = Depends(pegar_sessao)):
    consulta = session.query(Consulta).filter(Consulta.id == id_consulta, Consulta.status != "cancelado").first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if schema.data_hora.tzinfo is None:
        raise HTTPException(status_code=400, detail="O horário deve incluir fuso horário local")
    horario_utc = schema.data_hora.astimezone(timezone.utc)
    fuso_local = timezone(timedelta(hours=-3))
    hora_local = schema.data_hora.astimezone(fuso_local).time()
    if horario_utc < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Não é possível agendar em horários passados")
    if time(12, 0) <= hora_local < time(14, 0):
        raise HTTPException(status_code=400, detail="Não é possível realizar agendamentos no horário de almoço (12:00 às 14:00)")
    if hora_local < time(8, 0) or hora_local >= time(18, 0):
        raise HTTPException(status_code=400, detail="Horário fora do expediente")
    conflito = session.query(Consulta).filter(Consulta.dentista_id == schema.dentista_id, Consulta.data_hora == horario_utc.replace(tzinfo=None), Consulta.id != id_consulta, Consulta.status != "cancelado").first()
    if conflito:
        raise HTTPException(status_code=409, detail="Este dentista já possui uma consulta neste horário")
    dentista = session.query(Dentista).filter(Dentista.id == schema.dentista_id, Dentista.ativo == True).first()
    if not dentista:
        raise HTTPException(status_code=404, detail="Dentista não cadastrado ou inativo")
    paciente = session.query(Paciente).filter(Paciente.id == schema.paciente_id, Paciente.ativo == True).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não cadastrado ou inativo")
    consulta.paciente_id = schema.paciente_id
    consulta.dentista_id = schema.dentista_id
    consulta.data_hora = horario_utc.replace(tzinfo=None)
    consulta.descricao_consulta = schema.descricao_consulta
    session.commit()
    session.refresh(consulta)
    return consulta

@consultas_routes.delete("/cancelar/{id_consulta}")
async def cancelar_consulta(id_consulta: int, session: Session = Depends(pegar_sessao)):
    consulta = session.query(Consulta).filter(Consulta.id == id_consulta, Consulta.status != "cancelado").first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    consulta.status = "cancelado"
    session.commit()
    return {"mensagem": f"Consulta de id {id_consulta} cancelada com sucesso"}

@consultas_routes.get("/listar_consultas", response_model=list[ConsultaResponse])
async def listar_consultas(session: Session = Depends(pegar_sessao)):
    consultas = session.query(Consulta).filter_by(status="agendado").all()
    return consultas

@consultas_routes.get("/buscar_consulta/{id_consulta}", response_model=ConsultaResponse)
async def buscar_consulta(id_consulta: int, session: Session = Depends(pegar_sessao)):
    consulta = session.query(Consulta).filter(Consulta.id == id_consulta).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="consulta não encontrada")
    return consulta

@consultas_routes.patch("/realizar_consulta/{id_consulta}", response_model=ConsultaResponse)
async def realizar_consulta(id_consulta: int, session: Session = Depends(pegar_sessao)):
    consulta = session.query(Consulta).filter(Consulta.id == id_consulta).first()
    if not consulta:
            raise HTTPException(status_code=404, detail="consulta não encontrada")
    if consulta.status != "agendado":
        raise HTTPException(status_code=400,detail="apenas consultas agendadas podem ser realizadas")
    consulta.status = "realizado"
    session.commit()
    session.refresh(consulta)
    return consulta