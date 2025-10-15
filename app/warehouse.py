from fastapi import APIRouter, HTTPException
from sqlmodel import Field, SQLModel, Session, select
from typing import Optional, List
from .db import engine

router = APIRouter()


class Commodity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: int = 0


class TTN(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    commodity_id: int
    qty: int
    note: Optional[str] = None


@router.post("/commodities")
def create_commodity(c: Commodity):
    with Session(engine) as s:
        s.add(c)
        s.commit()
        s.refresh(c)
    return c


@router.post("/ttn")
def create_ttn(t: TTN):
    with Session(engine) as s:
        commodity = s.get(Commodity, t.commodity_id)
        if not commodity:
            raise HTTPException(status_code=404, detail="commodity not found")
        commodity.quantity += t.qty
        s.add(t)
        s.add(commodity)
        s.commit()
        s.refresh(t)
    return t


@router.get("/commodities", response_model=List[Commodity])
def list_commodities():
    with Session(engine) as s:
        return s.exec(select(Commodity)).all()


@router.get("/stock/{commodity_id}")
def stock_card(commodity_id: int):
    with Session(engine) as s:
        commodity = s.get(Commodity, commodity_id)
        if not commodity:
            raise HTTPException(status_code=404, detail="commodity not found")
        # simple stock card: return qty and TTNs
        tt = s.exec(select(TTN).where(TTN.commodity_id == commodity_id)).all()
        return {"commodity": commodity, "ttns": tt}
