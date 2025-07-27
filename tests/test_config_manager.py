import os
import json
import tempfile
from app.services.config_manager import ConfigManager
from datetime import datetime

def test_detectar_clase_para_hoy_sabado():
    # Simula que hoy es sábado 26 de julio de 2025
    data = {
        "clases_por_dia": {
            "sabado": {
                "nombre_clase": "08:00 METCOM 10:00-11:00",
                "fecha_clase": "Sábado",
                "selector": "sa",
                "fecha_reserva": "Sábado",
                "hora_reserva": "09:00:00",
                "activo": True
            }
        }
    }
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        json.dump(data, tmp, ensure_ascii=False)
        tmp.flush()
        config_manager = ConfigManager(config_path=tmp.name)
        resultado = config_manager.detectar_clase_para_hoy(config_path=tmp.name)
        assert resultado is not None
        assert resultado['nombre_clase'] == "08:00 METCOM 10:00-11:00"
        assert resultado['hora_reserva'] == "09:00:00"
        assert resultado['fecha_clase'].startswith("SU ")
        assert resultado['fecha_reserva'] == datetime.now().strftime('%Y-%m-%d')
        assert resultado['timezone'] == 'America/Santiago'
    os.unlink(tmp.name)

def test_detectar_clase_para_hoy_no_activa():
    data = {
        "clases_por_dia": {
            "sabado": {
                "nombre_clase": "08:00 METCOM 10:00-11:00",
                "fecha_clase": "Sábado",
                "selector": "sa",
                "fecha_reserva": "Sábado",
                "hora_reserva": "09:00:00",
                "activo": False
            }
        }
    }
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        json.dump(data, tmp, ensure_ascii=False)
        tmp.flush()
        config_manager = ConfigManager(config_path=tmp.name)
        resultado = config_manager.detectar_clase_para_hoy(config_path=tmp.name)
        assert resultado is None
    os.unlink(tmp.name)
