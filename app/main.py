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

    # --- Ejecución automática de reserva programada al iniciar el servidor ---
    from app.services.config_manager import ConfigManager
    from app.models import ReservaProgramadaRequest
    from app.services.scheduled_reservation_manager import ScheduledReservationManager
    import asyncio

    logger.info("🔎 Verificando si corresponde ejecutar reserva programada al iniciar el servidor...")
    config_manager = ConfigManager()
    params = config_manager.detectar_clase_para_hoy()
    if params:
        logger.info(f"✅ Clase activa detectada para hoy: {params['nombre_clase']} - Ejecutando reserva programada...")
        request = ReservaProgramadaRequest(**params)
        scheduled_manager = ScheduledReservationManager()
        # Ejecutar en background (no bloquear el arranque)
        asyncio.create_task(scheduled_manager.execute_scheduled_reservation(request))
    else:
        logger.info("⏭️  No hay clase activa para reservar hoy. No se ejecuta reserva automática.")

    # --- Log para depuración: mostrar reservas en curso antes y después ---
    from app.api.reservas import reservas_en_curso
    logger.info(f"[STARTUP] reservas_en_curso antes: {reservas_en_curso}")
    key = (params['nombre_clase'], params['fecha_reserva'], params['hora_reserva'])
    reservas_en_curso[key] = True
    logger.info(f"[STARTUP] reservas_en_curso después: {reservas_en_curso}")

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

@app.get("/health")
@app.head("/health")
async def health_check():
    """Endpoint de health check para Docker"""
    return {
        "status": "healthy",
        "service": "CrossFit Reservas MVP",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🌐 Iniciando servidor en puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
