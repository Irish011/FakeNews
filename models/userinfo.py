from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = 'usrinfo'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
