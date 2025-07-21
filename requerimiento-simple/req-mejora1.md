# Nuevo Endpoint de Reserva

## Descripción

Se requiere crear un nuevo endpoint para realizar reservas de clases, con mayor complejidad que el endpoint existente `/api/reservas/inmediata`.

## Problema a Solucionar

El objetivo de este proyecto es que la reserva se realice de forma **automática** en el momento exacto (25 horas antes del inicio de la clase), ya que los cupos se agotan en segundos debido a la alta demanda.

## Objetivo

El nuevo endpoint debe generar la reserva (presionando el botón "Reservar" o "Book") en el **segundo exacto** en que la clase se habilita oficialmente, es decir, 25 horas antes de que comience.

> **Importante:**  
> La secuencia para hacer una reserva es la misma que ya existe en `/api/reservas/inmediata`.

### Ejemplo

- Clase: `18:00 CrossFit 18:00-19:00`
- Inicio de la clase: Lunes a las 18:00 horas
- La reserva se puede realizar exactamente a las **17:00** del día anterior (Domingo).

## Solución Propuesta

Para realizar la reserva a una hora exacta, el endpoint debe recibir como parámetro la hora en que debe presionarse el botón de reserva.  
Por ejemplo, para la clase anterior (`18:00 CrossFit 18:00-19:00`), el nuevo parámetro sería:

```json
{
    "hora_reserva": "17:00"
}
```

Además, será necesario implementar un ciclo de espera para que la reserva se realice en el momento exacto.

### Consideraciones

- En el futuro, se desarrollará un módulo inteligente que activará este endpoint automáticamente, probablemente mediante un cron(inicialmente lo haré manual). La idea es que, por ejemplo, cuando falte 1 hora para la hora de la reserva, se active este nuevo endpoint. Como aún faltarán varios minutos para el momento exacto de la reserva, el endpoint deberá mantener un ciclo de espera.
- Al ejecutar la llamada a este servicio, se recibirá la hora exacta en la que se debe presionar el botón de reserva o book. Con esta información y la hora actual, se calculará el tiempo restante.
- El flujo navegacion en la web de la reserva debe comenzar **1 minuto antes** de la hora exacta de la hora de reserva recibida. Es decir, si la reserva debe realizarse a las 17:00, a las 16:59 debe iniciarse la navegación y llegar hasta el paso previo a presionar el botón "Reservar" o "Book". Justo a las 17:00:00 se debe ejecutar la reserva.

### Ejemplo de ciclo completo

- Clase: `18:00 CrossFit 18:00-19:00`
- Inicio de la clase: Lunes a las 18:00 horas
- La reserva se puede realizar exactamente a las **17:00** del día anterior (Domingo).
- Inicio flujo de nevegacion 16:59 (Llegar al momento donde se debe presionar el boton de reserva y esperar a la hora exacta).
- A partir de este momento, se debe monitorear cada 1 segundo y validar si es la hora exacta. (A menos que exista una forma mas simple de hacer lo mismo).

Ejemplo:
  1. El domingo a las 16:00 se realiza la llamada al servicio.
  2. El servicio calcula los minutos restantes hasta la hora de reserva (**17:00**). O tambien puede calcular hasta el inicio de la navegacion que es la hora de reserva menos 1 minuto.
  3. Como faltan aproximadamente 60 minutos, el ciclo de espera se ejecuta cada varios minutos.
  4. Cuando falten 3 minutos para la hora de reserva, el ciclo se vuelve más frecuente (por ejemplo, cada 30 segundos) a definir, no lo tengo claro.
  5. A las 16:59 se inicia el flujo de navegación (login, selección de clase, etc.) y se llega hasta el paso previo a presionar el botón.
  6. A las **17:00:00** exactas se presiona el botón de reserva.


