# Definición de Endpoints y APIs

## 1. Arquitectura de la API

### Visión General de la API

El sistema expone una API REST usando FastAPI para gestionar el proceso de reservas automáticas. La API está diseñada para ser simple pero efectiva, priorizando la funcionalidad core sobre features avanzadas.

```mermaid
graph TB
    subgraph "API Gateway"
        A[FastAPI Router]
    end
    
    subgraph "Endpoints"
        B[/health]
        C[/config]
        D[/schedule]
        E[/reservation]
        F[/status]
        G[/logs]
    end
    
    subgraph "Services"
        H[Health Service]
        I[Config Service]
        J[Scheduler Service]
        K[Reservation Service]
        L[Status Service]
        M[Log Service]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    
    B --> H
    C --> I
    D --> J
    E --> K
    F --> L
    G --> M
```

## 2. Definición de Endpoints

### 2.1 Health Check Endpoints

#### GET /health
**Descripción**: Verificar estado general del sistema
**Uso**: Health check para monitoreo y deployment

```yaml
summary: Sistema de health check
responses:
  200:
    description: Sistema operativo
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [healthy, degraded, unhealthy]
            timestamp:
              type: string
              format: date-time
            version:
              type: string
            components:
              type: object
              properties:
                browser:
                  type: string
                  enum: [ok, error]
                scheduler:
                  type: string
                  enum: [running, stopped, error]
                config:
                  type: string
                  enum: [loaded, error]
```

**Ejemplo de Respuesta**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T15:30:00-03:00",
  "version": "1.0.0",
  "components": {
    "browser": "ok",
    "scheduler": "running",
    "config": "loaded"
  }
}
```

#### GET /health/ready
**Descripción**: Verificar que el sistema está listo para procesar reservas
**Uso**: Readiness probe para Kubernetes/Docker

```yaml
summary: Verificar readiness del sistema
responses:
  200:
    description: Sistema listo
  503:
    description: Sistema no está listo
```

### 2.2 Configuration Endpoints

#### GET /config/classes
**Descripción**: Obtener configuración actual de clases

```yaml
summary: Obtener configuración de clases
responses:
  200:
    description: Configuración de clases
    content:
      application/json:
        schema:
          type: object
          properties:
            classes:
              type: object
              additionalProperties:
                type: object
                properties:
                  class_name:
                    type: string
                  start_time:
                    type: string
                  end_time:
                    type: string
                  enabled:
                    type: boolean
```

**Ejemplo de Respuesta**:
```json
{
  "classes": {
    "monday": {
      "class_name": "CrossFit",
      "start_time": "08:00",
      "end_time": "09:00",
      "enabled": true
    },
    "wednesday": {
      "class_name": "Competitor",
      "start_time": "19:00",
      "end_time": "20:00", 
      "enabled": true
    }
  }
}
```

#### PUT /config/classes
**Descripción**: Actualizar configuración de clases

```yaml
summary: Actualizar configuración de clases
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          classes:
            type: object
responses:
  200:
    description: Configuración actualizada
  400:
    description: Error de validación
```

#### GET /config/settings
**Descripción**: Obtener configuración general del sistema

```yaml
summary: Obtener configuración del sistema
responses:
  200:
    description: Configuración del sistema
    content:
      application/json:
        schema:
          type: object
          properties:
            timezone:
              type: string
            reservation_offset_hours:
              type: integer
            preparation_minutes:
              type: integer
            browser_settings:
              type: object
```

### 2.3 Schedule Management Endpoints

#### GET /schedule/next
**Descripción**: Obtener próximas reservas programadas

```yaml
summary: Obtener próximas reservas
parameters:
  - name: limit
    in: query
    schema:
      type: integer
      default: 10
responses:
  200:
    description: Lista de próximas reservas
    content:
      application/json:
        schema:
          type: object
          properties:
            reservations:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  class_name:
                    type: string
                  class_start_time:
                    type: string
                    format: date-time
                  reservation_time:
                    type: string
                    format: date-time
                  status:
                    type: string
                    enum: [scheduled, preparing, executing, completed, failed]
                  time_until_reservation:
                    type: string
```

**Ejemplo de Respuesta**:
```json
{
  "reservations": [
    {
      "id": "res_001",
      "class_name": "Competitor 19:00-20:00",
      "class_start_time": "2025-01-17T19:00:00-03:00",
      "reservation_time": "2025-01-16T18:00:00-03:00",
      "status": "scheduled",
      "time_until_reservation": "2h 30m 15s"
    }
  ]
}
```

#### POST /schedule/manual
**Descripción**: Programar una reserva manual (fuera del horario automático)

```yaml
summary: Programar reserva manual
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          class_name:
            type: string
          class_start_time:
            type: string
            format: date-time
          reservation_time:
            type: string
            format: date-time
        required:
          - class_name
          - class_start_time
          - reservation_time
responses:
  201:
    description: Reserva programada
  400:
    description: Error de validación
```

#### DELETE /schedule/{reservation_id}
**Descripción**: Cancelar una reserva programada

```yaml
summary: Cancelar reserva
parameters:
  - name: reservation_id
    in: path
    required: true
    schema:
      type: string
responses:
  200:
    description: Reserva cancelada
  404:
    description: Reserva no encontrada
```

### 2.4 Reservation Execution Endpoints

#### POST /reservation/execute
**Descripción**: Ejecutar reserva inmediatamente (para testing)

```yaml
summary: Ejecutar reserva inmediata
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          class_name:
            type: string
          dry_run:
            type: boolean
            default: false
        required:
          - class_name
responses:
  200:
    description: Reserva ejecutada exitosamente
  400:
    description: Error en parámetros
  500:
    description: Error en ejecución
