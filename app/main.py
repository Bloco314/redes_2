from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import Base, engine

from .routers import auth, accounts, transactions, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SecureBank API",
    description="Simulador bancário para estudo de segurança de redes",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(admin.router)


@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok"}
