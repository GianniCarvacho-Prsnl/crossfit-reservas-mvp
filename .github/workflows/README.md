# crossfit-reservas-mvp - Workflows en GitHub Actions

Este directorio contiene los workflows de GitHub Actions que automatizan la operación programada de la aplicación `crossfit-reservas-mvp` desplegada en Fly.io.

---

## Archivos principales

- **main.yml**: Workflow principal que se ejecuta diariamente para realizar la operación de reservas.
- **deploy.yml**: Workflow para desplegar la aplicación en Fly.io.
- **test.yml**: Workflow para ejecutar pruebas automatizadas del proyecto.

---

## Variables de entorno

Para que los workflows funcionen correctamente, es necesario configurar las siguientes variables de entorno en los secretos del repositorio:

- `FLY_API_TOKEN`: Token de autenticación para Fly.io.
- `DATABASE_URL`: URL de conexión a la base de datos.
- `RESERVAS_API_KEY`: API key para la integración con el sistema de reservas.

---

## Horarios de ejecución

- El workflow `main.yml` está configurado para ejecutarse todos los días a las 06:00 AM UTC.
- Otros workflows se activan bajo demanda o en eventos específicos como push o pull request.

---

## ¿Qué hace cada workflow?

### main.yml

- Conecta con la base de datos para obtener las reservas del día siguiente.
- Envía notificaciones a los usuarios con sus reservas confirmadas.
- Actualiza el estado de las reservas en la base de datos.

### deploy.yml

- Construye la imagen Docker de la aplicación.
- Despliega la imagen en Fly.io usando el token configurado.

### test.yml

- Ejecuta las pruebas unitarias y de integración.
- Reporta el resultado en GitHub Actions.

---

## Operación diaria

Cada día a las 06:00 AM UTC, el workflow `main.yml` realiza:

1. Consulta de reservas para el día siguiente.
2. Envío de correos electrónicos de confirmación a los usuarios.
3. Registro de la operación en logs para auditoría.

---

## Comandos útiles

- Para ejecutar localmente los scripts de reserva:

  ```bash
  node scripts/reservas.js
  ```

- Para desplegar manualmente:

  ```bash
  fly deploy
  ```

- Para ver logs en Fly.io:

  ```bash
  fly logs
  ```

---

## Pruebas

Ejecutar pruebas con:

```bash
npm test
```

o mediante el workflow `test.yml` en GitHub Actions.

---

## Problemas comunes

- **Error de autenticación Fly.io**: Verificar que el token `FLY_API_TOKEN` esté correctamente configurado.
- **Fallos en la conexión a la base de datos**: Revisar la variable `DATABASE_URL` y la disponibilidad de la base de datos.
- **Errores en envío de notificaciones**: Comprobar la validez del `RESERVAS_API_KEY`.

---

## Cambios de ventana

Si se requiere modificar la hora de ejecución diaria, editar el cron en el archivo `main.yml`:

```yaml
on:
  schedule:
    - cron: '0 6 * * *' # Cambiar a la hora deseada en UTC
```

---

## Deshabilitar temporalmente

Para deshabilitar un workflow temporalmente, se puede comentar la sección `on:` en el archivo YAML o renombrar la extensión del archivo a `.yml.disabled`.

---

Este README se actualizará conforme se realicen cambios en los workflows o en la operación del sistema.

# crossfit-reservas-mvp – Automatización en GitHub Actions

Este directorio contiene los workflows de GitHub Actions que controlan el encendido y apagado programado de la aplicación `crossfit-reservas-mvp` desplegada en Fly.io, así como un ping periódico para mantenerla activa durante la ventana horaria definida.

---

## Archivos

- **windows.yml** → Enciende la máquina a las 17:00 CL y la apaga a las 20:00 CL.  
  - También puede ejecutarse manualmente para forzar START/STOP según la hora actual.
- **ping.yml** → Envía una solicitud HTTP cada 2 minutos entre 17:00–20:00 CL para evitar que Fly.io la detenga por inactividad.

---

## Variables necesarias (Secrets en GitHub)

- `FLY_API_TOKEN`: Token de autenticación para Fly.io (con permisos para gestionar máquinas).

---

## Horarios

- **Ventana de operación:** 17:00 a 20:00 (hora de Santiago, Chile).  
- Fuera de esta ventana, `windows.yml` apaga la máquina y `ping.yml` no actúa.

---

## Qué hace cada workflow

### `windows.yml`
1. Consulta la hora local (America/Santiago).
2. Lista las máquinas activas del app.
3. Si está dentro del horario → envía `start`.
4. Si está fuera del horario → envía `stop`.

### `ping.yml`
1. Verifica que esté dentro del horario.
2. Hace `curl` a `https://crossfit-reservas-mvp.fly.dev/` cada 2 min para mantener la máquina activa.

---

## Operación diaria

1. **17:00** → `windows.yml` enciende la máquina.
2. **17:00–20:00** → `ping.yml` mantiene la app despierta.
3. **20:00** → `windows.yml` apaga la máquina.
4. Fuera de este horario, la máquina permanece detenida.

---

## Comandos útiles

Ver estado de máquinas:
```bash
fly machines list -a crossfit-reservas-mvp
```

Encender manualmente:
```bash
fly machines start <machine_id> -a crossfit-reservas-mvp
```

Apagar manualmente:
```bash
fly machines stop <machine_id> -a crossfit-reservas-mvp
```

---

## Pruebas

- Para probar apagado: ejecutar `windows.yml` manualmente fuera de la ventana.
- Para probar encendido: ejecutar `windows.yml` manualmente dentro de la ventana.
- Para probar ping: ejecutar `ping.yml` manualmente dentro de la ventana.

---

## Problemas comunes

- **No arranca** → revisar `auto_start_machines` en `fly.toml` (debe estar en `true` si usas ping para encender).
- **No se apaga** → confirmar que la hora en el Action corresponde a CL (UTC-4/UTC-3 según horario).
- **Ping no mantiene activa** → la app debe responder rápido a `/` o `/health`.

---

## Cambiar ventana horaria

Editar los valores de hora en los scripts dentro de cada workflow (`1500`/`2000` → `1700`/`2000`, etc.) y ajustar cron si es necesario.

---

## Deshabilitar temporalmente

En la pestaña **Actions** de GitHub:
- Abrir el workflow → **⋯** → **Disable workflow**.
- O renombrar el archivo `.yml` a `.yml.disabled`.

---