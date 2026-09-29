from fastapi import APIRouter, Depends, HTTPException
from models.paciente import Usuario
from dependencies.verify import pegar_sessao# verificar_token
from security import ph
from schemas.schemas_routes import UsuarioSchema, adminSchema, LoginSchema
from sqlalchemy.orm import Session
import jwt
from security import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from datetime import datetime, timedelta, timezone
auth_routes = APIRouter(prefix="/auth", tags=["auth"])
from fastapi.security import OAuth2PasswordRequestForm
from argon2.exceptions import VerifyMismatchError, InvalidHashError




def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False

    try:
        ph.verify(usuario.senha, senha)
        return usuario
    except (VerifyMismatchError, InvalidHashError):
        return False


def criarToken(id_usuario, duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_informacoes = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dic_informacoes, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_codificado




@auth_routes.get("/")
async def home():
    return {"mensagem": "você acessou a rota padrão de autenticação", "autenticado": False}

@auth_routes.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=401, detail="Email do usúario já cadastrado")
    else:
        senha_criptografada = ph.hash(usuario_schema.senha)
        novo_usuario = Usuario(nome=usuario_schema.nome,email=usuario_schema.email , senha=senha_criptografada)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuario criado {usuario_schema.email}"}


@auth_routes.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="não existe usúario com esse email, ou credenciais inválidas")
    else:
        access_token = criarToken(usuario.id)
        refresh_token = criarToken(usuario.id, duracao_token=timedelta(days=7))
        return {"access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
                }

@auth_routes.post("/login-form")
async def login_form(formulario_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(formulario_data.username, formulario_data.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="não existe usúario com esse email, ou credenciais inválidas")
    else:
        access_token = criarToken(usuario.id)
        return {"access_token": access_token,
                "token_type": "Bearer"
                }

@auth_routes.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criarToken(usuario.id)
    return {"access_token": access_token,
            "token_type": "Bearer"
                    }