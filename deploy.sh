#!/bin/bash

# Script de despliegue para CrossFit Reservas MVP
set -e

echo "🚀 Iniciando despliegue de CrossFit Reservas MVP..."

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env"
    echo "📝 Crea un archivo .env con las siguientes variables:"
    echo "CROSSFIT_URL=tu_url_del_sitio"
    echo "USERNAME=tu_usuario"
    echo "PASSWORD=tu_contraseña"
    echo "BROWSER_HEADLESS=true"
    echo "LOG_LEVEL=INFO"
    exit 1
fi

# Función para limpiar contenedores y volúmenes
cleanup() {
    echo "🧹 Limpiando contenedores y volúmenes anteriores..."
    docker-compose down -v 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
}

# Función para construir la imagen
build() {
    echo "🔨 Construyendo imagen Docker..."
    docker-compose build --no-cache
}

# Función para iniciar los servicios
start() {
    echo "🚀 Iniciando servicios..."
    docker-compose up -d
    
    echo "⏳ Esperando que el servicio esté listo..."
    sleep 10
    
    # Verificar que el servicio esté funcionando
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null; then
            echo "✅ Servicio iniciado correctamente!"
            echo "📋 API disponible en: http://localhost:8001"
            echo "📖 Documentación en: http://localhost:8001/docs"
            return 0
        fi
        echo "⏳ Esperando... (intento $i/30)"
        sleep 2
    done
    
    echo "❌ Error: El servicio no responde después de 60 segundos"
    echo "📋 Verificando logs..."
    docker-compose logs crossfit-reservas
    exit 1
}

# Función para mostrar logs
logs() {
    echo "📋 Mostrando logs del servicio..."
    docker-compose logs -f crossfit-reservas
}

# Función para parar los servicios
stop() {
    echo "🛑 Deteniendo servicios..."
    docker-compose down
}

# Función para mostrar el estado
status() {
    echo "📊 Estado de los servicios:"
    docker-compose ps
    
    echo ""
    echo "🏥 Health check:"
    curl -s http://localhost:8001/health | python -m json.tool 2>/dev/null || echo "Servicio no disponible"
}

# Función para hacer una prueba de reserva
test() {
    echo "🧪 Ejecutando prueba de reserva..."
    curl -X POST "http://localhost:8001/api/reservas" \
         -H "Content-Type: application/json" \
         -d '{
           "fecha": "2025-01-20",
           "hora": "18:00",
           "clase": "CrossFit"
         }' | python -m json.tool
}

# Menú principal
case "$1" in
    "clean")
        cleanup
        ;;
    "build")
        build
        ;;
    "start")
        cleanup
        build
        start
        ;;
    "logs")
        logs
        ;;
    "stop")
        stop
        ;;
    "restart")
        stop
        sleep 2
        start
        ;;
    "status")
        status
        ;;
    "test")
        test
        ;;
    *)
        echo "🐳 CrossFit Reservas MVP - Script de Despliegue"
        echo ""
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandos disponibles:"
        echo "  start    - Limpiar, construir e iniciar los servicios"
        echo "  build    - Construir la imagen Docker"
        echo "  clean    - Limpiar contenedores y volúmenes"
        echo "  logs     - Mostrar logs en tiempo real"
        echo "  stop     - Detener los servicios"
        echo "  restart  - Reiniciar los servicios"
        echo "  status   - Mostrar estado de los servicios"
        echo "  test     - Ejecutar una prueba de reserva"
        echo ""
        echo "Ejemplos:"
        echo "  $0 start     # Despliegue completo"
        echo "  $0 logs      # Ver logs"
        echo "  $0 status    # Ver estado"
        echo "  $0 test      # Probar API"
        ;;
esac
