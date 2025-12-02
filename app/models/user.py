from sqlalchemy import Integer, Boolean, Column, String
from app.database import Base


class User(Base):
    __tablename__ = "tb_users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    fl_admin = Column(Boolean)
    password_hash = Column(String(255))
