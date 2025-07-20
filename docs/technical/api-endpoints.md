# 📡 API Endpoints - Documentación Técnica

## Resumen de Endpoints

| Endpoint | Método | Descripción | Estado |
|----------|--------|-------------|---------|
| `/` | GET | Endpoint raíz informativo | ✅ Activo |
| `/health` | GET/HEAD | Health check para Docker | ✅ Activo |
| `/api/reservas/inmediata` | POST | Ejecutar reserva inmediata | ✅ Activo |

---

## 🎯 `/api/reservas/inmediata` - Reserva Inmediata

### Descripción
Endpoint principal que ejecuta una reserva inmediata para una clase específica. Automatiza todo el flujo de navegación web desde login hasta confirmación de reserva.

### Request

#### Método: `POST`
#### Content-Type: `application/json`

#### Parámetros del Body:
```json
{
  "nombre_clase": "string",  // Nombre exacto como aparece en el sitio web
  "fecha": "string"          // Formato "XX ##" (ej: "VI 19", "JU 17")
}
```

#### Ejemplo de Request:
```bash
curl -X POST "http://localhost:8001/api/reservas/inmediata" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_clase": "17:00 CrossFit 17:00-18:00",
    "fecha": "VI 19"
  }'
```

### Response

#### Modelo de Respuesta:
```json
{
  "id": "string",                    // UUID único de la reserva
  "clase_nombre": "string",          // Nombre de la clase solicitada
  "estado": "exitosa|fallida",       // Estado final de la reserva
  "fecha_ejecucion": "datetime",     // Timestamp de ejecución
  "mensaje": "string",               // Descripción del resultado
  "error_type": "string|null"        // Tipo de error (si aplica)
}
```

### Casos de Respuesta

#### ✅ Reserva Exitosa
```json
{
  "id": "43b99371-b208-4c4a-8706-56db6348d753",
  "clase_nombre": "17:00 CrossFit 17:00-18:00",
  "estado": "exitosa",
  "fecha_ejecucion": "2025-07-20T22:31:34.141644",
  "mensaje": "Reserva exitosa para 17:00 CrossFit 17:00-18:00 - Confirmada con botón 'Cancelar reserva'",
  "error_type": null
}
```

#### ⚠️ Sin Cupos Disponibles
```json
{
  "id": "43b99371-b208-4c4a-8706-56db6348d753",
  "clase_nombre": "Competitor 19:00-20:00",
  "estado": "fallida",
  "fecha_ejecucion": "2025-07-20T22:31:34.141644",
  "mensaje": "No se pudo reservar Competitor 19:00-20:00: No quedan cupos disponibles",
  "error_type": "NO_CUPOS"
}
```

#### 📝 Clase Ya Reservada
```json
{
  "id": "43b99371-b208-4c4a-8706-56db6348d753",
  "clase_nombre": "17:00 CrossFit 17:00-18:00",
  "estado": "exitosa",
  "fecha_ejecucion": "2025-07-20T22:31:34.141644",
  "mensaje": "La clase 17:00 CrossFit 17:00-18:00 ya estaba reservada previamente",
  "error_type": null
}
```

#### ❌ Error de Credenciales
```json
{
  "id": "43b99371-b208-4c4a-8706-56db6348d753",
  "clase_nombre": "17:00 CrossFit 17:00-18:00",
  "estado": "fallida",
  "fecha_ejecucion": "2025-07-20T22:31:34.141644",
  "mensaje": "Credenciales no configuradas",
  "error_type": "CREDENTIALS_ERROR"
}
```

#### 🚨 Error Técnico
```json
{
  "id": "43b99371-b208-4c4a-8706-56db6348d753",
  "clase_nombre": "17:00 CrossFit 17:00-18:00",
  "estado": "fallida",
  "fecha_ejecucion": "2025-07-20T22:31:34.141644",
  "mensaje": "Error inesperado: Navigation timeout exceeded",
  "error_type": "UNEXPECTED_ERROR"
}
```

### Códigos de Estado HTTP

| Código | Descripción | Cuándo |
|--------|-------------|---------|
| `200` | OK | Respuesta exitosa (independiente del resultado de reserva) |
| `422` | Validation Error | Parámetros inválidos en el request |
| `500` | Internal Server Error | Error crítico del servidor |

### Tipos de Error

| Error Type | Descripción | Reintentable | Acción Recomendada |
|------------|-------------|--------------|-------------------|
| `null` | Sin error | N/A | N/A |
| `NO_CUPOS` | Sin cupos disponibles | ❌ No | Esperar siguiente clase |
| `CREDENTIALS_ERROR` | Credenciales incorrectas | ❌ No | Verificar configuración |
| `UNEXPECTED_ERROR` | Error técnico/red | ✅ Sí | Reintentar después |

### Validaciones de Input

#### `nombre_clase`:
- ✅ **Requerido**: Debe estar presente
- ✅ **Formato**: String exacto como aparece en el sitio
- ✅ **Ejemplos válidos**: 
  - `"17:00 CrossFit 17:00-18:00"`
  - `"Competitor 19:00-20:00"`
  - `"08:00 CrossFit 08:00-09:00"`

#### `fecha`:
- ✅ **Requerido**: Debe estar presente  
- ✅ **Formato**: "XX ##" donde XX es día de semana y ## es número
- ✅ **Ejemplos válidos**:
  - `"VI 19"` (Viernes 19)
  - `"JU 17"` (Jueves 17)
  - `"LU 21"` (Lunes 21)

---

## 🏥 `/health` - Health Check

### Descripción
Endpoint de verificación de estado del servicio, utilizado por Docker y sistemas de monitoreo.

### Request
#### Métodos: `GET`, `HEAD`
#### Sin parámetros

### Response
```json
{
  "status": "healthy",
  "service": "CrossFit Reservas MVP",
  "version": "1.0.0"
}
```

---

## 🏠 `/` - Endpoint Raíz

### Descripción
Endpoint informativo que proporciona información básica del servicio.

### Request
#### Método: `GET`
#### Sin parámetros

### Response
```json
{
  "message": "CrossFit Reservas MVP",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## 🔍 Debugging y Monitoreo

### Headers Útiles
```bash
# Para debugging detallado
curl -H "Accept: application/json" \
     -H "Content-Type: application/json" \
     -v \
     ...
```

### Logs Relacionados
Cada request genera logs estructurados:
```
2025-07-20 22:31:34 | INFO     | app.api.reservas:reserva_inmediata:12 - 🎯 Iniciando reserva inmediata para clase: 'Competitor 19:00-20:00'
2025-07-20 22:31:34 | WARNING  | app.services.reservation_manager:execute_immediate_reservation:67 - ⚠️ Sin cupos disponibles para: Competitor 19:00-20:00
```

### Métricas de Performance
- **Tiempo promedio**: 15-30 segundos por reserva
- **Tiempo de navegación**: 10-15 segundos
- **Tiempo de verificación**: 2-5 segundos
