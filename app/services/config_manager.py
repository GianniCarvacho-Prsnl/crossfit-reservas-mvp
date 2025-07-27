import json
import os
from typing import List, Optional
from loguru import logger
from app.models import ClaseConfig
import unicodedata
from datetime import datetime, timedelta


class ConfigManager:
    def __init__(self, config_path: str = "config/clases.json"):
        self.config_path = config_path
        self._clases_cache = None
    
    def load_clases(self) -> List[ClaseConfig]:
        """Carga las clases desde el archivo JSON"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Archivo de configuración no encontrado: {self.config_path}")
                return []
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                clases = [ClaseConfig(**clase) for clase in data.get('clases', [])]
                logger.info(f"Cargadas {len(clases)} clases desde configuración")
                return clases
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return []
    
    def get_clase_by_id(self, clase_id: str) -> Optional[ClaseConfig]:
        """Obtiene una clase específica por ID"""
        clases = self.load_clases()
        for clase in clases:
            if clase.id == clase_id and clase.activo:
                return clase
        return None
    
    def get_clases_activas(self) -> List[ClaseConfig]:
        """Obtiene todas las clases activas"""
        clases = self.load_clases()
        return [clase for clase in clases if clase.activo]
    
    def get_clase_by_nombre(self, nombre_clase: str) -> Optional[ClaseConfig]:
        """
        Obtiene una clase específica por nombre exacto
        
        Args:
            nombre_clase: Nombre exacto de la clase
            
        Returns:
            ClaseConfig si se encuentra, None si no existe o está inactiva
        """
        clases = self.load_clases()
        for clase in clases:
            if clase.nombre == nombre_clase and clase.activo:
                return clase
        return None
    
    def detectar_clase_para_hoy(self, config_path: str = "config/clases.json"):
        """
        Detecta si hay una clase activa para el día de hoy según el archivo de configuración.
        Devuelve un diccionario con los parámetros de reserva si corresponde, o None si no hay clase activa.
        """
        def normalizar(texto):
            return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').lower()

        dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        dias_es_sin_tilde = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        hoy = datetime.now()
        dia_hoy = hoy.strftime('%A').lower()  # Ej: 'saturday'
        # Mapeo de inglés a español sin tilde
        map_en_es = {
            'monday': 'lunes',
            'tuesday': 'martes',
            'wednesday': 'miércoles',
            'thursday': 'jueves',
            'friday': 'viernes',
            'saturday': 'sábado',
            'sunday': 'domingo',
        }
        dia_hoy_es = map_en_es.get(dia_hoy, dia_hoy)
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            clases = data.get('clases_por_dia', {})
            for key, clase in clases.items():
                if not clase.get('activo', False):
                    continue
                fecha_reserva = clase.get('fecha_reserva', '')
                if normalizar(fecha_reserva) == normalizar(dia_hoy_es):
                    # Preparar parámetros para reserva
                    nombre_clase = clase.get('nombre_clase')
                    hora_reserva = clase.get('hora_reserva')
                    # Mapeo de días español a inglés (2 letras)
                    tabla_mapeo = {
                        'lunes': 'MO', 'martes': 'TU', 'miércoles': 'WE', 'miercoles': 'WE',
                        'jueves': 'TH', 'viernes': 'FR', 'sábado': 'SA', 'sabado': 'SA', 'domingo': 'SU'
                    }
                    manana = hoy + timedelta(days=1)
                    dia_manan_es = manana.strftime('%A').lower()
                    dia_manan_es = map_en_es.get(dia_manan_es, dia_manan_es)
                    prefijo = tabla_mapeo.get(dia_manan_es, dia_manan_es[:2].upper())
                    fecha_clase = f"{prefijo} {manana.day}"
                    fecha_reserva_str = hoy.strftime('%Y-%m-%d')
                    return {
                        'nombre_clase': nombre_clase,
                        'fecha_clase': fecha_clase,
                        'fecha_reserva': fecha_reserva_str,
                        'hora_reserva': hora_reserva,
                        'timezone': 'America/Santiago'
                    }
        return None

# NOTA IMPORTANTE:
# El parámetro 'fecha_clase' que se envía al endpoint se construye SIEMPRE como el día siguiente a la fecha de reserva (hoy + 1),
# usando el mapeo de días y el número de día de mañana. El valor 'fecha_clase' del JSON es solo informativo y NO se utiliza para el endpoint.
