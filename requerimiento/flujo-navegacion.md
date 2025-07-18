
Objetivo: Crear aplicacion en python para automatizar la reserva de clases en sitio web.



Flujo aplicacion:


1.- Inicio sesion:

    Se debe abrir sitio web e iniciar sesion con los siguientes datos:

    # Configuración del sitio web de crossfit
    CROSSFIT_URL=https://go.boxmagic.app/bienvenida/entrada?modo=ingreso
    USERNAME=gtcarvacho@gmail.com
    PASSWORD=Fitoko2024

    ** Imagen de referencia en : /Users/gianni/Desktop/2025/DevProyectos/PLAYWRIGHT/reserva-clases-boxmagic/requerimiento/Imagen1_inicio.png

2.- Ingresar a seccion 'Clases':

    En las opciones de la izquierda existe un boton que tiene como texto 'Clases'

    Elemento referencia :   <div data-v-32448cd4="" class="texto">Clases</div>
    Full Path           :   /html/body/div[1]/div/div/div/div[2]/div[3]/div[2]/a[3]/div[2]


3.- Seleccionar día:

    -Se debe seleccionar el día que se quiere reservar la clase.
    -Se debe considerar que siempre se reservará clases para el día siguiente, por ejemplo, si hoy es Domingo, siempre se debe seleccionar el día Lunes.. si es Lunes, siempre se querrá reservar una clase del día Martes.
    -En la zona superior, donde se marca en la imagen de referencia, siempre aparecerán dos días, el día de hoy y el de mañana de la siguiente manera:
        Lunes   = LU + espacio + día del mes
        Martes  = MA + espacio + día del mes
        Miercoles = MI + espacio + día del mes
        Jueves = JU + espacio + día del mes
        Viernes = VI + espacio + día del mes
        Sabado = SA + espacio + día del mes
        Domingo = DO + espacio + día del mes

        ** Por ejemplo, hoy es Domingo 13 y los botones muestran 'DO 13' y el segundo boton muestra 'LU 14'.

    - Recuerda que siempre querremos reservar el día de mañana:
        Elemento : <span data-v-4a63fb7f="" class="diaNumero"><span data-v-4a63fb7f="" class="diaSemana mr-xs"> lu</span><span data-v-4a63fb7f="">14</span></span>
        Full Path: /html/body/div/div/div/div/div[2]/div[2]/div/header[1]/div/div/div/div/span/div[2]/span

        Imagen Referencia: /Users/gianni/Desktop/2025/DevProyectos/PLAYWRIGHT/reserva-clases-boxmagic/requerimiento/Imagen2_dia.png


4.- Buscar clase:

    Luego de seleccionar el día, se debe buscar la clase que se quiere reservar. 

    Clase de ejemplo: <p data-v-64a261dd="" class="mb-0 text-lg text-capitalize">Competitor 19:00-20:00</p>

5.- Al presionar sobre la clase seleccionada se debe presionar el boton 'Reservar' del popup

    Elemento :  <span data-v-8ac6a486="">Reservar</span>


