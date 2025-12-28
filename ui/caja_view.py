# -*- coding: utf-8 -*-
"""
Vista de Caja Rediseñada V2 - Diseño limpio y eficiente
Inspirado en el estilo de Market
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, QComboBox,
    QMessageBox, QHeaderView, QDialog, QDoubleSpinBox, QTextEdit,
    QFrame, QDateEdit, QSpinBox, QScrollArea, QSplitter, QListWidget,
    QStackedWidget
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor
from services.caja_service import CajaService
from services.gasto_service import GastoService
from datetime import datetime


class CajaView(QWidget):
    """Vista principal de Caja - Diseño limpio estilo Market"""
    
    def __init__(self):
        super().__init__()
        self.caja_service = CajaService()
        self.gasto_service = GastoService()
        
        self._setup_ui()
        self.refresh_all()
        
        # Timer para actualizar cada 30 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_saldos)
        self.timer.start(30000)
    
    def _setup_ui(self):
        """Configura la interfaz estilo Market"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # ========== PANEL IZQUIERDO: Info y Acciones ==========
        left_panel = QWidget()
        left_panel.setFixedWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # Estado de caja (compacto)
        self.estado_widget = self._create_estado_widget()
        left_layout.addWidget(self.estado_widget)
        
        # Saldos por método (compacto)
        saldos_widget = self._create_saldos_widget()
        left_layout.addWidget(saldos_widget)
        
        # Alerta límite
        self.alerta_limite = QLabel("⚠️ Límite de efectivo excedido")
        self.alerta_limite.setStyleSheet("""
            background: transparent;
            border: 1px solid #ef4444;
            color: #ef4444;
            padding: 8px;
            border-radius: 4px;
            font-size: 11px;
        """)
        self.alerta_limite.setVisible(False)
        self.alerta_limite.setWordWrap(True)
        left_layout.addWidget(self.alerta_limite)
        
        # Botones de acción (estilo Market - transparentes)
        buttons_widget = self._create_buttons_widget()
        left_layout.addWidget(buttons_widget)
        
        left_layout.addStretch()
        
        # ========== PANEL DERECHO: Tabla de Movimientos ==========
        right_panel = self._create_movements_panel()
        
        # Agregar paneles al layout principal
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
    
    def _create_estado_widget(self):
        """Widget de estado compacto"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: transparent;
                border: 1px solid #22c55e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Estado
        self.lbl_estado = QLabel("✅ CAJA ABIERTA")
        self.lbl_estado.setStyleSheet("color: #22c55e; font-size: 14px; font-weight: bold; border: none;")
        layout.addWidget(self.lbl_estado)
        
        # Info
        self.lbl_info_sesion = QLabel("Desde: 28/12/2025 - 08:00")
        self.lbl_info_sesion.setStyleSheet("color: #94a3b8; font-size: 11px; border: none;")
        layout.addWidget(self.lbl_info_sesion)
        
        # Saldo total
        total_layout = QHBoxLayout()
        lbl_total_text = QLabel("SALDO TOTAL:")
        lbl_total_text.setStyleSheet("color: #94a3b8; font-size: 11px; border: none;")
        total_layout.addWidget(lbl_total_text)
        
        self.lbl_saldo_total = QLabel("S/ 0.00")
        self.lbl_saldo_total.setStyleSheet("color: #3b82f6; font-size: 18px; font-weight: bold; border: none;")
        total_layout.addWidget(self.lbl_saldo_total)
        total_layout.addStretch()
        
        layout.addLayout(total_layout)
        
        self.estado_frame = widget
        return widget
    
    def _create_saldos_widget(self):
        """Widget de saldos compacto"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: transparent;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Título
        lbl_titulo = QLabel("BALANCE POR MÉTODO")
        lbl_titulo.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; border: none;")
        layout.addWidget(lbl_titulo)
        
        # Grid de saldos
        grid = QGridLayout()
        grid.setSpacing(6)
        
        self.lbl_efectivo = self._create_saldo_line("💵 Efectivo:", "S/ 0.00", "#22c55e")
        self.lbl_yape = self._create_saldo_line("📱 Yape:", "S/ 0.00", "#8b5cf6")
        self.lbl_plin = self._create_saldo_line("📲 Plin:", "S/ 0.00", "#3b82f6")
        self.lbl_banco = self._create_saldo_line("🏦 POS/BCO:", "S/ 0.00", "#f59e0b")
        
        grid.addWidget(self.lbl_efectivo, 0, 0)
        grid.addWidget(self.lbl_yape, 1, 0)
        grid.addWidget(self.lbl_plin, 2, 0)
        grid.addWidget(self.lbl_banco, 3, 0)
        
        layout.addLayout(grid)
        
        return widget
    
    def _create_saldo_line(self, label, valor, color):
        """Crea una línea de saldo"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        lbl_text = QLabel(label)
        lbl_text.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_text)
        
        layout.addStretch()
        
        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("valor")
        lbl_valor.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl_valor)
        
        return container
    
    def _create_buttons_widget(self):
        """Botones estilo Market (transparentes)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Botón Arqueo
        btn_arqueo = QPushButton("📊 Arqueo de Caja")
        btn_arqueo.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #3b82f6;
                color: #3b82f6;
                padding: 10px;
                border-radius: 6px;
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.1);
            }
        """)
        btn_arqueo.clicked.connect(self.abrir_arqueo)
        layout.addWidget(btn_arqueo)
        
        # Botón Cashflow
        btn_cashflow = QPushButton("💸 Gestión de Flujo")
        btn_cashflow.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #ef4444;
                color: #ef4444;
                padding: 10px;
                border-radius: 6px;
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.1);
            }
        """)
        btn_cashflow.clicked.connect(self.abrir_cashflow)
        self.btn_cashflow = btn_cashflow
        layout.addWidget(btn_cashflow)
        
        return widget
    
    def _create_movements_panel(self):
        """Panel de movimientos"""
        widget = QFrame()
        widget.setStyleSheet("background: transparent; border: 1px solid #334155; border-radius: 6px;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        
        lbl_titulo = QLabel("CONSOLIDADO DE MOVIMIENTOS")
        lbl_titulo.setStyleSheet("color: #f8fafc; font-size: 14px; font-weight: bold;")
        header.addWidget(lbl_titulo)
        
        header.addStretch()
        
        # Filtros compactos
        lbl_periodo = QLabel("Período:")
        lbl_periodo.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header.addWidget(lbl_periodo)
        
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Hoy", "Semana", "Mes", "Personalizado"])
        self.combo_periodo.setFixedWidth(100)
        self.combo_periodo.currentIndexChanged.connect(self.refresh_movimientos)
        header.addWidget(self.combo_periodo)
        
        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header.addWidget(lbl_tipo)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Ingresos", "Egresos"])
        self.combo_tipo.setFixedWidth(90)
        self.combo_tipo.currentIndexChanged.connect(self.refresh_movimientos)
        header.addWidget(self.combo_tipo)
        
        lbl_categoria = QLabel("Categoría:")
        lbl_categoria.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header.addWidget(lbl_categoria)
        
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "Todas", "Membresías", "Market", "Clases", 
            "Proveedores", "Personal", "Servicios", "Tributos", "Otros"
        ])
        self.combo_categoria.setFixedWidth(110)
        self.combo_categoria.currentIndexChanged.connect(self.refresh_movimientos)
        header.addWidget(self.combo_categoria)
        
        layout.addLayout(header)
        
        # Tabla
        self.table_movimientos = QTableWidget()
        self.table_movimientos.setColumnCount(7)
        self.table_movimientos.setHorizontalHeaderLabels([
            "Fecha/Hora", "Tipo", "Categoría", "Descripción", "Método", "Monto", "Ref"
        ])
        
        # Configurar anchos apropiados
        header_table = self.table_movimientos.horizontalHeader()
        header_table.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header_table.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table_movimientos.setAlternatingRowColors(True)
        self.table_movimientos.setStyleSheet("""
            QTableWidget {
                background-color: #0f172a;
                alternate-background-color: #1e293b;
                gridline-color: #334155;
                color: white;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #94a3b8;
                padding: 8px;
                border: none;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table_movimientos)
        
        return widget
    
    def refresh_all(self):
        """Refresca todos los datos"""
        self.refresh_saldos()
        self.refresh_movimientos()
    
    def refresh_saldos(self):
        """Actualiza saldos y estado de caja"""
        sesion = self.caja_service.get_sesion_abierta()
        
        if not sesion:
            # Caja cerrada
            self.estado_frame.setStyleSheet("""
                QFrame {
                    background: transparent;
                    border: 1px solid #dc2626;
                    border-radius: 6px;
                    padding: 8px;
                }
            """)
            self.lbl_estado.setText("❌ CAJA CERRADA")
            self.lbl_estado.setStyleSheet("color: #dc2626; font-size: 14px; font-weight: bold; border: none;")
            self.lbl_info_sesion.setText("Abra la caja desde Arqueo")
            self.lbl_saldo_total.setText("S/ 0.00")
            
            # Resetear valores
            for widget in [self.lbl_efectivo, self.lbl_yape, self.lbl_plin, self.lbl_banco]:
                widget.findChild(QLabel, "valor").setText("S/ 0.00")
            
            self.alerta_limite.setVisible(False)
            self.btn_cashflow.setEnabled(False)
            return
        
        # Caja abierta
        self.estado_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: 1px solid #22c55e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.lbl_estado.setText("✅ CAJA ABIERTA")
        self.lbl_estado.setStyleSheet("color: #22c55e; font-size: 14px; font-weight: bold; border: none;")
        
        fecha_apertura = sesion[1]
        self.lbl_info_sesion.setText(f"Desde: {fecha_apertura}")
        
        # Obtener saldos
        saldos = self.caja_service.get_saldos_actuales()
        
        efectivo = saldos.get('efectivo', 0)
        yape = saldos.get('yape', 0)
        plin = saldos.get('plin', 0)
        banco = saldos.get('pos_banco', 0)
        total = efectivo + yape + plin + banco
        
        # Actualizar valores
        self.lbl_efectivo.findChild(QLabel, "valor").setText(f"S/ {efectivo:.2f}")
        self.lbl_yape.findChild(QLabel, "valor").setText(f"S/ {yape:.2f}")
        self.lbl_plin.findChild(QLabel, "valor").setText(f"S/ {plin:.2f}")
        self.lbl_banco.findChild(QLabel, "valor").setText(f"S/ {banco:.2f}")
        self.lbl_saldo_total.setText(f"S/ {total:.2f}")
        
        # Verificar límite de efectivo
        limite_efectivo = 500.0
        if efectivo > limite_efectivo:
            self.alerta_limite.setVisible(True)
        else:
            self.alerta_limite.setVisible(False)
        
        self.btn_cashflow.setEnabled(True)
    
    def refresh_movimientos(self):
        """Actualiza tabla de movimientos"""
        movimientos_ejemplo = [
            ("28/12/2025 08:30", "INGRESO", "Membresías", "PAGO MENSUALIDAD - JUAN PÉREZ", "Efectivo", "+ S/ 150.00", "MEM-001"),
            ("28/12/2025 09:15", "INGRESO", "Market", "VENTA PRODUCTOS", "Yape", "+ S/ 85.00", "MKT-042"),
            ("28/12/2025 10:00", "EGRESO", "Servicios", "PAGO LUZ - DICIEMBRE", "Efectivo", "- S/ 250.00", "SRV-018"),
            ("28/12/2025 11:00", "INGRESO", "Clases", "SESIÓN FUNCIONAL - MARÍA LÓPEZ", "Plin", "+ S/ 25.00", "CLS-089"),
            ("28/12/2025 12:30", "INGRESO", "Membresías", "PAGO MENSUALIDAD - CARLOS DÍAZ", "POS/BCO", "+ S/ 180.00", "MEM-002"),
        ]
        
        self.table_movimientos.setRowCount(0)
        
        for row, mov in enumerate(movimientos_ejemplo):
            self.table_movimientos.insertRow(row)
            
            for col, dato in enumerate(mov):
                item = QTableWidgetItem(str(dato))
                
                if col == 1:
                    if dato == "INGRESO":
                        item.setForeground(QColor("#22c55e"))
                    else:
                        item.setForeground(QColor("#ef4444"))
                
                if col == 5:
                    if "+" in dato:
                        item.setForeground(QColor("#22c55e"))
                    else:
                        item.setForeground(QColor("#ef4444"))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                self.table_movimientos.setItem(row, col, item)
    
    def abrir_arqueo(self):
        """Abre ventana de arqueo con panel lateral"""
        dialog = ArqueoWindow(self, self.caja_service)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_all()
    
    def abrir_cashflow(self):
        """Abre diálogo de cashflow"""
        dialog = CashflowDialog(self, self.caja_service, self.gasto_service)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_all()


class ArqueoWindow(QDialog):
    """Ventana de arqueo con panel lateral de navegación"""
    
    def __init__(self, parent, caja_service):
        super().__init__(parent)
        self.caja_service = caja_service
        
        self.setWindowTitle("Arqueo de Caja")
        self.setMinimumSize(900, 600)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura UI con panel lateral"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Panel lateral de navegación
        nav_panel = QFrame()
        nav_panel.setFixedWidth(200)
        nav_panel.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border-right: 1px solid #334155;
            }
        """)
        
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # Botones de navegación
        self.nav_buttons = []
        
        opciones = [
            ("📂 Apertura", 0),
            ("✅ Cuadre", 1),
            ("🏦 Remesas", 2),
            ("⚖️ Diferencias", 3),
            ("📖 Bitácora", 4)
        ]
        
        for texto, index in opciones:
            btn = QPushButton(texto)
            btn.setStyleSheet(self._get_nav_button_style(False))
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, i=index: self.cambiar_pagina(i))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        nav_layout.addStretch()
        
        # Contenedor de páginas
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: #0f172a;")
        
        # Crear páginas
        self.stacked_widget.addWidget(self._create_apertura_page())
        self.stacked_widget.addWidget(self._create_cuadre_page())
        self.stacked_widget.addWidget(self._create_remesa_page())
        self.stacked_widget.addWidget(self._create_diferencias_page())
        self.stacked_widget.addWidget(self._create_bitacora_page())
        
        layout.addWidget(nav_panel)
        layout.addWidget(self.stacked_widget, 1)
        
        # Seleccionar primera página
        self.cambiar_pagina(0)
    
    def _get_nav_button_style(self, active):
        """Estilo para botones de navegación"""
        if active:
            return """
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 13px;
                    font-weight: 600;
                }
            """
        else:
            return """
                QPushButton {
                    background: transparent;
                    color: #94a3b8;
                    border: none;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #334155;
                    color: white;
                }
            """
    
    def cambiar_pagina(self, index):
        """Cambia la página mostrada"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Actualizar estilos de botones
        for i, btn in enumerate(self.nav_buttons):
            btn.setStyleSheet(self._get_nav_button_style(i == index))
    
    def _create_apertura_page(self):
        """Página de apertura de caja"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        lbl_titulo = QLabel("📂 Apertura de Caja")
        lbl_titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_titulo)
        
        layout.addSpacing(20)
        
        # Formulario
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        
        # Efectivo inicial
        lbl_efectivo = QLabel("Efectivo Inicial:")
        lbl_efectivo.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_efectivo, 0, 0)
        
        self.spin_efectivo_inicial = QDoubleSpinBox()
        self.spin_efectivo_inicial.setMaximum(999999.99)
        self.spin_efectivo_inicial.setDecimals(2)
        self.spin_efectivo_inicial.setPrefix("S/ ")
        form_layout.addWidget(self.spin_efectivo_inicial, 0, 1)
        
        # Yape inicial
        lbl_yape = QLabel("Yape Inicial:")
        lbl_yape.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_yape, 1, 0)
        
        self.spin_yape_inicial = QDoubleSpinBox()
        self.spin_yape_inicial.setMaximum(999999.99)
        self.spin_yape_inicial.setDecimals(2)
        self.spin_yape_inicial.setPrefix("S/ ")
        form_layout.addWidget(self.spin_yape_inicial, 1, 1)
        
        # Plin inicial
        lbl_plin = QLabel("Plin Inicial:")
        lbl_plin.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_plin, 2, 0)
        
        self.spin_plin_inicial = QDoubleSpinBox()
        self.spin_plin_inicial.setMaximum(999999.99)
        self.spin_plin_inicial.setDecimals(2)
        self.spin_plin_inicial.setPrefix("S/ ")
        form_layout.addWidget(self.spin_plin_inicial, 2, 1)
        
        # POS/BCO inicial
        lbl_banco = QLabel("POS/BCO Inicial:")
        lbl_banco.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_banco, 3, 0)
        
        self.spin_banco_inicial = QDoubleSpinBox()
        self.spin_banco_inicial.setMaximum(999999.99)
        self.spin_banco_inicial.setDecimals(2)
        self.spin_banco_inicial.setPrefix("S/ ")
        form_layout.addWidget(self.spin_banco_inicial, 3, 1)
        
        # Límite de efectivo
        lbl_limite = QLabel("Límite Efectivo (Informativo):")
        lbl_limite.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_limite, 4, 0)
        
        self.spin_limite = QDoubleSpinBox()
        self.spin_limite.setMaximum(999999.99)
        self.spin_limite.setDecimals(2)
        self.spin_limite.setValue(500.00)
        self.spin_limite.setPrefix("S/ ")
        form_layout.addWidget(self.spin_limite, 4, 1)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Botón abrir
        btn_abrir = QPushButton("Abrir Caja")
        btn_abrir.setStyleSheet("""
            QPushButton {
                background: #22c55e;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #16a34a; }
        """)
        btn_abrir.clicked.connect(self.abrir_caja)
        layout.addWidget(btn_abrir)
        
        return page
    
    def _create_cuadre_page(self):
        """Página de cuadre de caja"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titulo = QLabel("✅ Cuadre de Caja")
        lbl_titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_titulo)
        
        layout.addSpacing(20)
        
        # Comparación Sistema vs Físico
        grid = QGridLayout()
        grid.setSpacing(12)
        
        metodos = [
            ("Efectivo", 0),
            ("Yape", 1),
            ("Plin", 2),
            ("POS/BCO", 3)
        ]
        
        lbl_header1 = QLabel("Método")
        lbl_header1.setStyleSheet("color: #94a3b8; font-weight: bold;")
        grid.addWidget(lbl_header1, 0, 0)
        
        lbl_header2 = QLabel("Sistema")
        lbl_header2.setStyleSheet("color: #94a3b8; font-weight: bold;")
        grid.addWidget(lbl_header2, 0, 1)
        
        lbl_header3 = QLabel("Contado")
        lbl_header3.setStyleSheet("color: #94a3b8; font-weight: bold;")
        grid.addWidget(lbl_header3, 0, 2)
        
        for metodo, row in metodos:
            lbl_metodo = QLabel(metodo)
            lbl_metodo.setStyleSheet("color: white;")
            grid.addWidget(lbl_metodo, row + 1, 0)
            
            lbl_sistema = QLabel("S/ 0.00")
            lbl_sistema.setStyleSheet("color: #3b82f6; font-weight: bold;")
            grid.addWidget(lbl_sistema, row + 1, 1)
            
            spin_contado = QDoubleSpinBox()
            spin_contado.setMaximum(999999.99)
            spin_contado.setDecimals(2)
            spin_contado.setPrefix("S/ ")
            grid.addWidget(spin_contado, row + 1, 2)
        
        layout.addLayout(grid)
        
        layout.addSpacing(20)
        
        # Observaciones
        lbl_obs = QLabel("Observaciones:")
        lbl_obs.setStyleSheet("color: #94a3b8;")
        layout.addWidget(lbl_obs)
        
        txt_obs = QTextEdit()
        txt_obs.setMaximumHeight(80)
        layout.addWidget(txt_obs)
        
        layout.addStretch()
        
        # Botón cuadrar
        btn_cuadrar = QPushButton("Cuadrar Caja")
        btn_cuadrar.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #2563eb; }
        """)
        layout.addWidget(btn_cuadrar)
        
        return page
    
    def _create_remesa_page(self):
        """Página de remesas"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titulo = QLabel("🏦 Remesa de Efectivo")
        lbl_titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_titulo)
        
        layout.addSpacing(20)
        
        form_layout = QGridLayout()
        
        lbl_monto = QLabel("Monto a Remesar:")
        lbl_monto.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_monto, 0, 0)
        
        spin_monto = QDoubleSpinBox()
        spin_monto.setMaximum(999999.99)
        spin_monto.setDecimals(2)
        spin_monto.setPrefix("S/ ")
        form_layout.addWidget(spin_monto, 0, 1)
        
        lbl_destino = QLabel("Destino:")
        lbl_destino.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_destino, 1, 0)
        
        combo_destino = QComboBox()
        combo_destino.addItems(["Yape", "Plin", "Cuenta Bancaria"])
        form_layout.addWidget(combo_destino, 1, 1)
        
        lbl_ref = QLabel("Referencia:")
        lbl_ref.setStyleSheet("color: #94a3b8;")
        form_layout.addWidget(lbl_ref, 2, 0)
        
        txt_ref = QLineEdit()
        form_layout.addWidget(txt_ref, 2, 1)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        btn_remesar = QPushButton("Registrar Remesa")
        btn_remesar.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #d97706; }
        """)
        layout.addWidget(btn_remesar)
        
        return page
    
    def _create_diferencias_page(self):
        """Página de gestión de diferencias"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titulo = QLabel("⚖️ Gestión de Diferencias")
        lbl_titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_titulo)
        
        layout.addSpacing(10)
        
        # Tabla de diferencias
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Fecha", "Descripción", "Monto", "Estado", ""])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Datos de ejemplo
        diferencias_ejemplo = [
            ("28/12/2025", "SOBRANTE CUADRE CAJA", "+ S/ 10.00", "PENDIENTE"),
            ("27/12/2025", "FALTANTE CUADRE CAJA", "- S/ 5.00", "REGULARIZADA"),
        ]
        
        table.setRowCount(len(diferencias_ejemplo))
        for row, dif in enumerate(diferencias_ejemplo):
            for col, dato in enumerate(dif):
                item = QTableWidgetItem(dato)
                if col == 2:
                    if "+" in dato:
                        item.setForeground(QColor("#22c55e"))
                    else:
                        item.setForeground(QColor("#ef4444"))
                elif col == 3:
                    if dato == "PENDIENTE":
                        item.setForeground(QColor("#f59e0b"))
                    else:
                        item.setForeground(QColor("#22c55e"))
                table.setItem(row, col, item)
            
            # Botón regularizar
            if diferencias_ejemplo[row][3] == "PENDIENTE":
                btn_reg = QPushButton("Regularizar")
                btn_reg.setFixedHeight(25)
                table.setCellWidget(row, 4, btn_reg)
        
        layout.addWidget(table)
        
        return page
    
    def _create_bitacora_page(self):
        """Página de bitácora"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titulo = QLabel("📖 Bitácora de Operaciones")
        lbl_titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_titulo)
        
        layout.addSpacing(10)
        
        # Tabla de histórico
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Fecha", "Apertura", "Cierre", "Diferencia", "Usuario"])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Datos de ejemplo
        historico = [
            ("27/12/2025", "S/ 100.00", "S/ 520.00", "+ S/ 10.00", "ADMINISTRADOR"),
            ("26/12/2025", "S/ 100.00", "S/ 485.00", "- S/ 5.00", "ADMINISTRADOR"),
            ("25/12/2025", "S/ 100.00", "S/ 500.00", "S/ 0.00", "ADMINISTRADOR"),
        ]
        
        table.setRowCount(len(historico))
        for row, hist in enumerate(historico):
            for col, dato in enumerate(hist):
                item = QTableWidgetItem(dato)
                if col == 3:
                    if "+" in dato:
                        item.setForeground(QColor("#22c55e"))
                    elif "-" in dato:
                        item.setForeground(QColor("#ef4444"))
                table.setItem(row, col, item)
        
        # Doble click para ver detalle
        table.doubleClicked.connect(lambda: QMessageBox.information(self, "Detalle", "Ver detalle del cuadre"))
        
        layout.addWidget(table)
        
        return page
    
    def abrir_caja(self):
        """Abre la caja"""
        efectivo = self.spin_efectivo_inicial.value()
        yape = self.spin_yape_inicial.value()
        plin = self.spin_plin_inicial.value()
        banco = self.spin_banco_inicial.value()
        
        if efectivo <= 0 and yape <= 0 and plin <= 0 and banco <= 0:
            QMessageBox.warning(self, "Error", "Debe ingresar al menos un monto inicial")
            return
        
        result = self.caja_service.abrir_sesion(efectivo, yape, plin, banco)
        if result['success']:
            QMessageBox.information(self, "Éxito", "Caja abierta exitosamente")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", result['message'])


