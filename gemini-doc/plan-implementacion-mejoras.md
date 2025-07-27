# Plan de Implementación: Punto de Entrada Principal para Reservas

Este documento detalla los pasos técnicos para implementar la mejora descrita en el [documento de diseño: Punto de Entrada Principal para Reservas](../docs/technical/diseno-punto-entrada-reservas.md).

## Fases de Implementación

### Fase 1: Crear el Servicio Orquestador

El primer paso es centralizar la lógica descrita en el diseño en un nuevo servicio.

*   **Tarea 1.1: Crear el archivo del nuevo servicio**
    *   **Acción:** Crear el archivo `app/services/entry_point_manager.py`.
    *   **Propósito:** Este servicio contendrá la lógica para verificar y preparar las reservas del día.

*   **Tarea 1.2: Implementar la clase `EntryPointManager`**
    *   **Acción:** Dentro de `entry_point_manager.py`, crear la clase `EntryPointManager`.
    *   **Detalles:**
        *   El constructor (`__init__`) recibirá instancias de `ConfigManager` y `ScheduledReservationManager` para interactuar con la configuración y el sistema de reservas.
        *   Crear un método privado para obtener el nombre del día de la semana actual en español (ej: "sábado").
        *   Crear un método privado para mapear el nombre del día en español a su abreviatura en inglés (ej: "sábado" -> "sa"), según la [tabla de mapeo del diseño](../docs/technical/diseno-punto-entrada-reservas.md#tabla-de-mapeo-d%C3%ADas).
        *   Crear el método principal `execute_daily_reservation_check`, que:
            1.  Lea la configuración de `clases.json` usando `ConfigManager`.
            2.  Busque una clase activa que corresponda al día actual.
            3.  Si la encuentra, prepare los parámetros de la reserva (`nombre_clase`, `fecha_clase`, `fecha_reserva`, `hora_reserva`, `timezone`) como se especifica en el [mapeo de parámetros del diseño](../docs/technical/diseno-punto-entrada-reservas.md#2-mapeo-de-par%C3%A1metros).
            4.  Invoque el método `execute_scheduled_reservation` de `ScheduledReservationManager` con los parámetros preparados.
            5.  Retorne el resultado de la invocación.

### Fase 2: Integrar el Servicio en el Arranque de la Aplicación

Para cumplir con el requisito de ejecución automática, el nuevo servicio debe ser invocado al iniciar el servidor.

*   **Tarea 2.1: Modificar el archivo principal de la aplicación**
    *   **Acción:** Editar el archivo `app/main.py`.
    *   **Propósito:** Añadir un evento de `startup` de FastAPI para ejecutar la verificación de reservas.
    *   **Detalles:**
        *   Importar `EntryPointManager` y los otros servicios necesarios.
        *   Crear una función `async` que será decorada con `@app.on_event("startup")`.
        *   Dentro de esta función, instanciar `EntryPointManager` y llamar a `execute_daily_reservation_check`.
        *   Se recomienda ejecutar esta lógica como una tarea en segundo plano (`asyncio.create_task`) para no bloquear el inicio del servidor.
        *   Añadir logging para registrar si la tarea de verificación se inició correctamente.

### Fase 3: Exponer el Nuevo Endpoint de API

Para permitir la ejecución bajo demanda, se creará un nuevo endpoint.

*   **Tarea 3.1: Modificar el router de la API de reservas**
    *   **Acción:** Editar el archivo `app/api/reservas.py`.
    *   **Propósito:** Añadir un nuevo endpoint para la ejecución manual.
    *   **Detalles:**
        *   Añadir un nuevo endpoint `POST /reservas/ejecutar-verificacion-diaria`.
        *   La función de este endpoint instanciará `EntryPointManager` (similar a como se hace en el evento `startup`).
        *   Invocará el método `execute_daily_reservation_check` y retornará el resultado directamente.
        *   El endpoint debe manejar posibles excepciones y devolver una respuesta de error HTTP 500 si la ejecución falla.

### Fase 4: Pruebas y Verificación

Es fundamental asegurar que la nueva funcionalidad opera como se espera y no introduce regresiones.

*   **Tarea 4.1: Crear pruebas unitarias para `EntryPointManager`**
    *   **Acción:** Crear el archivo `tests/test_entry_point_manager.py`.
    *   **Propósito:** Probar la lógica del nuevo servicio de forma aislada.
    *   **Casos de prueba a cubrir:**
        1.  **Escenario exitoso:** Existe una clase activa para el día actual y la reserva programada se invoca correctamente.
        2.  **Sin reservas para hoy:** No hay ninguna clase que coincida con el día actual.
        3.  **Clase inactiva:** La clase para el día de hoy está marcada como `activa: false`.
        4.  **Mapeo de parámetros:** Verificar que el cálculo de `fecha_clase` (día de mañana y abreviatura) es correcto.
        5.  **Fallo en la dependencia:** Simular un error en `ScheduledReservationManager` y verificar que se propaga correctamente.

*   **Tarea 4.2: Pruebas de integración**
    *   **Acción:** Ejecutar la aplicación y probar el flujo completo.
    *   **Pasos:**
        1.  Configurar `clases.json` para que haya una reserva para el día actual.
        2.  Iniciar el servidor y verificar en los logs que la tarea de reserva se ejecutó.
        3.  Llamar al nuevo endpoint `POST /reservas/ejecutar-verificacion-diaria` y confirmar que devuelve una respuesta exitosa.
        4.  Modificar `clases.json` para que no haya reserva y repetir los pasos 2 y 3, esperando un comportamiento de "no acción".