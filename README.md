# 🏋️ CrossFit Reservas MVP

Sistema automatizado de reservas para clases de CrossFit utilizando FastAPI y Playwright.

## 🚀 Características Principales

- ✅ **API REST** con FastAPI y documentación automática
- ✅ **Automatización Web** con Playwright (modo headless/visual)
- ✅ **Reservas inmediatas** por fecha y clase específica
- ✅ **Detección inteligente** de cupos disponibles
- ✅ **Manejo de errores tipificados** (sin cupos, credenciales, técnicos)
- ✅ **Logging robusto** con Loguru y niveles configurables
- ✅ **Docker Ready** con docker-compose para desarrollo y producción
- ✅ **Soporte multiidioma** (español/inglés) en el sitio web

## 📋 Descripción

Este proyecto automatiza las reservas de clases de CrossFit que tienen cupos limitados y se agotan en segundos. El sistema navega automáticamente por el sitio web del gimnasio, realiza login, encuentra la clase específica y ejecuta la reserva.

### Problema Resuelto
Las clases populares de CrossFit se agotan en 1-5 segundos. Este sistema permite realizar reservas automáticas en el momento exacto que se abren (25 horas antes del inicio de la clase).

## 🏗️ Arquitectura

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   FastAPI   │───▶│ Reservation  │───▶│ Web Automation  │
│   Endpoint  │    │   Manager    │    │   (Playwright)  │
└─────────────┘    └──────────────┘    └─────────────────┘
       │                   │                     │
       ▼                   ▼                     ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Swagger   │    │ Config       │    │   CrossFit      │
│    Docs     │    │ Manager      │    │   Website       │
└─────────────┘    └──────────────┘    └─────────────────┘
```

## � Inicio Rápido

### Prerrequisitos
- Docker y Docker Compose
- Variables de entorno configuradas en `.env`

### Instalación y Ejecución

1. **Clonar el repositorio:**
```bash
git clone <repo-url>
cd vscode-reserva
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

3. **Ejecutar con Docker:**
```bash
# Desarrollo
docker-compose up --build

# En background
docker-compose up -d --build
```

4. **Acceder a la documentación:**
- API Docs: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- Health Check: http://localhost:8001/health

## 🎯 Uso de la API

### Reserva Inmediata
```bash
curl -X POST "http://localhost:8001/api/reservas/inmediata" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_clase": "17:00 CrossFit 17:00-18:00",
    "fecha": "VI 19"
  }'
```

### Respuesta Exitosa
```json
{
  "id": "uuid-here",
  "clase_nombre": "17:00 CrossFit 17:00-18:00",
  "estado": "exitosa",
  "fecha_ejecucion": "2025-07-20T22:31:34.141644",
  "mensaje": "Reserva exitosa para 17:00 CrossFit 17:00-18:00",
  "error_type": null
}
```

### Sin Cupos Disponibles
```json
{
  "id": "uuid-here",
  "clase_nombre": "Competitor 19:00-20:00",
  "estado": "fallida",
  "fecha_ejecucion": "2025-07-20T22:31:34.141644",
  "mensaje": "No se pudo reservar Competitor 19:00-20:00: No quedan cupos disponibles",
  "error_type": "NO_CUPOS"
}
```

## 📁 Estructura del Proyecto

```
├── app/
│   ├── main.py              # FastAPI app principal
│   ├── api/
│   │   └── reservas.py      # Endpoints de reservas
│   ├── models/
│   │   └── reserva.py       # Modelos Pydantic
│   └── services/
│       ├── reservation_manager.py  # Orquestador principal
│       ├── web_automation.py       # Automatización Playwright
│       └── config_manager.py       # Gestión de configuración
├── config/
│   └── clases.json          # Configuración de clases
├── docs/                    # Documentación técnica detallada
├── docker-compose.yml       # Configuración Docker
├── Dockerfile              # Imagen Docker
└── requirements.txt        # Dependencias Python
```

## ⚙️ Configuración

### Variables de Entorno (.env)
```bash
# Credenciales del sitio web
CROSSFIT_URL=https://go.boxmagic.app/bienvenida/entrada?modo=ingreso
USERNAME=tu_email@ejemplo.com
PASSWORD=tu_password

# Configuración de la aplicación
LOG_LEVEL=WARNING           # INFO, WARNING, ERROR
BROWSER_HEADLESS=true       # true=sin ventana, false=con ventana
PORT=8001
```

## 🔧 Tipos de Error

| Error Type | Descripción | Reintentable |
|------------|-------------|--------------|
| `NO_CUPOS` | Sin cupos disponibles | ❌ No |
| `CREDENTIALS_ERROR` | Credenciales incorrectas | ❌ No |
| `UNEXPECTED_ERROR` | Error técnico/red | ✅ Sí |

## 📚 Documentación Técnica

Consulta el directorio `docs/technical/` para documentación detallada:

- **[📖 Índice General](docs/technical/README.md)** - Estado actual y roadmap
- **[📡 API Endpoints](docs/technical/api-endpoints.md)** - Documentación completa de endpoints
- **[🔄 Flujo de Reserva](docs/technical/flujo-reserva.md)** - Proceso técnico detallado
- **[🏗️ Arquitectura](docs/technical/arquitectura-sistema.md)** - Diseño del sistema

### Documentación Original

Para contexto histórico del proyecto:
- [`docs/00-resumen-ejecutivo.md`](docs/00-resumen-ejecutivo.md) - Resumen ejecutivo
- [`docs/01-analisis-problema.md`](docs/01-analisis-problema.md) - Análisis del problema
- [`docs/MVP-diseño-sistema.md`](docs/MVP-diseño-sistema.md) - Diseño inicial

## 🐛 Troubleshooting

### Logs en Docker
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs crossfit-reservas
```

### Debugging
- Cambiar `BROWSER_HEADLESS=false` para ver el navegador
- Cambiar `LOG_LEVEL=INFO` para más detalles
- Usar `/docs` para probar endpoints interactivamente

## 🚀 Próximas Funcionalidades

- [ ] **Scheduler automático** para reservas programadas
- [ ] **Notificaciones** (email/webhook) de resultados
- [ ] **Dashboard web** para monitoreo
- [ ] **Múltiples clases** por día
- [ ] **Reintentos inteligentes** en errores técnicos

## 🤝 Contribución

1. Fork el proyecto
2. Crear branch de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es de uso personal.