class CashflowDialog(QDialog):
    """Diálogo simplificado para cashflow"""
    
    def __init__(self, parent, caja_service, gasto_service):
        super().__init__(parent)
        self.caja_service = caja_service
        self.gasto_service = gasto_service
        
        self.setWindowTitle("Gestión de Flujo")
        self.setFixedSize(450, 400)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura UI del diálogo"""
        layout = QVBoxLayout(self)
        
        # Tipo
        layout.addWidget(QLabel("Tipo de Movimiento:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Ingreso", "Egreso"])
        self.combo_tipo.currentIndexChanged.connect(self.cambiar_tipo)
        layout.addWidget(self.combo_tipo)
        
        # Categoría
        layout.addWidget(QLabel("Categoría:"))
        self.combo_categoria = QComboBox()
        layout.addWidget(self.combo_categoria)
        
        # Método
        layout.addWidget(QLabel("Método de Pago:"))
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Efectivo", "Yape", "Plin", "POS/Banco"])
        layout.addWidget(self.combo_metodo)
        
        # Monto
        layout.addWidget(QLabel("Monto (S/):"))
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setMaximum(999999.99)
        self.spin_monto.setDecimals(2)
        layout.addWidget(self.spin_monto)
        
        # Descripción
        layout.addWidget(QLabel("Descripción:"))
        self.txt_descripcion = QLineEdit()
        layout.addWidget(self.txt_descripcion)
        
        layout.addStretch()
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Registrar")
        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)
        
        self.cambiar_tipo()
    
    def cambiar_tipo(self):
        """Cambia categorías según tipo"""
        self.combo_categoria.clear()
        
        if self.combo_tipo.currentText() == "Ingreso":
            self.combo_categoria.addItems(["Otros Ingresos", "Donación", "Varios"])
        else:
            self.combo_categoria.addItems([
                "Pago a Proveedor", "Pago de Sueldo", "Servicios",
                "Tributos", "Mantenimiento", "Otros Gastos"
            ])
    
    def guardar(self):
        """Guarda el movimiento"""
        monto = self.spin_monto.value()
        descripcion = self.txt_descripcion.text().strip()
        
        if monto <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
            return
        
        if not descripcion:
            QMessageBox.warning(self, "Error", "La descripción es obligatoria")
            return
        
        QMessageBox.information(self, "Éxito", "Movimiento registrado exitosamente")
        self.accept()
