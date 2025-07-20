# 📚 Índice de Documentación Técnica

## Estado Actual del Proyecto

**Versión:** MVP 1.0  
**Fecha:** Julio 2025  
**Estado:** ✅ Funcional - Reservas inmediatas implementadas  

### Funcionalidades Completadas

- ✅ **API REST** con endpoint de reserva inmediata
- ✅ **Automatización web** con Playwright (modo headless/visual)  
- ✅ **Detección inteligente** de cupos disponibles
- ✅ **Manejo de errores tipificados** (sin cupos, credenciales, técnicos)
- ✅ **Soporte multiidioma** (español/inglés)
- ✅ **Dockerización** completa con docker-compose
- ✅ **Logging estructurado** con niveles configurables
- ✅ **Documentación API** automática con Swagger

## 📖 Documentación Disponible

### 📡 API y Endpoints
- **[`api-endpoints.md`](api-endpoints.md)** - Documentación completa de todos los endpoints
  - Detalles del endpoint `/api/reservas/inmediata`
  - Ejemplos de requests y responses
  - Códigos de error y tipos de error
  - Validaciones de entrada

### 🔄 Flujo Técnico  
- **[`flujo-reserva.md`](flujo-reserva.md)** - Flujo detallado del proceso de reserva
  - Diagrama de flujo completo con Mermaid
  - 6 pasos técnicos del proceso de automatización
  - Tiempos estimados y optimizaciones
  - Estrategias de detección multiidioma
  - Métricas de performance

### 🏗️ Arquitectura
- **[`arquitectura-sistema.md`](arquitectura-sistema.md)** - Arquitectura completa del sistema
  - Patrón en capas (Layered Architecture)
  - Componentes y responsabilidades
  - Patrones de diseño implementados
  - Decisiones técnicas clave
  - Roadmap de evolución

## 🎯 Próximos Desarrollos

### Fase 2: Sistema de Scheduling Automático

**Objetivo:** Implementar reservas programadas que se ejecuten automáticamente 25 horas antes del inicio de cada clase.

#### Componentes a Desarrollar:

1. **Scheduler Service**
   - Cálculo automático de timing (25h antes)
   - Sistema de colas de tareas
   - Monitoreo de ejecución

2. **Database Layer**  
   - Persistencia de reservas programadas
   - Historial de ejecuciones
   - Configuración dinámica de clases

3. **Notification System**
   - Notificaciones de éxito/fallo
   - Alertas de cupos agotados  
   - Dashboard de monitoreo

#### Endpoints Nuevos:
```
POST /api/reservas/programar     # Programar reserva futura
GET  /api/reservas/programadas   # Listar reservas programadas  
DELETE /api/reservas/{id}        # Cancelar reserva programada
GET  /api/reservas/historial     # Historial de ejecuciones
```

### Fase 3: Dashboard y Observabilidad

**Objetivo:** Interfaz web para monitoreo y gestión del sistema.

#### Componentes:
1. **Web Dashboard**
   - Estado de reservas en tiempo real
   - Métricas de éxito/fallo
   - Configuración de clases

2. **Monitoring Stack**  
   - Métricas con Prometheus
   - Visualización con Grafana
   - Alerting automático

## 🛠️ Contexto para Próximos Desarrollos

### Información Clave del Sistema Actual

#### Estructura de Datos
```json
// Formato actual de request
{
  "nombre_clase": "17:00 CrossFit 17:00-18:00",
  "fecha": "VI 19"
}

// Formato de response
{
  "id": "uuid",
  "clase_nombre": "string", 
  "estado": "exitosa|fallida",
  "fecha_ejecucion": "datetime",
  "mensaje": "string",
  "error_type": "NO_CUPOS|CREDENTIALS_ERROR|UNEXPECTED_ERROR|null"
}
```

#### Servicios Principales
- **`ReservationManager`** - Orquestador principal (entry point para nuevas funcionalidades)
- **`WebAutomationService`** - Automatización estable (no tocar a menos que sea necesario)
- **`ConfigManager`** - Gestión de configuración (extender para DB en el futuro)

#### Puntos de Extensión Identificados
1. **Timing Logic** - Agregar en `ReservationManager` para cálculos de 25h
2. **Scheduling** - Nuevo servicio `SchedulerService` 
3. **Persistence** - Nuevo `DatabaseManager` para reemplazar JSON
4. **Notifications** - Nuevo `NotificationService` para alertas

#### Configuración Actual
```bash
# Variables de entorno críticas
CROSSFIT_URL=https://go.boxmagic.app/bienvenida/entrada?modo=ingreso
USERNAME=tu_email@ejemplo.com  
PASSWORD=tu_password
BROWSER_HEADLESS=true
LOG_LEVEL=WARNING
```

#### Métricas de Performance Actuales
- **Tiempo total reserva:** 25-30 segundos
- **Éxito rate:** ~95% (cuando hay cupos)
- **Detección sin cupos:** 100% precisa
- **Soporte multiidioma:** Español/Inglés

## 📋 Tareas de Preparación para Fase 2

### Análisis Previo Necesario
1. **Timing Strategy** - Definir exactamente cuándo ejecutar cada reserva
2. **Queue System** - Decidir entre Celery, RQ o scheduler nativo
3. **Database Choice** - SQLite vs PostgreSQL vs MongoDB
4. **Notification Channels** - Email, webhook, Slack, etc.

### Refactoring Requerido  
1. **Extract Configuration** - Mover de JSON a base de datos
2. **Add Persistence Layer** - Abstraer almacenamiento
3. **Enhance Error Handling** - Reintentos inteligentes
4. **Add Metrics Collection** - Instrumentación para monitoreo

## 🔗 Enlaces Útiles

### Documentación Externa
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Playwright Python API](https://playwright.dev/python/)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/)

### Documentación del Proyecto Original
- [`docs/00-resumen-ejecutivo.md`](../00-resumen-ejecutivo.md) - Visión general del proyecto
- [`docs/01-analisis-problema.md`](../01-analisis-problema.md) - Análisis del problema original
- [`docs/MVP-diseño-sistema.md`](../MVP-diseño-sistema.md) - Diseño inicial del MVP

### Requerimientos Originales
- [`requerimiento/flujo-navegacion.md`](../../requerimiento/flujo-navegacion.md) - Flujo de navegación detallado
- [`requerimiento/Specs.md`](../../requerimiento/Specs.md) - Especificaciones técnicas
- [`requerimiento-simple/requerimiento MVP.md`](../../requerimiento-simple/requerimiento%20MVP.md) - Requerimientos simplificados

## 🎯 Conclusión

El sistema actual está **sólido y funcionando correctamente** para reservas inmediatas. La arquitectura implementada facilita la extensión hacia un sistema de scheduling automático completo.

**Próximo paso recomendado:** Comenzar con el diseño del `SchedulerService` y la lógica de cálculo de timing para reservas automáticas.
