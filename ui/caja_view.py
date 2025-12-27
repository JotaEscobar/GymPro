# -*- coding: utf-8 -*-
"""
Vista de Caja - Gestión de Sesiones, Movimientos y Gastos
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, QComboBox,
    QMessageBox, QHeaderView, QDialog, QDoubleSpinBox, QTextEdit,
    QFrame, QGridLayout, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from services.caja_service import CajaService
from services.gasto_service import GastoService
from datetime import datetime


class CajaView(QWidget):
    """Vista principal de Caja con 4 pestañas"""
    
    def __init__(self):
        super().__init__()
        self.caja_service = CajaService()
        self.gasto_service = GastoService()
        
        self._setup_ui()
        self._check_sesion_abierta()
    
    def _setup_ui(self):
        """Configura la interfaz con pestañas"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Sesión Actual
        self.tab_sesion = SesionActualTab(self.caja_service)
        self.tabs.addTab(self.tab_sesion, "🏦 Sesión Actual")
        
        # Tab 2: Movimientos
        self.tab_movimientos = MovimientosTab(self.caja_service)
        self.tabs.addTab(self.tab_movimientos, "💸 Movimientos")
        
        # Tab 3: Arqueo
        self.tab_arqueo = ArqueoTab(self.caja_service)
        self.tabs.addTab(self.tab_arqueo, "📋 Arqueo de Caja")
        
        # Tab 4: Gastos
        self.tab_gastos = GastosTab(self.gasto_service)
        self.tabs.addTab(self.tab_gastos, "💵 Gastos")
        
        layout.addWidget(self.tabs)
        
        # Conectar señales
        self.tab_sesion.sesion_cambio.connect(self.tab_movimientos.refresh)
        self.tab_sesion.sesion_cambio.connect(self.tab_arqueo.refresh)
        self.tab_gastos.gasto_registrado.connect(self.tab_movimientos.refresh)
        self.tab_gastos.gasto_registrado.connect(self.tab_sesion.refresh_saldos)
    
    def _check_sesion_abierta(self):
        """Verifica si hay sesión abierta al iniciar"""
        sesion = self.caja_service.get_sesion_abierta()
        
        if not sesion:
            # No hay sesión, deshabilitar tabs excepto arqueo
            self.tabs.setTabEnabled(0, True)  # Sesión (para abrir)
            self.tabs.setTabEnabled(1, False)  # Movimientos
            self.tabs.setTabEnabled(2, True)  # Arqueo (para abrir)
            self.tabs.setTabEnabled(3, False)  # Gastos
        else:
            # Hay sesión, habilitar todo
            self.tabs.setTabEnabled(0, True)
            self.tabs.setTabEnabled(1, True)
            self.tabs.setTabEnabled(2, True)
            self.tabs.setTabEnabled(3, True)


