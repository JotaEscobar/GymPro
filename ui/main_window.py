# -*- coding: utf-8 -*-
"""
Ventana principal con pestañas
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QLabel, QVBoxLayout, QWidget
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

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self._setup_tabs()

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
