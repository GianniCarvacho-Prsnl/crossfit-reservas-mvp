# Documentación del Sistema de Reserva Automática BoxMagic

## Índice de Documentación

### 📋 Documentos Principales

1. **[Resumen Ejecutivo](00-resumen-ejecutivo.md)**
   - Visión general del proyecto
   - Objetivos y métricas de éxito
   - ROI y beneficios esperados

2. **[Análisis del Problema](01-analisis-problema.md)**
   - Entendimiento detallado del problema
   - Requerimientos funcionales y no funcionales
   - Casos de uso principales

3. **[Arquitectura y Tecnologías](02-arquitectura-tecnologias.md)**
   - Diseño de la arquitectura del sistema
   - Stack tecnológico seleccionado
   - Patrones de diseño aplicados

4. **[Endpoints y APIs](03-endpoints-apis.md)**
   - Definición completa de la API REST
   - Modelos de datos y schemas
   - Documentación de endpoints

5. **[Flujo de la Aplicación](04-flujo-aplicacion.md)**
   - Flujo detallado paso a paso
   - Diagramas de secuencia
   - Timing crítico y precisión temporal

6. **[Escenarios de Prueba](05-escenarios-prueba.md)**
   - Casos de prueba principales
   - Escenarios de estrés y recuperación
   - Criterios de validación

7. **[Gestión de Errores](06-gestion-errores.md)**
   - Estrategias de manejo de errores
   - Recuperación automática
   - Sistema de circuit breakers

8. **[Plan de Implementación](07-plan-implementacion.md)**
   - Roadmap detallado de desarrollo
   - Fases y entregables
   - Cronograma y recursos

## 🎯 Objetivos del Proyecto

### Problema Central
Las clases de CrossFit en BoxMagic tienen cupos limitados que se agotan en segundos. Las reservas se abren exactamente 25 horas antes del inicio de la clase, requiriendo una precisión temporal imposible de lograr manualmente.

### Solución
Sistema automatizado que ejecuta reservas en el segundo exacto de apertura, operando 24/7 sin intervención manual.

## 🏗️ Arquitectura de Alto Nivel

El sistema está compuesto por varios servicios interconectados que trabajan en conjunto para lograr reservas automáticas con precisión temporal crítica.

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sistema de Reserva Automática               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │  Scheduler  │───▶│   Timing    │───▶│   NTP Servers       │ │
│  │  Service    │    │   Service   │    │                     │ │
│  └─────┬───────┘    └─────────────┘    └─────────────────────┘ │
│        │                                                       │
│        ▼                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ Reservation │───▶│   Browser   │───▶│   BoxMagic Website  │ │
│  │   Engine    │    │   Manager   │    │                     │ │
│  └─────┬───────┘    └─────────────┘    └─────────────────────┘ │
│        │                                                       │
│        ▼                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │    Error    │    │   FastAPI   │    │   Configuration     │ │
│  │   Handler   │◀───│   Router    │───▶│     Manager         │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**� [Ver Diagrama Interactivo de Arquitectura](diagrams/arquitectura-sistema.md)**

**�🔄 [Ver Flujo de Secuencia Temporal](diagrams/flujo-secuencia.md)**

