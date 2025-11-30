from typing import Iterable
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.data import * 

def get_or_create_source(db: Session, name: str, url: str = "", description: str = "") -> Source:
    src = db.execute(select(Source).where(Source.name == name)).scalar_one_or_none()
    if not src:
        src = Source(name=name, url=url, description=description)
        db.add(src); db.commit(); db.refresh(src)
    return src

def get_or_create_indicator(db: Session, code: str, name: str, unit: str, source: Source) -> Indicator:
    ind = db.execute(select(Indicator).where(Indicator.code == code)).scalar_one_or_none()
    if not ind:
        ind = Indicator(code=code, name=name, unit=unit, source_id=source.id)
        db.add(ind); db.commit(); db.refresh(ind)
    return ind

def upsert_observations(db: Session, indicator_id: int, rows: Iterable[dict]) -> int:
    created = 0
    for r in rows:
        exists = db.execute(select(Observation).where(
            Observation.indicator_id == indicator_id,
            Observation.geo_id == str(r["geo_id"]),
            Observation.year == int(r["year"])
        )).scalar_one_or_none()
        if exists:
            exists.value = float(r["value"])
        else:
            db.add(Observation(
                indicator_id=indicator_id,
                geo_id=str(r["geo_id"]),
                geo_level=r.get("geo_level","uf"),
                year=int(r["year"]),
                value=float(r["value"]),
            ))
            created += 1
    db.commit()
    return created
