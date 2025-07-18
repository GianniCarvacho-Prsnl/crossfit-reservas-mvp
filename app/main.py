import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger.remove()  # Remover el logger por defecto
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=os.getenv("LOG_LEVEL", "INFO")
)

# Importar routers
from app.api.reservas import router as reservas_router

# Crear la aplicación FastAPI
app = FastAPI(
    title="CrossFit Reservas MVP",
    description="Sistema automatizado de reservas para clases de CrossFit",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(reservas_router, prefix="/api", tags=["Reservas"])

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("🚀 Iniciando CrossFit Reservas MVP...")
    logger.info(f"📍 URL del sitio: {os.getenv('CROSSFIT_URL')}")
    logger.info(f"👤 Usuario: {os.getenv('USERNAME')}")
    logger.info("✅ Aplicación iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("🛑 Cerrando aplicación...")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "CrossFit Reservas MVP", 
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🌐 Iniciando servidor en puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
