from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from routers import hazards, aviation, maritime, markets

load_dotenv()

app = FastAPI(
    title="Global Intelligence API",
    description="Real-time data: aviation, maritime, natural hazards, and financial markets.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hazards.router, prefix="/hazards", tags=["Natural Hazards"])
app.include_router(aviation.router, prefix="/aviation", tags=["Aviation"])
app.include_router(maritime.router, prefix="/maritime", tags=["Maritime"])
app.include_router(markets.router, prefix="/markets", tags=["Markets"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def frontend():
    return FileResponse("index.html")
