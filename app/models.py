# app/models.py

from datetime import datetime
import uuid

from sqlalchemy import (
    UUID, Boolean, Column, ForeignKey, Integer, String, Text, DateTime,
    Float, UniqueConstraint
)
from .database import Base


# ----------------- MODELOS EXISTENTES -----------------

class WikiPosts(Base):
    __tablename__ = 'tb_wiki_posts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    author_name = Column(String(255), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    topic_id = Column(UUID(as_uuid=True), nullable=False)


class User(Base):
    __tablename__ = 'tb_users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    username = Column(String(255))
    email = Column(String(255))
    fl_admin = Column(Boolean)
    passwordhash = Column(String(255))


# ----------------- MÓDULO DE DADOS -----------------
# Fonte -> Indicador -> Observação (séries temporais por UF/município)

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    url = Column(String(512))
    description = Column(Text)


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    code = Column(String(255), unique=True, nullable=False)  # ex.: IBGE_CENSO_PCD_PERCENT_TOTAL
    name = Column(String(255), nullable=False)
    unit = Column(String(50))
    source_id = Column(Integer, ForeignKey("sources.id"))


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    geo_id = Column(String(10), nullable=False)        # código IBGE (UF/município)
    geo_level = Column(String(10), nullable=False)     # 'uf' | 'mun'
    year = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("indicator_id", "geo_id", "year", name="uq_obs_one_value"),
    )
