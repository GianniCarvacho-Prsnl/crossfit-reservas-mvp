# Plan de Implementación: Punto de Entrada Principal para Reservas

Este plan detalla los pasos para implementar la mejora descrita en el documento de diseño, integrando el endpoint `/reservas/programada` y asegurando la ejecución automática y bajo demanda de reservas.

---

## 1. Función de Detección de Reserva para Hoy
- Crear una función utilitaria que lea `/config/clases.json`.
- Detectar si hay una clase activa para el día de hoy (comparando `fecha_reserva` con lower() y tildes).
- Devolver los parámetros necesarios para la reserva si corresponde.
- Ubicación sugerida: `app/services/config_manager.py` o un nuevo módulo utilitario.
- **Pruebas:** Unitarias para distintos escenarios de JSON y días.
- **Referencia diseño:** Ver sección "1. Detección de reservas para hoy" en [Diseño de la mejora](diseno-punto-entrada-reservas.md).

## 2. Mapeo de Parámetros para Reserva
- Implementar la lógica para transformar la información de la clase activa en los parámetros requeridos por `/reservas/programada`:
  - `nombre_clase` (del JSON)
  - `fecha_clase` (prefijo de dos letras en inglés + número de día de mañana)
  - `fecha_reserva` (fecha de hoy en formato `aaaa-mm-dd`)
  - `hora_reserva` (del JSON, asegurando formato `hh:mm:ss`)
- Separar esta lógica en función propia si es necesario para facilitar pruebas.
- **Pruebas:** Unitarias para el mapeo correcto de días y fechas.
- **Referencia diseño:** Ver sección "2. Mapeo de parámetros" y "Tabla de mapeo días" en [Diseño de la mejora](diseno-punto-entrada-reservas.md).

## 3. Ejecución Interna de Reserva
- Crear una función que invoque internamente el endpoint `/reservas/programada` (llamada directa a la función Python, no HTTP).
- Manejar la respuesta y errores como si fuera una llamada externa.
- **Pruebas:** Unitarias y de integración para la función de ejecución.
- **Referencia diseño:** Ver sección "3. Invocación del endpoint de reserva programada" en [Diseño de la mejora](diseno-punto-entrada-reservas.md).

## 4. Integración en el Arranque del Servidor
- Modificar `main.py` para que, al iniciar el servidor, se ejecute la detección y reserva automática si corresponde.
- Garantizar que esto ocurra solo una vez por arranque.
- Agregar logs claros del proceso.
- **Pruebas:** Manuales y automáticas (si es posible) para el arranque.
- **Referencia diseño:** Ver sección "1. Ejecución automática al iniciar el servidor" y "Flujo General" en [Diseño de la mejora](diseno-punto-entrada-reservas.md).

## 5. Nuevo Endpoint de Ejecución Bajo Demanda
- Exponer un endpoint (ej: `/api/ejecutar-reservas-hoy`) que ejecute el mismo flujo de reserva automática.
- Reutilizar la lógica implementada.
- Devolver la misma respuesta que `/reservas/programada`.
- **Pruebas:** Unitarias y de integración para el endpoint.
- **Referencia diseño:** Ver sección "2. Nuevo endpoint de ejecución bajo demanda" y "Flujo General" en [Diseño de la mejora](diseno-punto-entrada-reservas.md).

## 6. Pruebas y Documentación
- Agregar pruebas unitarias y de integración para cada función clave.
- Documentar el flujo, dependencias y puntos de extensión para futuras mejoras (ej: soporte a múltiples reservas por día).
- **Referencia diseño:** Ver sección "Consideraciones y Decisiones" en [Diseño de la mejora](diseno-punto-entrada-reservas.md).

---

## Estructura esperada del endpoint

```json
{
  "nombre_clase": "18:00 CrossFit 18:00-19:00",
  "fecha_clase": "LU 21",
  "fecha_reserva": "2025-01-19",
  "hora_reserva": "17:00:00"
}
```

## Ejemplos de Mapeo y Llamada al Endpoint

A continuación se muestran ejemplos prácticos de cómo, partiendo de un registro real del archivo `/config/clases.json`, se mapean los campos y se realiza la llamada al endpoint `/api/reservas/programada`.

### Caso 1: Sábado

**Supongamos que hoy es Sábado 26 de julio de 2025.**

Registro en el JSON:
```json
{
  "nombre_clase": "08:00 METCOM 10:00-11:00",
  "fecha_reserva": "Sábado",
  "hora_reserva": "09:00:00",
  "activo": true
}
```

**Mapeo:**
- `nombre_clase`: "08:00 METCOM 10:00-11:00" (del JSON)
- `fecha_clase`: "SU 27" (domingo, mañana es 27, usando el mapeo de días)
- `fecha_reserva`: "2025-07-26" (fecha de hoy en formato ISO)
- `hora_reserva`: "09:00:00" (del JSON)

**Llamada al endpoint:**
```json
{
  "nombre_clase": "08:00 METCOM 10:00-11:00",
  "fecha_clase": "SU 27",
  "fecha_reserva": "2025-07-26",
  "hora_reserva": "09:00:00"
}
```

---

### Caso 2: Miércoles

**Supongamos que hoy es Miércoles 30 de julio de 2025.**

Registro en el JSON:
```json
{
  "nombre_clase": "19:00 CrossFit 19:00-20:00",
  "fecha_reserva": "Miércoles",
  "hora_reserva": "19:00:00",
  "activo": true
}
```

**Mapeo:**
- `nombre_clase`: "19:00 CrossFit 19:00-20:00"
- `fecha_clase`: "TH 31" (jueves, mañana es 31)
- `fecha_reserva`: "2025-07-30"
- `hora_reserva`: "19:00:00"

**Llamada al endpoint:**
```json
{
  "nombre_clase": "19:00 CrossFit 19:00-20:00",
  "fecha_clase": "TH 31",
  "fecha_reserva": "2025-07-30",
  "hora_reserva": "19:00:00"
}
```

---

### Caso 3: Lunes

**Supongamos que hoy es Lunes 4 de agosto de 2025.**

Registro en el JSON:
```json
{
  "nombre_clase": "07:00 Competitor 07:00-08:00",
  "fecha_reserva": "Lunes",
  "hora_reserva": "07:00:00",
  "activo": true
}
```

**Mapeo:**
- `nombre_clase`: "07:00 Competitor 07:00-08:00"
- `fecha_clase`: "TU 5" (martes, mañana es 5)
- `fecha_reserva`: "2025-08-04"
- `hora_reserva`: "07:00:00"

**Llamada al endpoint:**
```json
{
  "nombre_clase": "07:00 Competitor 07:00-08:00",
  "fecha_clase": "TU 5",
  "fecha_reserva": "2025-08-04",
  "hora_reserva": "07:00:00"
}
```

---

**Referencia diseño:** Ver sección "2. Mapeo de parámetros" y ejemplos en [Diseño de la mejora](diseno-punto-entrada-reservas.md).

---

## Recomendaciones
- Mantener la lógica desacoplada y testeable.
- Documentar claramente cada función y endpoint.
- Considerar logs adicionales solo si aportan valor.


---

**Referencias:**
- [Diseño de la mejora](diseno-punto-entrada-reservas.md)
- [reservas.py](../app/api/reservas.py)
- [config_manager.py](../app/services/config_manager.py)
- [scheduled_reservation_manager.py](../app/services/scheduled_reservation_manager.py)
- [main.py](../app/main.py)

---

Este plan puede ser refinado según se detecten detalles adicionales durante la implementación.