> **📝 Nota sobre Diagramas**: 
> - **Para diagramas interactivos**: Abre los archivos `.md` en [mermaid.live](https://mermaid.live)
> - **En VS Code**: Usa extensión "Markdown Preview Enhanced" (`Ctrl+Shift+P` → "MPE: Open Preview")
> - **Diagramas ASCII**: Se ven correctamente en cualquier editor

## 🔧 Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Runtime** | Python | 3.11+ |
| **Web Framework** | FastAPI | ^0.104 |
| **Web Automation** | Playwright | ^1.40 |
| **Scheduling** | APScheduler | ^3.10 |
| **Time Handling** | Pendulum | ^2.1 |
| **Logging** | Loguru | ^0.7 |
| **Containerization** | Docker | Latest |
| **Cloud Platform** | fly.io | - |

## ⚡ Características Clave

### Timing Crítico
- **Precisión**: ±100ms objetivo, ±500ms aceptable
- **Sincronización NTP**: Compensación automática de deriva temporal
- **Monitoreo**: Precisión sub-segundo en fase crítica

### Robustez
- **Recuperación Automática**: 95% de errores recuperables
- **Circuit Breakers**: Prevención de cascadas de fallas
- **Redundancia**: Múltiples estrategias de localización de elementos

### Observabilidad
- **Logging Estructurado**: Contexto completo para troubleshooting
- **Métricas**: Success rate, timing accuracy, performance
- **Health Checks**: Monitoreo continuo del estado del sistema

## 🚀 Inicio Rápido

### Prerrequisitos
```bash
# Python 3.11+
python --version

# Poetry para gestión de dependencias
pip install poetry

# Docker para containerización
docker --version
```

### Configuración Inicial
```bash
# Clonar repositorio
git clone <repository-url>
cd boxmagic-reserva

# Instalar dependencias
poetry install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con credenciales

# Instalar browsers de Playwright
poetry run playwright install chromium

# Ejecutar aplicación
poetry run uvicorn src.main:app --reload
```

### Configuración de Clases
```json
{
  "clases": {
    "lunes": {
      "clase": "CrossFit",
      "horario": "08:00-09:00",
      "habilitado": true
    },
    "miercoles": {
      "clase": "Competitor", 
      "horario": "19:00-20:00",
      "habilitado": true
    }
  }
}
```

## 📊 Métricas de Éxito

### Objetivos Primarios
- **Success Rate**: >95% de reservas exitosas
- **Timing Accuracy**: 90% dentro de ±500ms
- **System Uptime**: >99% disponibilidad

### Objetivos Secundarios  
- **Recovery Time**: <30s para errores recuperables
- **Navigation Time**: <80s tiempo total de navegación
- **Error Detection**: <3s para detectar fallas críticas

## 🔄 Flujo de Desarrollo

### Fase 1: MVP (Semana 1)
- ✅ Sistema de timing crítico
- ✅ Automatización web básica
- ✅ API REST funcional
- ✅ Testing inicial

### Fase 2: Robustez (Semana 2)
- ✅ Manejo avanzado de errores
- ✅ Logging y observabilidad
- ✅ Testing exhaustivo

### Fase 3: Deployment (Semana 3)
- ✅ Containerización
- ✅ CI/CD pipeline
- ✅ Deploy en cloud
- ✅ Monitoreo en producción

## 🛠️ APIs Principales

### Health Check
```bash
GET /health
# Respuesta: {"status": "healthy", "timestamp": "..."}
```

### Programar Reserva
```bash
POST /schedule/reservation
Content-Type: application/json

{
  "day": "monday",
  "class_name": "CrossFit",
  "start_time": "08:00",
  "end_time": "09:00"
}
```

### Estado del Sistema
```bash
GET /status/system
# Respuesta: Estado detallado de componentes
```

## 🚨 Gestión de Errores

### Estrategias de Recuperación
1. **Element Not Found**: Selectores alternativos y fallbacks
2. **Network Timeouts**: Reintentos con backoff exponencial
3. **Browser Failures**: Restart automático con preservación de contexto
4. **Server Errors**: Circuit breakers y degradación gradual

### Logging
- **Structured Logs**: JSON con contexto completo
- **Error Correlation**: IDs de trazabilidad
- **Performance Metrics**: Tiempos de ejecución y éxito

## 📈 Monitoreo y Alertas

### Métricas Clave
- **Reservation Success Rate**
- **Timing Accuracy Distribution**
- **Error Rate by Type**
- **System Resource Usage**

### Alertas Críticas
- Success rate < 80%
- Timing drift > 2s
- Browser failures > 3 consecutive
- System unavailable > 5min

## 🔐 Seguridad

### Consideraciones
- **Credential Management**: Variables de entorno seguras
- **Browser Fingerprinting**: Configuración human-like
- **Rate Limiting**: Evitar detección como bot
- **Network Security**: HTTPS obligatorio

## 📚 Recursos Adicionales

### Enlaces Útiles
- [Playwright Documentation](https://playwright.dev/python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [fly.io Documentation](https://fly.io/docs/)

### Soporte
- **Issues**: GitHub Issues para bugs y mejoras
- **Discussions**: GitHub Discussions para preguntas
- **Documentation**: Carpeta `docs/` para referencia completa

---

**Nota**: Esta documentación está diseñada como guía completa para el desarrollo del sistema. Cada documento en el índice proporciona detalles específicos de su área correspondiente.

**Última actualización**: 16 de enero de 2025
