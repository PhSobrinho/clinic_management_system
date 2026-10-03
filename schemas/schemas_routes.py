from pydantic import BaseModel, EmailStr
from typing import Optional, List


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


