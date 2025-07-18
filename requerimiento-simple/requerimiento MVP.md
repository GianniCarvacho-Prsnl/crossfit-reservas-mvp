# Requerimiento MVP

## Contexto

Este es un proyecto personal y no profesional. La prioridad es crear una versión simple y funcional, para luego agregar nuevas funcionalidades.

## Objetivos

- Desarrollar una aplicación que realice reservas en un sitio web de clases de crossfit.
- Utilizar **Python** y **FastAPI** para el backend.
- Implementar la navegación de la página con el **MCP de Playwright**.
- Las clases a reservar cada día estarán definidas en un archivo `clases.json`.

## Necesidad

Las clases que deseo reservar tienen cupos limitados y se agotan en segundos. Por eso, la reserva debe realizarse exactamente en el momento en que se habilitan las clases.

## Lógica de Reserva de Clases

La opcion para reservar las clases se abre 25 horas exactas antes que comience la clase.

Ejemplo1: El día Jueves hay una clase publicada que se llama '17:00 CrossFit 17:00-18:00' y esta clase comienza a las 17:00
por lo tanto la reserva se debe hacer exactamente a las 16:00 del día miercoles.

Ejemplo2: Hay otra clase para el Jueves que se llama 'Competitor 18:00-19:00' que comienza a las 18:00 por lo tanto la reserva se debe hacer a las 18:00 del miercoles.

Imagen: En la imagen requerimiento/requerimiento-simple/clases.png puedes ver un screenshot de las clases.

Como puedes ver el nombre de la clase tiene la hora en el mismo texto, pero prefiero que manejemos los valores por separado en el json, por ejemplo el json de las clases debería tener esta informacion como minimo:
    -Nombre clase : Competitor 18:00-19:00
    -Hora Reserva : 18:00


Navegacion:
    Quiero que hagamos la navegacion la hagamos con el MCP-


    Credenciales:
        CROSSFIT_URL=https://go.boxmagic.app/bienvenida/entrada?modo=ingreso
        USERNAME=gtcarvacho@gmail.com
        PASSWORD=Fitoko2024

    El flujo tiene principalmente:
        1.- Login
        2.- Seleccionar opcion 'Clases'
        3.- Seleccionar día: Este punto es importante ya que siempre querremos seleccionar el día de mañana ya que la reserva es 25 horas antes. Esto se hace en un selector de días que puedes ver en la imagen (/Users/gianni/Desktop/2025/DevProyectos/PLAYWRIGHT/vscode-reserva/requerimiento-simple/image.png). Siempre se muestran 2 días (hoy y mañana), siempre seleccionaremos el segundo boton.
        4.- Seleccionar la clase : A partir del texto del nombre de la clase que obtenemos del json.
        5.- presionar el boton reservar.



**IMPORTANTE 1: Como este es un MVP primero haremos que cada vez que iniciemos la sesion, sabremos que clases debe reservar desde el json y generar el flujo... independiente de las 25 horas antes**

**IMPORTANTE2: Una vez que funcione el paso anterior deberemos implementar que cuando la aplicacion inicie obtenga la clase que debe reservar y calcule exctamente cuanto tiempo falta para que comience con el flujo en la web para hacer la reserva, el flujo debería comenzar 2 minutos antes de la reserva, para que en el segundo exacto presione el boton reservar.**

ARQUITECTURA:
    PREGUNTA IMPORTANTE: Crees que será buena idea crear un endpoint que reciba, el nombre de la clase, hora de reserva para que este comience el flujo y haga la reserva?. En el futuro podemos hacer otro endpoint que haga la espera a la hora exacta, pero como primer MVP quizás podemos hacerlo simple y que trate de reservar al instante.
