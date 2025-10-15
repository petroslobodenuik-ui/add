from fastapi import FastAPI
from sqlmodel import SQLModel
from .personnel import router as personnel_router
from .warehouse import router as warehouse_router
from .planning import router as planning_router
from .db import engine

app = FastAPI(title="Humanitarian Projects Management")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"status": "ok"}


app.include_router(personnel_router, prefix="/personnel", tags=["personnel"])
app.include_router(warehouse_router, prefix="/warehouse", tags=["warehouse"])
app.include_router(planning_router, prefix="/planning", tags=["planning"])
