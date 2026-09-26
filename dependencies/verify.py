from database import Session


def pegar_sessao():
    db = Session()
    try:
        yield db
    finally:
        db.close()