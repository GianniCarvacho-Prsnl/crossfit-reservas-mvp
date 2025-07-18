import json
import os
from typing import List, Optional
from loguru import logger
from app.models import ClaseConfig


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
