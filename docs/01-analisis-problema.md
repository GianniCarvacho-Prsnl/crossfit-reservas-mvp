# Análisis del Problema y Requerimientos

## 1. Entendimiento del Problema

### Problema Central
El usuario necesita reservar clases de CrossFit con cupos limitados que se agotan en segundos. Las clases requieren una reserva exacta en el momento que se aperturan (25 horas antes del inicio de la clase).

### Condiciones Críticas
- **Timing Exacto**: Las reservas deben realizarse en el segundo exacto de apertura (25 horas antes del inicio)
- **Cupos Limitados**: Los cupos se agotan en pocos segundos
- **Automatización Requerida**: Es imposible hacer la reserva manualmente con la precisión necesaria
- **Zona Horaria**: Santiago de Chile (UTC-3/UTC-4 según DST)

### Ejemplo de Timing
```
Clase: Martes 19:00
Apertura de reserva: Lunes 18:00:00 (exacto)
Ventana de oportunidad: ~1-5 segundos antes de agotarse
```

## 2. Contexto del Negocio

### Plataforma Objetivo
- **Sitio Web**: BoxMagic (https://go.boxmagic.app)
- **Tipo**: Sistema de reservas de gimnasio/CrossFit
- **Comportamiento**: Sistema de reservas por cupos limitados

### Credenciales de Acceso
```
URL: https://go.boxmagic.app/bienvenida/entrada?modo=ingreso
EMAIL: gtcarvacho@gmail.com
PASSWORD: Fitoko2024
```

## 3. Requerimientos Funcionales

### RF001 - Programación de Reservas
- El sistema debe leer la configuración de clases a reservar
- Debe calcular automáticamente cuándo hacer cada reserva (25 horas antes)
- Debe mantener un scheduler activo 24/7

### RF002 - Automatización Web
- Debe iniciar sesión automáticamente en la plataforma
- Debe navegar hasta la sección de clases
- Debe seleccionar el día correcto (siempre día siguiente)
- Debe localizar y seleccionar la clase específica
- Debe ejecutar la reserva en el timing exacto

### RF003 - Gestión de Timing Crítico
- Debe iniciar navegación 1-2 minutos antes del momento exacto
- Debe preparar todos los elementos (login, navegación, popup)
- Debe ejecutar el click de reserva en el segundo exacto
- Debe manejar la zona horaria de Santiago correctamente

### RF004 - Configuración Flexible
- Debe permitir configurar diferentes clases por día de la semana
- Debe soportar diferentes horarios por clase
- Debe permitir activar/desactivar días específicos

## 4. Requerimientos No Funcionales

### RNF001 - Precisión Temporal
- Precisión de ejecución: ±1 segundo máximo
- Sincronización con servidor de tiempo confiable
- Compensación de latencias de red y procesamiento

### RNF002 - Confiabilidad
- Disponibilidad: 99.9% (crítico para no perder reservas)
- Manejo robusto de errores de red y timeouts
- Logs detallados para troubleshooting

### RNF003 - Rendimiento
- Tiempo de login y navegación: <30 segundos
- Tiempo de preparación de reserva: <45 segundos
- Respuesta del click de reserva: <100ms

### RNF004 - Portabilidad
- Debe ejecutarse en contenedor Docker
- Compatible con plataformas cloud (fly.io, etc.)
- Independiente del sistema operativo host

## 5. Restricciones y Consideraciones

### Restricciones Técnicas
- Debe usar Python como lenguaje principal
- Debe usar Playwright para automatización web
- Debe usar FastAPI para servicios web
- Debe funcionar de forma autónoma sin intervención manual

### Consideraciones de Diseño
- **Aplicación Personal**: No requiere logs empresariales complejos
- **Simplicidad**: Priorizar funcionamiento sobre robustez inicial
- **Escalabilidad Futura**: Diseño que permita mejoras posteriores

### Riesgos Identificados
1. **Cambios en la UI del sitio web**: Elementos pueden cambiar
2. **Latencia de red**: Puede afectar timing crítico
3. **Bloqueos por automatización**: Sitio puede detectar bots
4. **Fallas de infraestructura**: Servidor/internet down en momento crítico

## 6. Casos de Uso Principales

### CU001 - Configurar Horario de Clases
**Actor**: Usuario
**Descripción**: Configurar qué clases reservar cada día de la semana

### CU002 - Ejecutar Reserva Automática
**Actor**: Sistema Scheduler
**Descripción**: Ejecutar proceso completo de reserva en timing exacto

### CU003 - Monitorear Estado del Sistema
**Actor**: Usuario
**Descripción**: Verificar que el sistema esté funcionando correctamente

### CU004 - Gestionar Errores de Reserva
**Actor**: Sistema
**Descripción**: Manejar fallos en el proceso de reserva y notificar

## 7. Criterios de Éxito

### Criterios Primarios
- ✅ Ejecutar reserva en el segundo exacto (±1s)
- ✅ Tasa de éxito de reserva: >95%
- ✅ Funcionamiento autónomo sin intervención manual

### Criterios Secundarios
- ✅ Logs claros para troubleshooting
- ✅ Configuración simple y flexible
- ✅ Deploy automatizado en cloud

## 8. Fuera del Alcance (v1.0)

- Sistema de notificaciones avanzado
- Interface web para configuración
- Múltiples usuarios/cuentas
- Análisis estadístico de reservas
- Integración con calendarios externos
