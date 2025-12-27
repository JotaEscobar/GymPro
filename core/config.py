# -*- coding: utf-8 -*-
"""
Configuración centralizada del sistema GymManager PRO
"""

class Config:
    """Configuración global de la aplicación"""
    
    # Base de datos
    DB_NAME = 'gym_db.sqlite'
    
    # Formatos de fecha
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    DISPLAY_DATE_FORMAT = '%d/%m/%Y'
    
    # Reglas de negocio
    ALERT_DAYS_THRESHOLD = 5  # Días antes de vencer para mostrar alerta
    MAX_CLIENTS = 1000  # Límite inicial del sistema
    
    # Paginación
    DEFAULT_PAGE_SIZE = 50
    
    # Logging
    LOG_FILE = 'gym_manager.log'
    LOG_LEVEL = 'INFO'
    
    # Planes por defecto
    DEFAULT_PLANS = [
        ('Sesión Diaria', 5.00, 1, 1),
        ('Membresía Mensual', 60.00, 30, 1)
    ]
    
    # Estados de membresía
    STATUS_ACTIVE = 'Activo'
    STATUS_EXPIRED = 'Vencido'
    STATUS_NO_PLAN = 'Sin Plan'
    STATUS_UNKNOWN = 'Desconocido'
    
    # Mensajes de respuesta
    MSG_SUCCESS = 'Éxito'
    MSG_ERROR = 'Error'
    MSG_WARNING = 'Advertencia'