class SesionActualTab(QWidget):
    """Pestaña de sesión actual con saldos en tiempo real"""
    
    sesion_cambio = pyqtSignal()
    
    def __init__(self, caja_service):
        super().__init__()
        self.caja_service = caja_service
        self._setup_ui()
        self.refresh_saldos()
        
        # Timer para actualizar cada 30 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_saldos)
        self.timer.start(30000)  # 30 segundos
    
    def _setup_ui(self):
        """Configura UI de sesión actual"""
        layout = QVBoxLayout(self)
        
        # Header estado
        self.estado_frame = QFrame()
        self.estado_frame.setFixedHeight(80)
        estado_layout = QVBoxLayout(self.estado_frame)
        
        self.lbl_estado = QLabel("⏳ Verificando estado...")
        self.lbl_estado.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        estado_layout.addWidget(self.lbl_estado)
        
        self.lbl_info = QLabel("")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        estado_layout.addWidget(self.lbl_info)
        
        layout.addWidget(self.estado_frame)
        
        # Grid de saldos
        saldos_frame = QFrame()
        saldos_frame.setStyleSheet("background: #1e293b; border-radius: 8px; padding: 15px;")
        saldos_layout = QGridLayout(saldos_frame)
        
        # Efectivo
        self.card_efectivo = self._create_saldo_card("💵 Efectivo", "S/ 0.00", "#22c55e")
        saldos_layout.addWidget(self.card_efectivo, 0, 0)
        
        # Yape
        self.card_yape = self._create_saldo_card("📱 Yape", "S/ 0.00", "#7c3aed")
        saldos_layout.addWidget(self.card_yape, 0, 1)
        
        # Plin
        self.card_plin = self._create_saldo_card("📲 Plin", "S/ 0.00", "#3b82f6")
        saldos_layout.addWidget(self.card_plin, 1, 0)
        
        # POS/Banco
        self.card_banco = self._create_saldo_card("🏦 POS/Banco", "S/ 0.00", "#f59e0b")
        saldos_layout.addWidget(self.card_banco, 1, 1)
        
        layout.addWidget(saldos_frame)
        
        # Total
        total_frame = QFrame()
        total_frame.setStyleSheet("background: #0f172a; border: 2px solid #3b82f6; border-radius: 8px; padding: 20px;")
        total_layout = QVBoxLayout(total_frame)
        
        lbl_total_text = QLabel("SALDO TOTAL EN CAJA")
        lbl_total_text.setStyleSheet("color: #94a3b8; font-size: 14px;")
        lbl_total_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(lbl_total_text)
        
        self.lbl_total = QLabel("S/ 0.00")
        self.lbl_total.setStyleSheet("color: #3b82f6; font-size: 32px; font-weight: bold;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(self.lbl_total)
        
        layout.addWidget(total_frame)
        
        # Botones
        self.btn_remesa = QPushButton("🏦 Remesar Efectivo")
        self.btn_remesa.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #2563eb; }
            QPushButton:disabled { background: #64748b; }
        """)
        self.btn_remesa.clicked.connect(self.remesar_efectivo)
        layout.addWidget(self.btn_remesa)
        
        layout.addStretch()
    
    def _create_saldo_card(self, titulo, valor, color):
        """Crea una tarjeta de saldo"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        card.setFixedHeight(100)
        
        card_layout = QVBoxLayout(card)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("color: white; font-size: 14px; font-weight: 600;")
        card_layout.addWidget(lbl_titulo)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("valor")
        lbl_valor.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        card_layout.addWidget(lbl_valor)
        
        return card
    
    def refresh_saldos(self):
        """Actualiza saldos actuales"""
        sesion = self.caja_service.get_sesion_abierta()
        
        if not sesion:
            self.estado_frame.setStyleSheet("background: #dc2626; border-radius: 8px;")
            self.lbl_estado.setText("❌ CAJA CERRADA")
            self.lbl_info.setText("Abre la caja desde la pestaña 'Arqueo'")
            self.btn_remesa.setEnabled(False)
            
            # Resetear valores
            for card in [self.card_efectivo, self.card_yape, self.card_plin, self.card_banco]:
                card.findChild(QLabel, "valor").setText("S/ 0.00")
            self.lbl_total.setText("S/ 0.00")
            return
        
        # Sesión abierta
        self.estado_frame.setStyleSheet("background: #22c55e; border-radius: 8px;")
        self.lbl_estado.setText("✅ CAJA ABIERTA")
        
        fecha_apertura = sesion[1]
        self.lbl_info.setText(f"Abierta desde: {fecha_apertura}")
        
        self.btn_remesa.setEnabled(True)
        
        # Obtener saldos
        saldos = self.caja_service.get_saldos_actuales()
        
        if saldos:
            efectivo = saldos.get('efectivo_esperado', 0)
            yape = saldos.get('yape_esperado', 0)
            plin = saldos.get('plin_esperado', 0)
            banco = saldos.get('pos_banco_esperado', 0)
            total = efectivo + yape + plin + banco
            
            self.card_efectivo.findChild(QLabel, "valor").setText(f"S/ {efectivo:.2f}")
            self.card_yape.findChild(QLabel, "valor").setText(f"S/ {yape:.2f}")
            self.card_plin.findChild(QLabel, "valor").setText(f"S/ {plin:.2f}")
            self.card_banco.findChild(QLabel, "valor").setText(f"S/ {banco:.2f}")
            self.lbl_total.setText(f"S/ {total:.2f}")
    
    def remesar_efectivo(self):
        """Diálogo para remesar efectivo"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Remesar Efectivo a Banco")
        dialog.setFixedSize(300, 150)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Monto a remesar (S/):"))
        spin_monto = QDoubleSpinBox()
        spin_monto.setMaximum(999999.99)
        spin_monto.setDecimals(2)
        layout.addWidget(spin_monto)
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Remesar")
        btn_cancel = QPushButton("Cancelar")
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        def remesar():
            monto = spin_monto.value()
            if monto <= 0:
                QMessageBox.warning(dialog, "Error", "Ingresa un monto válido")
                return
            
            result = self.caja_service.registrar_remesa(monto)
            
            if result['success']:
                QMessageBox.information(dialog, "Éxito", "Remesa registrada")
                self.refresh_saldos()
                self.sesion_cambio.emit()
                dialog.accept()
            else:
                QMessageBox.critical(dialog, "Error", result['message'])
        
        btn_ok.clicked.connect(remesar)
        btn_cancel.clicked.connect(dialog.reject)
        
        dialog.exec()


class MovimientosTab(QWidget):
    """Pestaña de movimientos de efectivo"""
    
    def __init__(self, caja_service):
        super().__init__()
        self.caja_service = caja_service
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Configura UI de movimientos"""
        layout = QVBoxLayout(self)
        
        # Filtros
        filtros = QHBoxLayout()
        
        filtros.addWidget(QLabel("Período:"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Hoy", "Última semana", "Último mes", "Personalizado"])
        self.combo_periodo.currentIndexChanged.connect(self.on_periodo_changed)
        filtros.addWidget(self.combo_periodo)
        
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setVisible(False)
        filtros.addWidget(self.fecha_inicio)
        
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setVisible(False)
        filtros.addWidget(self.fecha_fin)
        
        filtros.addWidget(QLabel("Categoría:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Todas", None)
        self.combo_categoria.addItem("Membresía", "membresia")
        self.combo_categoria.addItem("Clases", "clase")
        self.combo_categoria.addItem("Market", "market")
        self.combo_categoria.addItem("Gastos", "gasto")
        self.combo_categoria.addItem("Ajustes", "ajuste")
        self.combo_categoria.addItem("Remesas", "remesa")
        self.combo_categoria.currentIndexChanged.connect(self.refresh)
        filtros.addWidget(self.combo_categoria)
        
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.refresh)
        filtros.addWidget(btn_filtrar)
        
        filtros.addStretch()
        layout.addLayout(filtros)
        
        # Resumen
        resumen_frame = QFrame()
        resumen_frame.setStyleSheet("background: #1e293b; border-radius: 8px; padding: 10px;")
        resumen_layout = QHBoxLayout(resumen_frame)
        
        self.lbl_ingresos = QLabel("Ingresos: S/ 0.00")
        self.lbl_ingresos.setStyleSheet("color: #22c55e; font-weight: bold;")
        resumen_layout.addWidget(self.lbl_ingresos)
        
        self.lbl_egresos = QLabel("Egresos: S/ 0.00")
        self.lbl_egresos.setStyleSheet("color: #ef4444; font-weight: bold;")
        resumen_layout.addWidget(self.lbl_egresos)
        
        self.lbl_neto = QLabel("Neto: S/ 0.00")
        self.lbl_neto.setStyleSheet("color: #3b82f6; font-weight: bold;")
        resumen_layout.addWidget(self.lbl_neto)
        
        layout.addWidget(resumen_frame)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Fecha/Hora", "Tipo", "Categoría", "Método", "Monto", "Descripción"
        ])
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
    
    def on_periodo_changed(self, index):
        """Maneja cambio de período"""
        if index == 3:  # Personalizado
            self.fecha_inicio.setVisible(True)
            self.fecha_fin.setVisible(True)
        else:
            self.fecha_inicio.setVisible(False)
            self.fecha_fin.setVisible(False)
    
    def refresh(self):
        """Recarga movimientos"""
        # Determinar fechas según período
        periodo = self.combo_periodo.currentIndex()
        
        if periodo == 0:  # Hoy
            movimientos = self.caja_service.get_movimientos_hoy()
        else:
            # Para otros períodos, usar fecha actual
            fecha_inicio = QDate.currentDate().toString(Qt.DateFormat.ISODate)
            fecha_fin = QDate.currentDate().toString(Qt.DateFormat.ISODate)
            
            if periodo == 1:  # Última semana
                fecha_inicio = QDate.currentDate().addDays(-7).toString(Qt.DateFormat.ISODate)
            elif periodo == 2:  # Último mes
                fecha_inicio = QDate.currentDate().addMonths(-1).toString(Qt.DateFormat.ISODate)
            elif periodo == 3:  # Personalizado
                fecha_inicio = self.fecha_inicio.date().toString(Qt.DateFormat.ISODate)
                fecha_fin = self.fecha_fin.date().toString(Qt.DateFormat.ISODate)
            
            categoria = self.combo_categoria.currentData()
            movimientos = self.caja_service.get_movimientos(fecha_inicio, fecha_fin, categoria)
        
        # Calcular totales
        total_ingresos = sum(m[5] for m in movimientos if m[2] == 'ingreso')
        total_egresos = sum(m[5] for m in movimientos if m[2] == 'egreso')
        neto = total_ingresos - total_egresos
        
        self.lbl_ingresos.setText(f"Ingresos: S/ {total_ingresos:.2f}")
        self.lbl_egresos.setText(f"Egresos: S/ {total_egresos:.2f}")
        self.lbl_neto.setText(f"Neto: S/ {neto:.2f}")
        
        # Llenar tabla
        self.table.setRowCount(0)
        for row, mov in enumerate(movimientos):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(mov[0])))
            self.table.setItem(row, 1, QTableWidgetItem(mov[1]))
            
            # Tipo con color
            tipo_item = QTableWidgetItem(mov[2].upper())
            if mov[2] == 'ingreso':
                tipo_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                tipo_item.setForeground(Qt.GlobalColor.darkRed)
            self.table.setItem(row, 2, tipo_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(mov[3]))
            self.table.setItem(row, 4, QTableWidgetItem(mov[4]))
            
            # Monto con signo
            signo = "+" if mov[2] == 'ingreso' else "-"
            monto_item = QTableWidgetItem(f"{signo} S/ {mov[5]:.2f}")
            monto_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, monto_item)
            
            self.table.setItem(row, 6, QTableWidgetItem(mov[6] or ""))


