# -*- coding: utf-8 -*-
"""
Ventana principal con pestañas
"""
import os
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from ui.members_view import MembersView
from ui.attendance_view import AttendanceView
from ui.plans_view import PlansView
from ui.market_view import MarketView
from ui.caja_view import CajaView

class DashboardView(QWidget):
    """Vista de inicio/dashboard"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        texto = QLabel("¡Bienvenido al Panel Principal de GymManager PRO!")
        texto.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(texto)

        sub_texto = QLabel("Sistema listo para operar. Usa las pestañas para gestionar el gimnasio.")
        layout.addWidget(sub_texto)
        layout.addStretch()

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GymManager PRO | Sistema de Gestión")
        self.setGeometry(100, 100, 1200, 700)
        
        # ========== CONFIGURAR ÍCONO ==========
        self._set_window_icon()
        # ======================================

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self._setup_tabs()

    def _set_window_icon(self):
        """
        Configura el ícono de la ventana.
        Busca el archivo de ícono en el directorio actual.
        
        Formatos soportados: .png, .ico, .jpg, .jpeg, .svg
        Nombres de archivo a buscar (en orden de prioridad):
        1. icon.png / icon.ico
        2. logo.png / logo.ico
        3. gym_icon.png / gym_icon.ico
        4. Cualquier archivo que contenga 'icon' o 'logo'
        """
        # Lista de nombres posibles para el ícono
        possible_names = [
            'icon.png', 'icon.ico',
            'logo.png', 'logo.ico',
            'gym_icon.png', 'gym_icon.ico',
            'app_icon.png', 'app_icon.ico',
            'gymmanager.png', 'gymmanager.ico'
        ]
        
        # Directorio actual (donde está el script)
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Buscar el archivo de ícono
        icon_path = None
        
        # Primero buscar en la lista de nombres posibles
        for name in possible_names:
            test_path = os.path.join(current_dir, name)
            if os.path.exists(test_path):
                icon_path = test_path
                break
        
        # Si no encontró, buscar cualquier archivo que contenga 'icon' o 'logo'
        if not icon_path:
            try:
                for file in os.listdir(current_dir):
                    if file.lower().endswith(('.png', '.ico', '.jpg', '.jpeg', '.svg')):
                        if 'icon' in file.lower() or 'logo' in file.lower():
                            icon_path = os.path.join(current_dir, file)
                            break
            except Exception as e:
                print(f"No se pudo buscar ícono: {e}")
        
        # Aplicar el ícono si se encontró
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                self.setWindowIcon(icon)
                print(f"✅ Ícono cargado: {os.path.basename(icon_path)}")
            except Exception as e:
                print(f"⚠️ Error al cargar ícono: {e}")
        else:
            print("⚠️ No se encontró archivo de ícono en el directorio principal")
            print(f"   Directorio buscado: {current_dir}")
            print(f"   Nombres buscados: {', '.join(possible_names[:5])}")

    def _setup_tabs(self):
        """Configura todas las pestañas en el orden correcto"""
        # 1. Dashboard
        self.tab_dashboard = DashboardView()
        self.tab_widget.addTab(self.tab_dashboard, "🏠 Inicio")

        # 2. Gestión de Miembros (PRIMERO)
        self.tab_members = MembersView()
        self.tab_widget.addTab(self.tab_members, "👥 Gestión de Miembros")

        # 3. Check-in / Asistencias (SEGUNDO)
        self.tab_attendance = AttendanceView()
        self.tab_widget.addTab(self.tab_attendance, "🏃 Check-in / Asistencia")
        
        # 🔥 ENLAZAR DESPUÉS DE CREAR AMBAS
        self.tab_members.attendance_view = self.tab_attendance

        # 4. Planes
        self.tab_plans = PlansView()
        self.tab_widget.addTab(self.tab_plans, "💰 Planes y Tarifas")
        
        # 5. Market
        self.tab_market = MarketView()
        self.tab_widget.addTab(self.tab_market, "🛒 Market")
        
        # 6. Caja
        self.tab_caja = CajaView()
        self.tab_widget.addTab(self.tab_caja, "💰 Caja")
