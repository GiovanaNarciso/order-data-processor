from fastapi import FastAPI
from app.adapters.controller import router
from app.database.models import Base
from app.database.session import engine

app = FastAPI(
    title="Order Normalizer API",
    description="Transforms legacy order files into a normalized JSON structure",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
