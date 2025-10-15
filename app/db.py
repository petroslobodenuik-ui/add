from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, echo=False)
