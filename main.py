# -*- coding: utf-8 -*-
"""
Punto de entrada principal de GymManager PRO
"""
import sys
from PyQt6.QtWidgets import QApplication
from core.database_manager import create_initial_tables
from core.logger import logger
from ui.main_window import MainWindow
from ui.styles import ESTILO_OSCURO

def main():
    """Función principal de inicio"""
    logger.info("="*50)
    logger.info("Iniciando GymManager PRO")
    logger.info("="*50)
    
    # Crear/actualizar base de datos
    try:
        create_initial_tables()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        sys.exit(1)

    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO_OSCURO)
    
    # Crear y mostrar ventana principal
    ventana = MainWindow()
    ventana.show()
    
    logger.info("Aplicación iniciada correctamente")
    
    # Ejecutar loop de eventos
    exit_code = app.exec()
    
    logger.info(f"Aplicación cerrada con código: {exit_code}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