```

#### GET /reservation/{reservation_id}/status
**Descripción**: Obtener estado detallado de una reserva

```yaml
summary: Estado de reserva específica
parameters:
  - name: reservation_id
    in: path
    required: true
    schema:
      type: string
responses:
  200:
    description: Estado de la reserva
    content:
      application/json:
        schema:
          type: object
          properties:
            id:
              type: string
            status:
              type: string
            start_time:
              type: string
              format: date-time
            end_time:
              type: string
              format: date-time
            steps:
              type: array
              items:
                type: object
                properties:
                  step:
                    type: string
                  status:
                    type: string
                  timestamp:
                    type: string
                    format: date-time
                  details:
                    type: string
```

### 2.5 System Status Endpoints

#### GET /status/system
**Descripción**: Estado detallado del sistema

```yaml
summary: Estado detallado del sistema
responses:
  200:
    description: Estado del sistema
    content:
      application/json:
        schema:
          type: object
          properties:
            uptime:
              type: string
            scheduler:
              type: object
              properties:
                status:
                  type: string
                active_jobs:
                  type: integer
                next_execution:
                  type: string
                  format: date-time
            browser:
              type: object
              properties:
                status:
                  type: string
                version:
                  type: string
                last_test:
                  type: string
                  format: date-time
            timing:
              type: object
              properties:
                current_time:
                  type: string
                  format: date-time
                ntp_sync_status:
                  type: string
                time_drift_ms:
                  type: integer
```

#### GET /status/metrics
**Descripción**: Métricas de rendimiento del sistema

```yaml
summary: Métricas del sistema
responses:
  200:
    description: Métricas de rendimiento
    content:
      application/json:
        schema:
          type: object
          properties:
            success_rate:
              type: number
              format: float
            average_execution_time:
              type: number
              format: float
            total_reservations:
              type: integer
            failed_reservations:
              type: integer
            timing_accuracy:
              type: object
              properties:
                average_drift_ms:
                  type: number
                max_drift_ms:
                  type: number
```

### 2.6 Logging and Debugging Endpoints

#### GET /logs
**Descripción**: Obtener logs del sistema

```yaml
summary: Obtener logs
parameters:
  - name: level
    in: query
    schema:
      type: string
      enum: [DEBUG, INFO, WARNING, ERROR]
  - name: limit
    in: query
    schema:
      type: integer
      default: 100
  - name: since
    in: query
    schema:
      type: string
      format: date-time
responses:
  200:
    description: Logs del sistema
    content:
      application/json:
        schema:
          type: object
          properties:
            logs:
              type: array
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                    format: date-time
                  level:
                    type: string
                  message:
                    type: string
                  context:
                    type: object
```

#### GET /logs/reservation/{reservation_id}
**Descripción**: Logs específicos de una reserva

```yaml
summary: Logs de reserva específica
parameters:
  - name: reservation_id
    in: path
    required: true
    schema:
      type: string
responses:
  200:
    description: Logs de la reserva
```

### 2.7 Administrative Endpoints

#### POST /admin/scheduler/start
**Descripción**: Iniciar el scheduler

```yaml
summary: Iniciar scheduler
responses:
  200:
    description: Scheduler iniciado
  409:
    description: Scheduler ya está ejecutándose
```

#### POST /admin/scheduler/stop
**Descripción**: Detener el scheduler

```yaml
summary: Detener scheduler
responses:
  200:
    description: Scheduler detenido
```

#### POST /admin/browser/test
**Descripción**: Probar conectividad del browser

```yaml
summary: Test de browser
responses:
  200:
    description: Browser funcionando correctamente
  500:
    description: Error en browser
```

## 3. Modelos de Datos

### Esquemas Pydantic

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class ReservationStatus(str, Enum):
    SCHEDULED = "scheduled"
    PREPARING = "preparing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class ClassConfig(BaseModel):
    class_name: str
    start_time: str = Field(pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    enabled: bool = True

class ReservationTask(BaseModel):
    id: str
    class_name: str
    class_start_time: datetime
    reservation_time: datetime
    status: ReservationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

class SystemStatus(BaseModel):
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]

class ExecutionStep(BaseModel):
    step: str
    status: str
    timestamp: datetime
    details: Optional[str] = None
    duration_ms: Optional[int] = None
```

## 4. Manejo de Errores

### Códigos de Error Estándar

| Código HTTP | Descripción | Uso |
|-------------|-------------|-----|
| 200 | OK | Operación exitosa |
| 201 | Created | Recurso creado |
| 400 | Bad Request | Error en parámetros |
| 401 | Unauthorized | Credenciales inválidas |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Conflicto de estado |
| 422 | Unprocessable Entity | Error de validación |
| 500 | Internal Server Error | Error interno |
| 503 | Service Unavailable | Servicio no disponible |

### Formato de Respuesta de Error

```json
{
  "error": {
    "code": "RESERVATION_FAILED",
    "message": "Failed to execute reservation",
    "details": {
      "step": "button_click",
      "reason": "Element not found",
      "timestamp": "2025-01-16T18:00:05-03:00"
    },
    "request_id": "req_12345"
  }
}
```

## 5. Consideraciones de Seguridad para APIs

### Autenticación
- API Key simple para acceso básico
- Rate limiting por IP
- Validación de origen para requests críticos

### Validación
- Validación estricta de todos los inputs
- Sanitización de datos de configuración
- Límites en tamaños de payload

Esta definición de API proporciona una interfaz completa para gestionar y monitorear el sistema de reservas automáticas, manteniendo la simplicidad requerida para una aplicación personal pero con la robustez necesaria para operación confiable.
