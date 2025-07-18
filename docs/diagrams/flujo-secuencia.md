# Flujo de Reserva - Secuencia Temporal

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant T as Timing Service
    participant R as Reservation Engine
    participant B as Browser Manager
    participant W as BoxMagic Website
    
    Note over S,W: T-25h: Configuración de reserva
    S->>T: Calcular tiempo de reserva
    T-->>S: Tiempo exacto (25h antes)
    S->>S: Programar job
    
    Note over S,W: T-2min: Inicio de preparación
    S->>R: Iniciar proceso de reserva
    R->>B: Preparar browser
    B-->>R: Browser listo
    
    Note over S,W: T-90s: Navegación
    R->>B: Navegar a BoxMagic
    B->>W: GET /bienvenida/entrada
    W-->>B: Página de login
    B->>W: Enviar credenciales
    W-->>B: Dashboard
    
    Note over S,W: T-60s: Preparación de reserva
    B->>W: Navegar a clases
    W-->>B: Lista de clases
    B->>W: Seleccionar día siguiente
    W-->>B: Clases del día
    B->>W: Click en clase objetivo
    W-->>B: Popup de reserva
    
    Note over S,W: T-10s: Espera precisa
    R->>T: Obtener tiempo actual
    T-->>R: Tiempo con compensación NTP
    R->>R: Calcular tiempo restante
    
    Note over S,W: T-0s: EJECUCIÓN
    R->>B: CLICK EN RESERVAR
    B->>W: POST /reservar
    W-->>B: Confirmación
    B-->>R: Resultado
    R-->>S: Éxito/Fallo
```

## Timing Crítico del Proceso

### Fases Temporales

| **Fase** | **Timing** | **Duración** | **Actividad Principal** |
|----------|------------|--------------|-------------------------|
| **Configuración** | T-25h | Instantáneo | Calcular y programar reserva |
| **Preparación** | T-2min | 30s | Inicializar browser y contexto |
| **Navegación** | T-90s | 60s | Login y navegación a clases |
| **Posicionamiento** | T-30s | 20s | Localizar clase y abrir popup |
| **Espera Precisa** | T-10s | 10s | Monitoreo temporal fino |
| **Ejecución** | T-0s | <1s | Click en reservar |
| **Verificación** | T+1s | 5s | Confirmar éxito/fallo |

### Precisión Temporal

- **T-10s a T-1s**: Monitoreo cada 100ms
- **T-1s a T-0s**: Monitoreo cada 10ms  
- **T-0s**: Ejecución inmediata
- **Objetivo**: ±100ms de precisión
- **Aceptable**: ±500ms de precisión
