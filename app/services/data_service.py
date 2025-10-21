from typing import Iterable
from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models

def get_or_create_source(db: Session, name: str, url: str = "", description: str = "") -> models.Source:
    src = db.execute(select(models.Source).where(models.Source.name == name)).scalar_one_or_none()
    if not src:
        src = models.Source(name=name, url=url, description=description)
        db.add(src); db.commit(); db.refresh(src)
    return src

def get_or_create_indicator(db: Session, code: str, name: str, unit: str, source: models.Source) -> models.Indicator:
    ind = db.execute(select(models.Indicator).where(models.Indicator.code == code)).scalar_one_or_none()
    if not ind:
        ind = models.Indicator(code=code, name=name, unit=unit, source_id=source.id)
        db.add(ind); db.commit(); db.refresh(ind)
    return ind

def upsert_observations(db: Session, indicator_id: int, rows: Iterable[dict]) -> int:
    created = 0
    for r in rows:
        exists = db.execute(select(models.Observation).where(
            models.Observation.indicator_id == indicator_id,
            models.Observation.geo_id == str(r["geo_id"]),
            models.Observation.year == int(r["year"])
        )).scalar_one_or_none()
        if exists:
            exists.value = float(r["value"])
        else:
            db.add(models.Observation(
                indicator_id=indicator_id,
                geo_id=str(r["geo_id"]),
                geo_level=r.get("geo_level","uf"),
                year=int(r["year"]),
                value=float(r["value"]),
            ))
            created += 1
    db.commit()
    return created
