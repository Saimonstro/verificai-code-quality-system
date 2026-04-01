from fastapi import Depends, HTTPException
from main import ALGORITHM, SECRET_KEY, oauth2_scheme
from models import db
from sqlalchemy.orm import sessionmaker, Session 
from models import Usuario
from jose import jwt, JWTError

def pegar_sessao():
    try:
        session = sessionmaker(bind=db)
        session = session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_scheme), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError as erro:
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token") from erro
    # verifica se o token é valido  
    # extrai o id do usuario do token  
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token")
    return usuario  