# Especificaciones del Sistema de Reserva Automática de Clases

## Requerimiento Principal

El motivo por el que estoy desarrollando esta aplicación es porque las clases que deseo reservar tienen cupos limitados y estos se acaban en pocos segundos, entonces necesito que la reserva se haga en el segundo exacto. Las clases se aperturan 25 horas antes de la hora de inicio de la misma.

## Condiciones de la Reserva de Clases

- **Condición universal**: Todas las clases tienen la misma condición de apertura para poder realizar la reserva.
- **Tiempo de apertura**: Las clases se aperturan **25 horas antes** de que inicie.
  - **Ejemplo**: Si la clase inicia el día Martes a las 19:00, entonces la clase se puede reservar desde el Lunes a las 18:00 en punto.
- **Precisión temporal crítica**: La reserva se debe realizar en el **segundo exacto** que se apertura la clase.
  - En el ejemplo anterior, se debe realizar el Lunes a las 18:00:00 en punto.
  - **Razón**: De lo contrario, la clase se queda sin cupos disponibles.

## Arquitectura Propuesta

Tengo una idea de como puede ser la arquitectura, estoy dispuesto a que busquemos la mejor alternativa pero a la vez simple.

### Componentes del Sistema

La aplicación debería tener **dos partes principales**:

#### 1. Scheduler (Programador de Tareas)
- **Función**: Consultar qué clases debe tomar y cuánto tiempo falta para la reserva
- **Configuración**: Las clases a reservar podrían ser definidas en `requerimiento/clases.json`
  - Indica el día que es la clase
  - Hora que comienza
  - Si es necesario, se podría agregar la hora que se debe hacer la reserva (o calcular automáticamente) o cualquier otro dato, esto es solo un ejemplo.

#### 2. Navegador Web Automatizado (Gatillado por Scheduler)
- **Función**: Generar el login, la navegación y la reserva en el sitio web
- **Consideración crítica de timing**:
  - Desde que inicia la navegación hasta llegar al botón de reserva pueden pasar varios segundos
  - **Estrategia propuesta**: La navegación podría iniciar **1 minuto antes** de la hora exacta de reserva (A pesar de que Scheduler invoque este servicio antes del miunuto)
  - **Flujo sugerido**:
    1. Iniciar sesión
    2. Loguearse
    3. Navegar y encontrar la clase
    4. Tener el popup abierto para realizar la reserva
    5. **Esperar el segundo exacto** para presionar el botón

    ***Importante: Para los horarios debes considerar SIEMPRE que la zona horaria es la de Santiago de Chile**


#### 3. Flujo del Sistema

El paso a paso de como se debe realizar el flujo está detallado en el archivo: `requerimiento/flujo-navegacion.md`

**Flujo propuesto:**

1. **Proceso Scheduler en ejecución continua**
   - Se ejecuta cada x tiempo
   - Lee desde un endpoint o las clases que debe reservar próximamente
   - Calcula cuánto tiempo falta para la reserva exacta (25 horas antes del inicio de la clase)

2. **Identificación y espera de clases próximas**
   - Al tener identificada la o las clases próximas del día que debe reservar
   - Se mantiene a la espera (por ejemplo, 2 minutos antes de la reserva)
   - Gatilla el endpoint del proceso 'Navegador Web Automatizado'

3. **Inicio del Navegador Web Automatizado**
   - Al ser iniciado, sabe que debe esperar 1 minuto antes de la reserva exacta
   - Utiliza este tiempo para:
     - Iniciar sesión
     - Encontrar la clase
     - Preparar el popup de reserva

4. **Monitoreo y ejecución de reserva**
   - Monitorea cada segundo si es la hora exacta
   - Presiona el botón de reservar en el momento preciso

> **Nota**: Si crees que se puede hacer más simple y eficiente, me comentas el plan y lo discutimos

## Requisitos Técnicos y Deploy

### Stack Tecnológico
- **Python**: Lenguaje principal
- **Playwright**: Para automatización web
- **FastAPI**: Para la API y servicios

### Infraestructura
- **Funcionamiento autónomo**: La aplicación debe funcionar de forma autónoma en un servidor
- **Contenedorización**: Implementar en un contenedor Docker
- **Plataforma sugerida**: Servidor como fly.io u otros similares
