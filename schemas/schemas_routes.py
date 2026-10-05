from pydantic import BaseModel, EmailStr
from typing import Optional, List, ClassVar
from datetime import datetime

class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str

    class Config:
        from_attributes =True

class adminSchema(BaseModel):
    admin: Optional[bool]
    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str
    class Config:
        from_attributes = True

class PacienteSchema(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    class Config:
        from_attributes = True

class PacienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    ativo: bool

    model_config = {
        "from_attributes": True
    }

class DentistaSchema(BaseModel):
    nome:str
    email: EmailStr
    telefone: str
    cro: str
    especialidade: str

    class Config:
        from_attributes =True

class DentistaResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    cro: str
    especialidade: str
    ativo: bool

    model_config = {
        "from_attributes": True
    }
class ConsultaCreate(BaseModel):
    paciente_id: int
    dentista_id: int
    data_hora: datetime
    descricao_consulta: str
    


class ConsultaResponse(BaseModel):
    id: int
    paciente_id: int
    dentista_id: int
    data_hora: datetime
    status: str
    descricao_consulta: str

    model_config = {
        "from_attributes": True
    }