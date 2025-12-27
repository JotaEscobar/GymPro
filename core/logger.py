# -*- coding: utf-8 -*-
"""
Sistema de logging centralizado
"""
import logging
import sys
from pathlib import Path
from core.config import Config

def setup_logger(name: str = 'GymManager') -> logging.Logger:
    """
    Configura y retorna un logger con handlers de archivo y consola
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    # Nivel de logging desde config
    level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    try:
        file_handler = logging.FileHandler(
            Config.LOG_FILE,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"No se pudo crear el archivo de log: {e}", file=sys.stderr)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Logger global por defecto
logger = setup_logger()