class ArqueoTab(QWidget):
    """Pestaña de arqueo (abrir/cerrar caja)"""
    
    def __init__(self, caja_service):
        super().__init__()
        self.caja_service = caja_service
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Configura UI de arqueo"""
        layout = QVBoxLayout(self)
        
        # Estado actual
        self.lbl_estado = QLabel("⏳ Verificando estado...")
        self.lbl_estado.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_estado)
        
        # Panel apertura
        self.panel_apertura = QFrame()
        self.panel_apertura.setStyleSheet("background: #1e293b; border-radius: 8px; padding: 15px;")
        apertura_layout = QVBoxLayout(self.panel_apertura)
        
        apertura_layout.addWidget(QLabel("💰 Apertura de Caja"))
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Efectivo Inicial:"), 0, 0)
        self.spin_efectivo_ini = QDoubleSpinBox()
        self.spin_efectivo_ini.setMaximum(99999.99)
        grid.addWidget(self.spin_efectivo_ini, 0, 1)
        
        grid.addWidget(QLabel("Yape Inicial:"), 1, 0)
        self.spin_yape_ini = QDoubleSpinBox()
        self.spin_yape_ini.setMaximum(99999.99)
        grid.addWidget(self.spin_yape_ini, 1, 1)
        
        grid.addWidget(QLabel("Plin Inicial:"), 2, 0)
        self.spin_plin_ini = QDoubleSpinBox()
        self.spin_plin_ini.setMaximum(99999.99)
        grid.addWidget(self.spin_plin_ini, 2, 1)
        
        grid.addWidget(QLabel("POS/Banco Inicial:"), 3, 0)
        self.spin_banco_ini = QDoubleSpinBox()
        self.spin_banco_ini.setMaximum(99999.99)
        grid.addWidget(self.spin_banco_ini, 3, 1)
        
        apertura_layout.addLayout(grid)
        
        btn_abrir = QPushButton("✅ Abrir Caja")
        btn_abrir.setStyleSheet("""
            QPushButton {
                background: #22c55e;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #16a34a; }
        """)
        btn_abrir.clicked.connect(self.abrir_caja)
        apertura_layout.addWidget(btn_abrir)
        
        layout.addWidget(self.panel_apertura)
        
        # Panel cierre
        self.panel_cierre = QFrame()
        self.panel_cierre.setStyleSheet("background: #1e293b; border-radius: 8px; padding: 15px;")
        cierre_layout = QVBoxLayout(self.panel_cierre)
        
        cierre_layout.addWidget(QLabel("📋 Cierre de Caja"))
        
        # Esperado vs Contado
        self.frame_comparacion = QFrame()
        comp_layout = QGridLayout(self.frame_comparacion)
        
        comp_layout.addWidget(QLabel("Método"), 0, 0)
        comp_layout.addWidget(QLabel("Esperado"), 0, 1)
        comp_layout.addWidget(QLabel("Contado"), 0, 2)
        comp_layout.addWidget(QLabel("Diferencia"), 0, 3)
        
        # Efectivo
        comp_layout.addWidget(QLabel("💵 Efectivo:"), 1, 0)
        self.lbl_efectivo_esp = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_efectivo_esp, 1, 1)
        self.spin_efectivo_cont = QDoubleSpinBox()
        self.spin_efectivo_cont.setMaximum(99999.99)
        self.spin_efectivo_cont.valueChanged.connect(self.calcular_diferencias)
        comp_layout.addWidget(self.spin_efectivo_cont, 1, 2)
        self.lbl_efectivo_dif = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_efectivo_dif, 1, 3)
        
        # Yape
        comp_layout.addWidget(QLabel("📱 Yape:"), 2, 0)
        self.lbl_yape_esp = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_yape_esp, 2, 1)
        self.spin_yape_cont = QDoubleSpinBox()
        self.spin_yape_cont.setMaximum(99999.99)
        self.spin_yape_cont.valueChanged.connect(self.calcular_diferencias)
        comp_layout.addWidget(self.spin_yape_cont, 2, 2)
        self.lbl_yape_dif = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_yape_dif, 2, 3)
        
        # Plin
        comp_layout.addWidget(QLabel("📲 Plin:"), 3, 0)
        self.lbl_plin_esp = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_plin_esp, 3, 1)
        self.spin_plin_cont = QDoubleSpinBox()
        self.spin_plin_cont.setMaximum(99999.99)
        self.spin_plin_cont.valueChanged.connect(self.calcular_diferencias)
        comp_layout.addWidget(self.spin_plin_cont, 3, 2)
        self.lbl_plin_dif = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_plin_dif, 3, 3)
        
        # Banco
        comp_layout.addWidget(QLabel("🏦 POS/Banco:"), 4, 0)
        self.lbl_banco_esp = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_banco_esp, 4, 1)
        self.spin_banco_cont = QDoubleSpinBox()
        self.spin_banco_cont.setMaximum(99999.99)
        self.spin_banco_cont.valueChanged.connect(self.calcular_diferencias)
        comp_layout.addWidget(self.spin_banco_cont, 4, 2)
        self.lbl_banco_dif = QLabel("S/ 0.00")
        comp_layout.addWidget(self.lbl_banco_dif, 4, 3)
        
        cierre_layout.addWidget(self.frame_comparacion)
        
        # Observaciones
        cierre_layout.addWidget(QLabel("Observaciones:"))
        self.text_observaciones = QTextEdit()
        self.text_observaciones.setMaximumHeight(60)
        cierre_layout.addWidget(self.text_observaciones)
        
        btn_cerrar = QPushButton("🔒 Cerrar Caja")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background: #dc2626;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #b91c1c; }
        """)
        btn_cerrar.clicked.connect(self.cerrar_caja)
        cierre_layout.addWidget(btn_cerrar)
        
        layout.addWidget(self.panel_cierre)
    
    def refresh(self):
        """Actualiza estado de la caja"""
        sesion = self.caja_service.get_sesion_abierta()
        
        if not sesion:
            self.lbl_estado.setText("❌ Caja Cerrada - Abre una nueva sesión")
            self.panel_apertura.setVisible(True)
            self.panel_cierre.setVisible(False)
        else:
            self.lbl_estado.setText(f"✅ Caja Abierta desde: {sesion[1]}")
            self.panel_apertura.setVisible(False)
            self.panel_cierre.setVisible(True)
            
            # Cargar saldos esperados
            saldos = self.caja_service.get_totales_sesion(sesion[0])
            if saldos:
                self.lbl_efectivo_esp.setText(f"S/ {saldos['efectivo_esperado']:.2f}")
                self.lbl_yape_esp.setText(f"S/ {saldos['yape_esperado']:.2f}")
                self.lbl_plin_esp.setText(f"S/ {saldos['plin_esperado']:.2f}")
                self.lbl_banco_esp.setText(f"S/ {saldos['pos_banco_esperado']:.2f}")
    
    def abrir_caja(self):
        """Abre una nueva sesión de caja"""
        efectivo = self.spin_efectivo_ini.value()
        yape = self.spin_yape_ini.value()
        plin = self.spin_plin_ini.value()
        banco = self.spin_banco_ini.value()
        
        result = self.caja_service.abrir_caja(efectivo, yape, plin, banco)
        
        if result['success']:
            QMessageBox.information(self, "Éxito", "Caja abierta exitosamente")
            self.refresh()
        else:
            QMessageBox.critical(self, "Error", result['message'])
    
    def calcular_diferencias(self):
        """Calcula y muestra diferencias"""
        # Obtener esperados
        def parse_saldo(lbl):
            return float(lbl.text().replace("S/ ", "").replace(",", ""))
        
        ef_esp = parse_saldo(self.lbl_efectivo_esp)
        ya_esp = parse_saldo(self.lbl_yape_esp)
        pl_esp = parse_saldo(self.lbl_plin_esp)
        ba_esp = parse_saldo(self.lbl_banco_esp)
        
        # Obtener contados
        ef_cont = self.spin_efectivo_cont.value()
        ya_cont = self.spin_yape_cont.value()
        pl_cont = self.spin_plin_cont.value()
        ba_cont = self.spin_banco_cont.value()
        
        # Calcular diferencias
        ef_dif = ef_cont - ef_esp
        ya_dif = ya_cont - ya_esp
        pl_dif = pl_cont - pl_esp
        ba_dif = ba_cont - ba_esp
        
        # Mostrar con color
        def set_dif_label(lbl, dif):
            color = "#22c55e" if abs(dif) < 0.01 else "#ef4444"
            signo = "+" if dif > 0 else ""
            lbl.setText(f"{signo}S/ {dif:.2f}")
            lbl.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        set_dif_label(self.lbl_efectivo_dif, ef_dif)
        set_dif_label(self.lbl_yape_dif, ya_dif)
        set_dif_label(self.lbl_plin_dif, pl_dif)
        set_dif_label(self.lbl_banco_dif, ba_dif)
    
    def cerrar_caja(self):
        """Cierra la sesión de caja"""
        sesion = self.caja_service.get_sesion_abierta()
        if not sesion:
            return
        
        # Confirmar
        reply = QMessageBox.question(
            self, "Confirmar Cierre",
            "¿Estás seguro de cerrar la caja?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Obtener valores contados
        efectivo = self.spin_efectivo_cont.value()
        yape = self.spin_yape_cont.value()
        plin = self.spin_plin_cont.value()
        banco = self.spin_banco_cont.value()
        obs = self.text_observaciones.toPlainText()
        
        result = self.caja_service.cerrar_caja(
            sesion[0], efectivo, yape, plin, banco, None, obs
        )
        
        if result['success']:
            diferencias = result.get('data', {}).get('diferencias', {})
            
            msg = "Caja cerrada exitosamente\n\n"
            if any(abs(v) > 0.01 for v in diferencias.values()):
                msg += "⚠️ Se detectaron diferencias:\n"
                for metodo, dif in diferencias.items():
                    if abs(dif) > 0.01:
                        msg += f"{metodo}: {'+' if dif > 0 else ''}S/ {dif:.2f}\n"
            
            QMessageBox.information(self, "Éxito", msg)
            self.refresh()
        else:
            QMessageBox.critical(self, "Error", result['message'])


class GastosTab(QWidget):
    """Pestaña de registro y gestión de gastos"""
    
    gasto_registrado = pyqtSignal()
    
    def __init__(self, gasto_service):
        super().__init__()
        self.gasto_service = gasto_service
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Configura UI de gastos"""
        layout = QVBoxLayout(self)
        
        # Botón nuevo gasto
        btn_nuevo = QPushButton("➕ Registrar Nuevo Gasto")
        btn_nuevo.setStyleSheet("""
            QPushButton {
                background: #dc2626;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #b91c1c; }
        """)
        btn_nuevo.clicked.connect(self.nuevo_gasto)
        layout.addWidget(btn_nuevo)
        
        # Filtros
        filtros = QHBoxLayout()
        
        filtros.addWidget(QLabel("Período:"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Hoy", "Esta semana", "Este mes", "Personalizado"])
        self.combo_periodo.currentIndexChanged.connect(self.refresh)
        filtros.addWidget(self.combo_periodo)
        
        filtros.addWidget(QLabel("Tipo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Todos", None)
        tipos = self.gasto_service.get_tipos_gasto()
        for tipo in tipos:
            self.combo_tipo.addItem(tipo.title(), tipo)
        self.combo_tipo.currentIndexChanged.connect(self.refresh)
        filtros.addWidget(self.combo_tipo)
        
        filtros.addStretch()
        layout.addLayout(filtros)
        
        # Total del período
        self.lbl_total = QLabel("Total: S/ 0.00")
        self.lbl_total.setStyleSheet("""
            background: #1e293b;
            color: #ef4444;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            border-radius: 6px;
        """)
        layout.addWidget(self.lbl_total)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Fecha/Hora", "Tipo", "Descripción", "Método Pago", "Monto"
        ])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
    
    def refresh(self):
        """Recarga gastos"""
        # Determinar fechas
        periodo = self.combo_periodo.currentIndex()
        
        if periodo == 0:  # Hoy
            gastos = self.gasto_service.get_gastos_hoy()
            fecha_inicio = QDate.currentDate().toString(Qt.DateFormat.ISODate)
            fecha_fin = fecha_inicio
        else:
            fecha_fin = QDate.currentDate().toString(Qt.DateFormat.ISODate)
            
            if periodo == 1:  # Esta semana
                fecha_inicio = QDate.currentDate().addDays(-7).toString(Qt.DateFormat.ISODate)
            elif periodo == 2:  # Este mes
                fecha_inicio = QDate.currentDate().addMonths(-1).toString(Qt.DateFormat.ISODate)
            else:  # Personalizado
                fecha_inicio = fecha_fin
            
            tipo = self.combo_tipo.currentData()
            gastos = self.gasto_service.get_gastos(fecha_inicio, fecha_fin, tipo)
        
        # Calcular total
        total = sum(g[3] for g in gastos)
        self.lbl_total.setText(f"Total: S/ {total:.2f}")
        
        # Llenar tabla
        self.table.setRowCount(0)
        for row, gasto in enumerate(gastos):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(gasto[0])))
            self.table.setItem(row, 1, QTableWidgetItem(gasto[1]))
            self.table.setItem(row, 2, QTableWidgetItem(gasto[2].title()))
            self.table.setItem(row, 3, QTableWidgetItem(gasto[5]))
            self.table.setItem(row, 4, QTableWidgetItem(gasto[4]))
            
            monto_item = QTableWidgetItem(f"S/ {gasto[3]:.2f}")
            monto_item.setForeground(Qt.GlobalColor.darkRed)
            monto_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, monto_item)
    
    def nuevo_gasto(self):
        """Abre diálogo para registrar gasto"""
        dialog = GastoDialog(self, self.gasto_service)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.gasto_registrado.emit()


class GastoDialog(QDialog):
    """Diálogo para registrar gastos"""
    
    def __init__(self, parent, gasto_service):
        super().__init__(parent)
        self.gasto_service = gasto_service
        
        self.setWindowTitle("Registrar Gasto")
        self.setFixedSize(400, 350)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura UI del diálogo"""
        layout = QVBoxLayout(self)
        
        # Tipo de gasto
        layout.addWidget(QLabel("Tipo de Gasto:"))
        self.combo_tipo = QComboBox()
        tipos = self.gasto_service.get_tipos_gasto()
        for tipo in tipos:
            self.combo_tipo.addItem(tipo.title(), tipo)
        layout.addWidget(self.combo_tipo)
        
        # Monto
        layout.addWidget(QLabel("Monto (S/):"))
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setMaximum(999999.99)
        self.spin_monto.setDecimals(2)
        layout.addWidget(self.spin_monto)
        
        # Método de pago
        layout.addWidget(QLabel("Método de Pago:"))
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Efectivo", "Yape", "Plin", "POS/Banco"])
        layout.addWidget(self.combo_metodo)
        
        # Descripción
        layout.addWidget(QLabel("Descripción:"))
        self.input_descripcion = QLineEdit()
        layout.addWidget(self.input_descripcion)
        
        # Glosa (opcional)
        layout.addWidget(QLabel("Glosa (opcional):"))
        self.text_glosa = QTextEdit()
        self.text_glosa.setMaximumHeight(60)
        layout.addWidget(self.text_glosa)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)
    
    def guardar(self):
        """Guarda el gasto"""
        tipo = self.combo_tipo.currentData()
        monto = self.spin_monto.value()
        metodo_map = {
            "Efectivo": "efectivo",
            "Yape": "yape",
            "Plin": "plin",
            "POS/Banco": "pos_banco"
        }
        metodo = metodo_map[self.combo_metodo.currentText()]
        descripcion = self.input_descripcion.text().strip()
        glosa = self.text_glosa.toPlainText().strip() or None
        
        if not descripcion:
            QMessageBox.warning(self, "Error", "La descripción es obligatoria")
            return
        
        if monto <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
            return
        
        result = self.gasto_service.registrar_gasto(
            tipo, monto, metodo, descripcion, None, None, glosa
        )
        
        if result['success']:
            QMessageBox.information(self, "Éxito", "Gasto registrado exitosamente")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", result['message'])
