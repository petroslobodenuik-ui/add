from fastapi import APIRouter, HTTPException
from sqlmodel import Field, SQLModel, Session, select
from typing import Optional, List
from .db import engine
from .warehouse import Commodity

router = APIRouter()


class PlanItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: Optional[int] = None
    commodity_id: int
    qty: int


class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class PlanItemCreate(SQLModel):
    commodity_id: int
    qty: int


class PlanCreate(SQLModel):
    name: str
    items: List[PlanItemCreate]


@router.post("/plans")
def create_plan(plan: PlanCreate):
    # check stock
    with Session(engine) as s:
        for it in plan.items:
            c = s.get(Commodity, it.commodity_id)
            if not c:
                raise HTTPException(status_code=404, detail=f"commodity {it.commodity_id} not found")
            if c.quantity < it.qty:
                raise HTTPException(status_code=400, detail=f"insufficient stock for {c.name}")
        # all ok -> persist plan and items
        p = Plan(name=plan.name)
        s.add(p)
        s.commit()
        s.refresh(p)
        # capture values while instance is attached to session
        pid = p.id
        pname = p.name
        for it in plan.items:
            pi = PlanItem(plan_id=pid, commodity_id=it.commodity_id, qty=it.qty)
            s.add(pi)
        s.commit()
    return {"plan": {"id": pid, "name": pname}, "items": [{"commodity_id": i.commodity_id, "qty": i.qty} for i in plan.items]}
