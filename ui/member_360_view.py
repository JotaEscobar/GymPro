# -*- coding: utf-8 -*-
"""
Vista 360 del miembro - VERSIÓN COMPLETA RESTAURADA
Incluye: Perfil, Pagos, Mediciones, Asistencias, Notas, Clases
"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor
from datetime import datetime
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np
import sqlite3
from services.attendance_service import AttendanceService
from services.member_service import MemberService
from services.payment_service import PaymentService
from models.payment_model import PaymentModel
from core.config import Config
from services.note_service import NoteService
from services.category_service import CategoryService
from services.benefit_service import BenefitService
from ui.benefits_tooltip import BenefitsTooltip

class MedidasChartWidget(QWidget):
    """Widget para gráficos de mediciones corporales"""
    punto_clickeado = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 🔥 FONDO OSCURO PARA EVITAR CUADRO BLANCO
        self.setStyleSheet("background-color: #0f172a;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(figsize=(5, 2.4), facecolor="#0f172a")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #0f172a;")
        
        self.layout.addWidget(self.canvas)
        self.setMinimumHeight(200)
        
        self.mediciones = []
        self.canvas.mpl_connect("button_press_event", self._on_click)

        self.category_service = CategoryService()
        self.benefit_service = BenefitService()
        self.current_categoria_id = None        

    def actualizar_grafico_multiple(self, data, claves, label):
        """Actualiza gráfico con múltiples métricas"""
        self.mediciones = data
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'Sin mediciones registradas\nRegistra tu primera medición', 
                   ha='center', va='center', color='#9ca3af', fontsize=11)
            ax.set_facecolor("#0f172a")
            self.canvas.draw()
            return
        
        fechas = [datetime.strptime(m["fecha"], Config.DATE_FORMAT) for m in data]
        colores = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        
        for i, clave in enumerate(claves):
            vals = [m.get(clave) for m in data]
            vals_limpios = [v for v in vals if v is not None]
            
            if vals_limpios:
                fechas_validas = [fechas[j] for j, v in enumerate(vals) if v is not None]
                ax.plot(fechas_validas, vals_limpios, 
                       marker='o', markersize=6, markerfacecolor='white',
                       color=colores[i % len(colores)],
                       label=clave.capitalize(), linewidth=2.5)
                
                # Anotar valores
                for x, y in zip(fechas_validas, vals_limpios):
                    ax.annotate(f"{y:.1f}", (x, y),
                               textcoords="offset points", xytext=(0, -12),
                               ha='center', fontsize=7, color='white')
        
        ax.set_facecolor("#0f172a")
        ax.tick_params(colors="#e5e7eb", labelsize=8)
        ax.spines['bottom'].set_color('#334155')
        ax.spines['left'].set_color('#334155')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(f"Evolución de {label}", color="#e5e7eb", weight='bold', fontsize=10)
        ax.set_xlabel("Fecha", color="#e5e7eb", fontsize=9)
        ax.set_ylabel("Valor", color="#e5e7eb", fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.3, color='#475569')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.legend(loc='upper left', fontsize=8, facecolor='#1e293b', edgecolor='#334155', labelcolor='#e5e7eb')
        
        self.figure.tight_layout()
        self.canvas.draw()

    def _on_click(self, event):
        """Detecta clicks en puntos del gráfico"""
        if not self.mediciones or not event.xdata:
            return
        
        click_fecha = mdates.num2date(event.xdata).date()
        fechas = [datetime.strptime(m["fecha"], Config.DATE_FORMAT).date() for m in self.mediciones]
        distancias = [abs((f - click_fecha).days) for f in fechas]
        idx = np.argmin(distancias)
        
        if distancias[idx] <= 5:  # Solo si está cerca
            self.punto_clickeado.emit(self.mediciones[idx])


class Member360Dialog(QDialog):
    """Vista 360 completa del miembro"""
    
    asistencia_registrada = pyqtSignal()
    pago_registrado = pyqtSignal()

    def __init__(self, member_data, parent=None):
        super().__init__(parent)
        self.member = member_data or {}
        self.setWindowTitle("Miembro 360")
        self.setModal(True)
        self.setMinimumSize(1000, 680)
        self.edit_mode = False
        self.mediciones_data = []
        self.chips = []
        self.note_service = NoteService()
        self.category_service = CategoryService()
        self.benefit_service = BenefitService()
        self._apply_dark_style()
        self._build_header()
        self._build_tabs()

        root = QVBoxLayout()
        root.addLayout(self.header_layout)
        root.addWidget(self.tabs)
        self.setLayout(root)

    def _apply_dark_style(self):
        """Estilos dark UI"""
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: #e2e8f0; }
            QLabel { color: #e2e8f0; }
            QLineEdit, QTextEdit, QDateEdit, QComboBox {
                background-color: #111827; color: #e5e7eb;
                border: 1px solid #334155; padding: 6px; border-radius: 6px;
            }
            QLineEdit:read-only { background-color: #1e293b; color: #94a3b8; }
            QTabWidget::pane { border: 1px solid #334155; border-radius: 8px; margin-top: -1px; }
            QTabBar::tab { 
                background: #0b1220; color: #cbd5e1; padding: 10px 16px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: #1f2937; color: #ffffff; font-weight: bold; }
            QPushButton {
                background-color: #1f2937; color: #e5e7eb;
                border: 1px solid #374151; padding: 8px 12px;
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #374151; }
            QPushButton[destructive="true"] { background-color: #b91c1c; color: white; }
            QPushButton:checked { background-color: #3b82f6; border: 2px solid #60a5fa; }
            QTableWidget {
                background-color: #0b1220; color: #e5e7eb;
                gridline-color: #334155; border: 1px solid #334155; border-radius: 6px;
            }
            QHeaderView::section { background-color: #111827; color: #e5e7eb; padding: 6px; border: 0px; }
        """)

    def _build_header(self):
        """Cabecera con avatar circular e info completa"""
        self.header_layout = QHBoxLayout()
        
        # 🔥 AVATAR CIRCULAR
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(90, 90)
        self.avatar_label.setStyleSheet("border-radius: 45px; background-color: #1e293b;")
        self.avatar_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.avatar_label.mousePressEvent = self._avatar_menu
        self._refresh_avatar()

        # Info del miembro
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(self.member.get('nombre', 'Miembro'))
        name_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #e5e7eb;")
        
        # 🔥 CLIENTE DESDE (formato dd/mm/yyyy)
        fecha_registro = self.member.get('fecha_registro', datetime.now().strftime(Config.DATE_FORMAT))
        try:
            fecha_obj = datetime.strptime(fecha_registro, Config.DATE_FORMAT)
            fecha_formateada = fecha_obj.strftime(Config.DISPLAY_DATE_FORMAT)
        except:
            fecha_formateada = fecha_registro
        
        since_label = QLabel(f"Cliente desde {fecha_formateada}")
        since_label.setStyleSheet("color: #9ca3af; font-style: italic; font-size: 10pt;")
        
        # 🔥 ESTADO Y CATEGORÍA
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(10)

        # Estado: Determinar Activo/Inactivo basado en vencimiento
        state_text = self.member.get('estado', 'Inactivo')

        # Lógica: Si tiene "Válida" o "Activo" → Activo, sino → Inactivo
        if 'Válida' in state_text or 'Activo' in state_text:
            estado_display = "Activo"
            estado_color = "#22c55e"  # Verde
        else:
            estado_display = "Inactivo"
            estado_color = "#ef4444"  # Rojo

        state_badge = QLabel(estado_display)
        state_badge.setStyleSheet(f"""
            color: {estado_color}; 
            font-weight: bold;
            font-size: 11pt;
        """)

        # Categoría desde BD real
        self.current_categoria_id = self._get_member_categoria()

        if self.current_categoria_id:
            categoria_obj = self.category_service.get_category_by_id(self.current_categoria_id)
            if categoria_obj:
                categoria_badge = QLabel(f"🏷️ {categoria_obj['nombre']}")
                categoria_badge.setStyleSheet(f"""
                    background: {categoria_obj['color_hex']}22;
                    color: {categoria_obj['color_hex']};
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-weight: 600;
                    border: 1px solid {categoria_obj['color_hex']};
                """)
                
                # Icono info para tooltip
                self.info_btn = QPushButton("i")  # 🔥 Usar "i" simple en lugar de ⓘ
                self.info_btn.setFixedSize(24, 24)
                self.info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                self.info_btn.setStyleSheet("""
                    QPushButton {
                        background: #fbbf24;     /* Fondo amarillo brillante */
                        border: 2px solid #f59e0b;  /* Borde naranja */
                        border-radius: 12px;     /* Circular */
                        color: #000000;          /* Texto negro */
                        font-size: 14px;
                        font-weight: bold;
                        font-family: Arial, sans-serif;
                    }
                    QPushButton:hover {
                        background: #fde047;     /* Amarillo más brillante al hover */
                        border-color: #fbbf24;
                    }
                """)
                self.info_btn.clicked.connect(self._show_benefits_tooltip)
                
                badges_layout.addWidget(state_badge)
                badges_layout.addWidget(categoria_badge)
                badges_layout.addWidget(self.info_btn)
            else:
                # Sin categoría asignada
                badges_layout.addWidget(state_badge)
        else:
            # Sin categoría
            badges_layout.addWidget(state_badge)

        badges_layout.addStretch()

        info_layout.addWidget(name_label)
        info_layout.addWidget(since_label)
        info_layout.addLayout(badges_layout)
        
        self.header_layout.addWidget(self.avatar_label)
        self.header_layout.addSpacing(16)
        self.header_layout.addLayout(info_layout)
        self.header_layout.addStretch()

    def _build_tabs(self):
        """Construye todas las pestañas"""
        self.tabs = QTabWidget()
        self.tabs.addTab(self._perfil_widget(), "👤 Perfil")
        self.tabs.addTab(self._pagos_widget(), "💳 Pagos")
        self.tabs.addTab(self._mediciones_widget(), "📊 Mediciones")
        self.tabs.addTab(self._asistencias_widget(), "🏃 Asistencias")
        self.tabs.addTab(self._clases_widget(), "🧘 Clases")
        self.tabs.addTab(self._notas_widget(), "📝 Notas")
        # 🔥 Pestaña de beneficios eliminada - ahora se muestra en modal

    def _get_member_categoria(self):
        """
        Obtiene la categoría actual del miembro basado en su membresía activa.
        
        Returns:
            int: ID de categoría o None
        """
        try:
            miembro_id = self.member.get('id')
            if not miembro_id:
                return None
            
            # Obtener última membresía activa del miembro
            from models.payment_model import PaymentModel
            from models.plan_model import PlanModel
            
            payment_model = PaymentModel()
            plan_model = PlanModel()
            
            # Obtener pagos del miembro
            payments = payment_model.get_payments_by_member_id(miembro_id)
            
            if not payments:
                return None
            
            # Buscar el último pago activo
            for payment in payments:
                fecha_pago, plan_nombre, monto, fecha_vencimiento = payment
                
                # Verificar si está activo (fecha_vencimiento >= hoy)
                from datetime import date
                
                if isinstance(fecha_vencimiento, str):
                    fecha_venc_obj = datetime.strptime(fecha_vencimiento, Config.DATE_FORMAT).date()
                else:
                    fecha_venc_obj = fecha_vencimiento
                
                if fecha_venc_obj >= date.today():
                    # Obtener plan por nombre y su categoría
                    planes = plan_model.get_all_plans(include_inactive=True)
                    for plan in planes:
                        if plan[1] == plan_nombre:  # plan[1] es nombre
                            if plan[9]:  # plan[9] es categoria_id
                                return plan[9]
            
            return None
        
        except Exception as e:
            from core.logger import logger
            logger.error(f"Error al obtener categoría del miembro: {e}")
            return None
        
    def _show_benefits_tooltip(self):
        """Muestra el tooltip con TODOS los beneficios completos"""
        miembro_id = self.member.get('id')
        if not miembro_id:
            return
        
        # 🔥 Tooltip optimizado - sin parámetros extra
        tooltip = BenefitsTooltip(
            parent=self,
            miembro_id=miembro_id
        )
        
        # Mostrar tooltip cerca del botón info
        tooltip.show_near_widget(self.info_btn)

    # ========== TAB: PERFIL ==========
    def _perfil_widget(self):
        """Pestaña de perfil con botones Editar/Eliminar"""
        w = QWidget()
        layout = QVBoxLayout(w)
        form = QFormLayout()
        
        self.inp_codigo = QLineEdit(self.member.get('codigo', ''))
        self.inp_codigo.setReadOnly(True)
        self.inp_nombre = QLineEdit(self.member.get('nombre', ''))
        self.inp_nombre.setReadOnly(True)
        self.inp_dni = QLineEdit(self.member.get('dni', ''))
        self.inp_dni.setReadOnly(True)
        self.inp_contacto = QLineEdit(self.member.get('contacto', ''))
        self.inp_contacto.setReadOnly(True)
        self.inp_email = QLineEdit(self.member.get('email', ''))
        self.inp_email.setReadOnly(True)
        self.inp_direccion = QLineEdit(self.member.get('direccion', ''))
        self.inp_direccion.setReadOnly(True)
        
        form.addRow("Código:", self.inp_codigo)
        form.addRow("Nombre:", self.inp_nombre)
        form.addRow("DNI:", self.inp_dni)
        form.addRow("Contacto:", self.inp_contacto)
        form.addRow("Email:", self.inp_email)
        form.addRow("Dirección:", self.inp_direccion)
        
        # 🔥 BOTONES: EDITAR / GUARDAR / ELIMINAR
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_editar = QPushButton("✏️ Editar datos")
        self.btn_editar.clicked.connect(self._toggle_edit_mode)
        
        self.btn_guardar = QPushButton("💾 Guardar cambios")
        self.btn_guardar.clicked.connect(self._save_profile)
        self.btn_guardar.setVisible(False)
        
        btn_eliminar = QPushButton("🗑️ Eliminar miembro")
        btn_eliminar.setProperty("destructive", True)
        btn_eliminar.clicked.connect(self._delete_member)
        
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(btn_eliminar)
        
        layout.addLayout(form)
        layout.addSpacing(10)
        layout.addLayout(btn_layout)
        layout.addStretch()
        return w

    def _toggle_edit_mode(self):
        """Activa/desactiva modo edición"""
        self.edit_mode = not self.edit_mode
        
        campos = [self.inp_nombre, self.inp_dni, self.inp_contacto, self.inp_email, self.inp_direccion]
        for campo in campos:
            campo.setReadOnly(not self.edit_mode)
        
        self.btn_editar.setVisible(not self.edit_mode)
        self.btn_guardar.setVisible(self.edit_mode)

    def _save_profile(self):
        """Guarda cambios del perfil"""
        MemberService().update_member_profile(
            self.inp_codigo.text().strip(),
            self.inp_nombre.text().strip(),
            self.inp_dni.text().strip(),
            self.inp_contacto.text().strip(),
            self.inp_email.text().strip(),
            self.inp_direccion.text().strip()
        )
        QMessageBox.information(self, "Perfil", "Cambios guardados correctamente")
        self._toggle_edit_mode()

    def _delete_member(self):
        """Elimina miembro con confirmación"""
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar a {self.member.get('nombre')}?\n\n"
            "Esta acción moverá el registro a la tabla de respaldo.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            MemberService().delete_member(self.inp_codigo.text().strip())
            QMessageBox.information(self, "Eliminado", "Miembro eliminado correctamente")
            self.accept()

    # ========== TAB: PAGOS ==========
    def _pagos_widget(self):
        """Pestaña de pagos con filtros y extorno"""
        w = QWidget()
        layout = QVBoxLayout(w)
        
        # Filtros
        filt = QHBoxLayout()
        filt.addWidget(QLabel("Desde:"))
        
        # 🔥 CALENDARIOS ACTIVADOS
        self.pagos_desde = QDateEdit()
        self.pagos_desde.setDate(QDate.currentDate().addMonths(-3))
        self.pagos_desde.setCalendarPopup(True)
        self.pagos_desde.setDisplayFormat("dd/MM/yyyy")
        
        filt.addWidget(self.pagos_desde)
        filt.addWidget(QLabel("Hasta:"))
        
        self.pagos_hasta = QDateEdit()
        self.pagos_hasta.setDate(QDate.currentDate())
        self.pagos_hasta.setCalendarPopup(True)
        self.pagos_hasta.setDisplayFormat("dd/MM/yyyy")
        
        filt.addWidget(self.pagos_hasta)
        filt.addStretch()
        
        btn_filtrar = QPushButton("🔎 Filtrar")
        btn_filtrar.clicked.connect(self._filter_pagos)
        
        btn_nuevo = QPushButton("➕ Nuevo pago")
        btn_nuevo.clicked.connect(self._new_payment)
        
        btn_extornar = QPushButton("🗑️ Extornar último")
        btn_extornar.setProperty("destructive", True)
        btn_extornar.clicked.connect(self._extornar_ultimo_pago)
        
        filt.addWidget(btn_filtrar)
        filt.addWidget(btn_nuevo)
        filt.addWidget(btn_extornar)
        
        # 🔥 TABLA CON SELECCIÓN DE FILA COMPLETA
        self.pagos_table = QTableWidget(0, 4)
        self.pagos_table.setHorizontalHeaderLabels(["Fecha", "Plan", "Monto", "Vence"])
        self.pagos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pagos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pagos_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addLayout(filt)
        layout.addWidget(self.pagos_table)
        self._load_payment_history()
        return w

    def _new_payment(self):
        """Abre diálogo de nuevo pago"""
        from ui.payment_dialog import PaymentDialog
        dlg = PaymentDialog(
            self.member.get('id'), 
            self.member.get('nombre'),
            self.member.get('dni'), 
            self.member.get('codigo'), 
            self
        )
        if dlg.table_history:
            dlg.table_history.hide()
        
        dlg.pago_registrado.connect(self._load_payment_history)
        dlg.pago_registrado.connect(self.pago_registrado.emit)
        dlg.exec()

    def _load_payment_history(self):
        """Carga historial de pagos"""
        pagos = PaymentService().get_payments_by_codigo(self.member.get('codigo'))
        self.pagos_table.setRowCount(0)
        
        for row, (fecha, plan, monto, vence) in enumerate(pagos):
            self.pagos_table.insertRow(row)
            self.pagos_table.setItem(row, 0, QTableWidgetItem(fecha))
            self.pagos_table.setItem(row, 1, QTableWidgetItem(plan))
            self.pagos_table.setItem(row, 2, QTableWidgetItem(f"S/ {monto:.2f}"))
            
            item_vence = QTableWidgetItem(vence)
            try:
                if datetime.strptime(vence, Config.DATE_FORMAT).date() < datetime.now().date():
                    item_vence.setForeground(QColor("#ef4444"))
                else:
                    item_vence.setForeground(QColor("#22c55e"))
            except:
                pass
            self.pagos_table.setItem(row, 3, item_vence)

    def _filter_pagos(self):
        """Filtra pagos por rango de fechas"""
        desde = self.pagos_desde.date().toString("yyyy-MM-dd")
        hasta = self.pagos_hasta.date().toString("yyyy-MM-dd")
        pagos = PaymentService().get_payments_by_codigo(self.member.get('codigo'), desde, hasta)
        
        self.pagos_table.setRowCount(0)
        for row, (fecha, plan, monto, vence) in enumerate(pagos):
            self.pagos_table.insertRow(row)
            self.pagos_table.setItem(row, 0, QTableWidgetItem(fecha))
            self.pagos_table.setItem(row, 1, QTableWidgetItem(plan))
            self.pagos_table.setItem(row, 2, QTableWidgetItem(f"S/ {monto:.2f}"))
            self.pagos_table.setItem(row, 3, QTableWidgetItem(vence))

    def _extornar_ultimo_pago(self):
        """🔥 EXTORNA EL PAGO MÁS RECIENTE (primero de la lista ordenada DESC)"""
        pagos = PaymentService().get_payments_by_codigo(self.member.get('codigo'))
        
        if not pagos:
            QMessageBox.information(self, "Sin pagos", "No hay pagos registrados")
            return
        
        # El primer elemento es el más reciente (ORDER BY DESC)
        fecha, plan, monto, _ = pagos[0]
        
        reply = QMessageBox.question(
            self, "Extornar pago",
            f"¿Extornar el último pago realizado?\n\n"
            f"Plan: {plan}\nMonto: S/ {monto:.2f}\nFecha: {fecha}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            id_pago = PaymentService().get_payment_id_by_fecha_plan_monto(
                self.member.get('codigo'), fecha, plan, monto
            )
            if id_pago:
                resultado = PaymentService().delete_payment_by_id(id_pago)
                if resultado.get("success"):
                    QMessageBox.information(self, "Extornado", "Pago eliminado correctamente")
                    self._load_payment_history()
                    self.pago_registrado.emit()
                else:
                    QMessageBox.critical(self, "Error", resultado.get("message"))

    # ========== TAB: MEDICIONES ==========
    def _mediciones_widget(self):
        """Pestaña de mediciones con KPIs, gráfico y formulario completo"""
        w = QWidget()
        layout = QVBoxLayout(w)
        
        # 🔥 KPIS - TARJETAS RESUMEN
        self._cargar_mediciones()
        
        kpis_layout = QHBoxLayout()
        kpis_layout.setSpacing(12)
        
        if self.mediciones_data:
            actual = self.mediciones_data[-1]
            anterior = self.mediciones_data[-2] if len(self.mediciones_data) > 1 else {}
        else:
            actual = {}
            anterior = {}
        
        def crear_kpi(titulo, valor_actual, valor_anterior, unidad=""):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1e293b; 
                    border-radius: 8px;
                }
            """)
            card.setMinimumHeight(85)  # 🔥 ALTURA MÍNIMA PARA VER TODO
            card.setMaximumHeight(100)
            
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(4)
            card_layout.setContentsMargins(12, 10, 12, 10)
            
            # Título
            lbl_titulo = QLabel(titulo)
            lbl_titulo.setStyleSheet("color: #9ca3af; font-size: 10pt; font-weight: bold;")
            lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Valor con flecha
            if valor_actual is not None:
                valor_str = f"{valor_actual:.1f}{unidad}"
            else:
                valor_str = "—"
            
            # 🔥 FLECHA DE TENDENCIA
            flecha = ""
            color_flecha = ""
            if valor_actual is not None and valor_anterior is not None:
                diferencia = valor_actual - valor_anterior
                if diferencia > 0:
                    flecha = " ▲"
                    color_flecha = "#22c55e"  # Verde
                elif diferencia < 0:
                    flecha = " ▼"
                    color_flecha = "#ef4444"  # Rojo
                else:
                    flecha = " ━"
                    color_flecha = "#6b7280"  # Gris
            
            # Construir HTML del valor
            if flecha:
                valor_html = f"{valor_str} <span style='color:{color_flecha}; font-size: 14pt;'>{flecha}</span>"
            else:
                valor_html = valor_str
            
            lbl_valor = QLabel(valor_html)
            lbl_valor.setTextFormat(Qt.TextFormat.RichText)
            lbl_valor.setStyleSheet("color: #e5e7eb; font-size: 20pt; font-weight: bold;")
            lbl_valor.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            card_layout.addWidget(lbl_titulo)
            card_layout.addWidget(lbl_valor)
            card_layout.addStretch()
            
            return card

        # 🔥 CREAR LOS KPIs (esto va después de cargar mediciones)
        if self.mediciones_data:
            actual = self.mediciones_data[-1]
            anterior = self.mediciones_data[-2] if len(self.mediciones_data) > 1 else {}
        else:
            actual = {}
            anterior = {}

        kpis_layout.addWidget(crear_kpi("Peso", actual.get('peso'), anterior.get('peso'), " kg"))
        kpis_layout.addWidget(crear_kpi("% Grasa", actual.get('grasa'), anterior.get('grasa'), "%"))
        kpis_layout.addWidget(crear_kpi("IMC", actual.get('imc'), anterior.get('imc'), ""))
                
        layout.addLayout(kpis_layout)
        layout.addSpacing(10)
        
        # 🔥 CHIPS CON ESTILO VISUAL DE SELECCIÓN
        chip_bar = QHBoxLayout()
        
        grupos = [
            ("Generales", ["peso", "grasa", "imc"]),
            ("Superiores", ["pecho", "hombros", "brazo"]),
            ("Inferiores", ["cintura", "cadera", "muslo"])
        ]
        
        self.chips = []
        for label, claves in grupos:
            chip = QPushButton(label)
            chip.setCheckable(True)
            chip.setFixedHeight(32)
            chip.clicked.connect(lambda checked, c=claves, l=label, b=chip: self._seleccionar_chip(c, l, b))
            chip_bar.addWidget(chip)
            self.chips.append((chip, claves, label))
        
        btn_nueva = QPushButton("➕ Nueva medición")
        btn_nueva.clicked.connect(self._new_measurement)
        chip_bar.addStretch()
        chip_bar.addWidget(btn_nueva)
        
        layout.addLayout(chip_bar)
        
        # Gráfico
        self.chart_widget = MedidasChartWidget()
        self.chart_widget.punto_clickeado.connect(self._mostrar_ficha_medicion)
        layout.addWidget(self.chart_widget)
        
        # Activar primer chip por defecto
        if self.chips:
            self.chips[0][0].setChecked(True)
            self._seleccionar_chip(self.chips[0][1], self.chips[0][2], self.chips[0][0])
        
        return w

    def _cargar_mediciones(self):
        """Carga mediciones desde BD"""
        conn = sqlite3.connect("gym_db.sqlite")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha_medicion, peso, talla, grasa_corporal, pecho, hombros,
                   cintura, cadera, biceps, antebrazo, muslo, gemelos, cuello, comentarios
            FROM measurements WHERE miembro_id = ? ORDER BY fecha_medicion ASC
        """, (self.member.get('id'),))
        rows = cursor.fetchall()
        conn.close()
        
        self.mediciones_data = []
        for r in rows:
            imc = round(r[2]/(r[3]*r[3]), 2) if r[2] and r[3] else None
            self.mediciones_data.append({
                "id": r[0], "fecha": r[1], "peso": r[2], "grasa": r[4], "imc": imc,
                "pecho": r[5], "hombros": r[6], "cintura": r[7], "cadera": r[8],
                "brazo": r[9], "antebrazo": r[10], "muslo": r[11], 
                "pantorrilla": r[12], "cuello": r[13], "comentarios": r[14]
            })

    def _seleccionar_chip(self, claves, label, boton):
        """Selecciona chip y actualiza gráfico"""
        for chip, _, _ in self.chips:
            chip.setChecked(False)
        boton.setChecked(True)
        self.chart_widget.actualizar_grafico_multiple(self.mediciones_data, claves, label)

    def _mostrar_ficha_medicion(self, medicion):
        """🔥 POPUP COMPLETO CON DETALLES Y BOTÓN ELIMINAR"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📊 Medición del {medicion['fecha']}")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet("background-color: #1e293b; color: #e5e7eb;")
        
        layout = QVBoxLayout(dialog)
        
        # Grid de métricas
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(8)
        
        metricas = [
            ("Peso", f"{medicion.get('peso','—')} kg"),
            ("% Grasa", f"{medicion.get('grasa','—')} %"),
            ("IMC", f"{medicion.get('imc','—')}"),
            ("Pecho", f"{medicion.get('pecho','—')} cm"),
            ("Cintura", f"{medicion.get('cintura','—')} cm"),
            ("Cadera", f"{medicion.get('cadera','—')} cm"),
            ("Brazo", f"{medicion.get('brazo','—')} cm"),
            ("Muslo", f"{medicion.get('muslo','—')} cm"),
            ("Cuello", f"{medicion.get('cuello','—')} cm")
        ]
        
        for i, (nombre, valor) in enumerate(metricas):
            row = i // 2
            col = (i % 2) * 2
            
            lbl_nombre = QLabel(f"{nombre}:")
            lbl_nombre.setStyleSheet("color: #9ca3af;")
            lbl_valor = QLabel(valor)
            lbl_valor.setStyleSheet("font-weight: bold; color: #e5e7eb;")
            
            grid.addWidget(lbl_nombre, row, col)
            grid.addWidget(lbl_valor, row, col + 1)
        
        layout.addLayout(grid)
        
        # Comentarios
        if medicion.get("comentarios"):
            layout.addSpacing(10)
            lbl_coment = QLabel(f"💬 Comentario: {medicion['comentarios']}")
            lbl_coment.setStyleSheet("font-style: italic; color: #9ca3af;")
            lbl_coment.setWordWrap(True)
            layout.addWidget(lbl_coment)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_eliminar = QPushButton("🗑️ Eliminar medición")
        btn_eliminar.setStyleSheet("background-color: #dc2626; color: white;")
        btn_eliminar.clicked.connect(lambda: self._eliminar_medicion(medicion, dialog))
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(dialog.close)
        
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def _eliminar_medicion(self, medicion, dialog):
        """Elimina una medición"""
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar la medición del {medicion['fecha']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("gym_db.sqlite")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM measurements WHERE id = ?", (medicion["id"],))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Eliminada", "Medición eliminada correctamente")
            dialog.close()
            self._cargar_mediciones()
            
            # Refrescar gráfico con chip activo
            for chip, claves, label in self.chips:
                if chip.isChecked():
                    self._seleccionar_chip(claves, label, chip)
                    break

    def _new_measurement(self):
        """🔥 FORMULARIO COMPLETO DE NUEVA MEDICIÓN"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Nueva medición")
        dialog.setMinimumWidth(550)
        dialog.setStyleSheet("background-color: #1e293b; color: #e5e7eb;")
        
        layout = QVBoxLayout(dialog)
        
        # Grid de campos
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        
        # Fecha
        grid.addWidget(QLabel("Fecha:"), 0, 0)
        fecha = QDateEdit()
        fecha.setCalendarPopup(True)
        fecha.setDate(QDate.currentDate())
        fecha.setDisplayFormat("dd/MM/yyyy")
        grid.addWidget(fecha, 0, 1)
        
        # Campos numéricos
        campos = {}
        campos_config = [
            ("Peso (kg):", "peso", 0, 2),
            ("Talla (m):", "talla", 0, 4),
            ("% Grasa:", "grasa", 1, 0),
            ("Pecho (cm):", "pecho", 1, 2),
            ("Hombros (cm):", "hombros", 1, 4),
            ("Cintura (cm):", "cintura", 2, 0),
            ("Cadera (cm):", "cadera", 2, 2),
            ("Bíceps (cm):", "biceps", 2, 4),
            ("Antebrazo (cm):", "antebrazo", 3, 0),
            ("Muslo (cm):", "muslo", 3, 2),
            ("Gemelos (cm):", "gemelos", 3, 4),
            ("Cuello (cm):", "cuello", 4, 0)
        ]
        
        for label_text, key, row, col in campos_config:
            grid.addWidget(QLabel(label_text), row, col)
            inp = QLineEdit()
            inp.setFixedWidth(80)
            inp.setPlaceholderText("0.0")
            campos[key] = inp
            grid.addWidget(inp, row, col + 1)
        
        # Resistencia
        grid.addWidget(QLabel("Resistencia:"), 4, 2)
        resistencia = QComboBox()
        resistencia.addItems(["", "Baja", "Media", "Alta"])
        grid.addWidget(resistencia, 4, 3)
        
        layout.addLayout(grid)
        
        # IMC calculado
        lbl_imc = QLabel("IMC: —")
        lbl_imc.setStyleSheet("font-weight: bold; color: #3b82f6;")
        layout.addWidget(lbl_imc)
        
        def calcular_imc():
            try:
                p = float(campos['peso'].text())
                t = float(campos['talla'].text())
                if t > 0:
                    imc = p / (t * t)
                    lbl_imc.setText(f"IMC: {imc:.2f}")
            except:
                lbl_imc.setText("IMC: —")
        
        campos['peso'].textChanged.connect(calcular_imc)
        campos['talla'].textChanged.connect(calcular_imc)
        
        # Comentarios
        layout.addSpacing(8)
        lbl_comentarios = QLabel("Comentarios:")
        lbl_comentarios.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_comentarios)

        comentarios = QTextEdit()
        comentarios.setFixedHeight(60)
        comentarios.setPlaceholderText("Notas adicionales sobre esta medición...")
        comentarios.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                border: 2px solid #475569;
                border-radius: 6px;
                padding: 8px;
                color: #e5e7eb;
                font-size: 10pt;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        layout.addWidget(comentarios)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(dialog.reject)
        
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.setStyleSheet("background-color: #10b981; color: white;")
        btn_guardar.clicked.connect(lambda: self._guardar_medicion(fecha, campos, resistencia, comentarios, dialog))
        
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_guardar)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def _guardar_medicion(self, fecha, campos, resistencia, comentarios, dialog):
        """Guarda nueva medición en BD"""
        if not campos['peso'].text() or not campos['talla'].text():
            QMessageBox.warning(self, "Campos requeridos", "Peso y Talla son obligatorios")
            return
        
        def to_float(val):
            try: return float(val.text()) if val.text() else None
            except: return None
        
        conn = sqlite3.connect("gym_db.sqlite")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO measurements (
                miembro_id, fecha_medicion, peso, talla, grasa_corporal,
                resistencia_fisica, pecho, hombros, cintura, cadera, biceps,
                antebrazo, muslo, gemelos, cuello, comentarios
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.member.get('id'),
            fecha.date().toString("yyyy-MM-dd"),
            to_float(campos['peso']),
            to_float(campos['talla']),
            to_float(campos['grasa']),
            resistencia.currentText(),
            to_float(campos['pecho']),
            to_float(campos['hombros']),
            to_float(campos['cintura']),
            to_float(campos['cadera']),
            to_float(campos['biceps']),
            to_float(campos['antebrazo']),
            to_float(campos['muslo']),
            to_float(campos['gemelos']),
            to_float(campos['cuello']),
            comentarios.toPlainText()
        ))
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Guardado", "Medición registrada correctamente")
        dialog.accept()
        self._cargar_mediciones()
        
        # Refrescar gráfico
        for chip, claves, label in self.chips:
            if chip.isChecked():
                self._seleccionar_chip(claves, label, chip)
                break

    # ========== TAB: ASISTENCIAS ==========
    def _asistencias_widget(self):
        """Pestaña de asistencias con filtros funcionales"""
        w = QWidget()
        layout = QVBoxLayout(w)
        
        filt = QHBoxLayout()
        filt.addWidget(QLabel("Desde:"))
        
        # Calendarios
        self.asis_desde = QDateEdit()
        self.asis_desde.setDate(QDate.currentDate().addMonths(-1))
        self.asis_desde.setCalendarPopup(True)
        self.asis_desde.setDisplayFormat("dd/MM/yyyy")
        
        filt.addWidget(self.asis_desde)
        filt.addWidget(QLabel("Hasta:"))
        
        self.asis_hasta = QDateEdit()
        self.asis_hasta.setDate(QDate.currentDate())
        self.asis_hasta.setCalendarPopup(True)
        self.asis_hasta.setDisplayFormat("dd/MM/yyyy")
        
        filt.addWidget(self.asis_hasta)
        filt.addStretch()
        
        btn_filtrar = QPushButton("🔎 Filtrar")
        btn_filtrar.clicked.connect(self._filter_asistencias)
        
        btn_marcar = QPushButton("✅ Marcar entrada")
        btn_marcar.clicked.connect(self._mark_attendance_here)
        
        filt.addWidget(btn_filtrar)
        filt.addWidget(btn_marcar)
        
        # Tabla con selección de fila
        self.asis_table = QTableWidget(0, 2)
        self.asis_table.setHorizontalHeaderLabels(["Fecha/Hora", "Plan"])
        self.asis_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.asis_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addLayout(filt)
        layout.addWidget(self.asis_table)
        
        # 🔥 CARGAR HISTORIAL INICIAL AL CREAR LA PESTAÑA
        self._filter_asistencias()
        
        return w

    def _filter_asistencias(self):
        """Filtra asistencias por rango de fechas"""
        desde = self.asis_desde.date().toString("yyyy-MM-dd")
        hasta = self.asis_hasta.date().toString("yyyy-MM-dd")
        
        try:
            registros = AttendanceService().get_log_by_member_and_range(
                self.member.get("id"), desde, hasta
            )
            self.asis_table.setRowCount(0)
            for row, (fecha_hora, plan) in enumerate(registros):
                self.asis_table.insertRow(row)
                self.asis_table.setItem(row, 0, QTableWidgetItem(str(fecha_hora)))
                self.asis_table.setItem(row, 1, QTableWidgetItem(str(plan)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo filtrar:\n{str(e)}")

    def _mark_attendance_here(self):
        """Registra asistencia desde vista 360"""
        try:
            resultado = AttendanceService().register_check_in(self.member.get("codigo"))
            
            if resultado.get('status') == 'Éxito':
                QMessageBox.information(self, "Asistencia", resultado['message'])
                self._filter_asistencias()
                self.asistencia_registrada.emit()
            else:
                QMessageBox.warning(self, "Asistencia", resultado['message'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo marcar:\n{str(e)}")

    # ========== TAB: CLASES ==========
    def _clases_widget(self):
        """🔥 PLACEHOLDER ELEGANTE PARA CLASES"""
        w = QWidget()
        layout = QVBoxLayout(w)
        
        layout.addStretch()
        
        icon = QLabel("🧘")
        icon.setStyleSheet("font-size: 48pt;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        titulo = QLabel("Gestión de Clases")
        titulo.setStyleSheet("font-size: 18pt; font-weight: bold; color: #e5e7eb;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel("Módulo en desarrollo. Próximamente podrás:\n\n"
                     "• Ver clases disponibles\n"
                     "• Inscribir al miembro\n"
                     "• Consultar horarios")
        desc.setStyleSheet("font-size: 11pt; color: #9ca3af;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(icon)
        layout.addWidget(titulo)
        layout.addSpacing(10)
        layout.addWidget(desc)
        layout.addStretch()
        
        return w

    # ========== TAB: NOTAS ==========
    def _notas_widget(self):
        """🔥 CORREGIDO: Pestaña de notas con eliminación por ID"""
        w = QWidget()
        layout = QVBoxLayout(w)
        
        # Tabla de historial - 🔥 SOLO 2 COLUMNAS VISIBLES
        self.notes_table = QTableWidget(0, 2)
        self.notes_table.setHorizontalHeaderLabels(["Fecha/Hora", "Nota"])
        header = self.notes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.notes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.notes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.notes_table)
        
        # Campo de entrada
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Escribe una nota sobre el miembro...")
        self.notes_input.setFixedHeight(40)
        layout.addWidget(self.notes_input)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_guardar = QPushButton("💾 Guardar nota")
        btn_guardar.setStyleSheet("background-color: #10b981; color: white;")
        btn_guardar.clicked.connect(self._save_note)
        
        btn_eliminar = QPushButton("🗑️ Eliminar nota")
        btn_eliminar.setProperty("destructive", True)
        btn_eliminar.clicked.connect(self._delete_note)
        
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_eliminar)
        layout.addLayout(btn_layout)
        
        # Cargar notas existentes
        self._load_notes()
        
        return w

    def _save_note(self):
        """🔥 CORREGIDO: Guarda nota usando NoteService"""
        texto = self.notes_input.text().strip()
        
        if not texto:
            QMessageBox.warning(self, "Nota vacía", "Escribe algo antes de guardar")
            return
        
        # 🔥 USAR NOTE SERVICE
        resultado = self.note_service.add_note(self.member.get('id'), texto)
        
        if resultado["success"]:
            self._load_notes()
            self.notes_input.clear()
            QMessageBox.information(self, "Guardada", resultado["message"])
        else:
            QMessageBox.warning(self, "Error", resultado["message"])

    def _delete_note(self):
        """🔥 CORREGIDO: Elimina nota usando ID almacenado en UserRole"""
        selected_items = self.notes_table.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(
                self, 
                "Sin selección", 
                "Por favor, seleccione una nota para eliminar"
            )
            return
        
        row = self.notes_table.currentRow()
        
        # 🔥 OBTENER ID DESDE UserRole (almacenado en _load_notes)
        item_fecha = self.notes_table.item(row, 0)
        note_id = item_fecha.data(Qt.ItemDataRole.UserRole)
        
        if note_id is None:
            QMessageBox.critical(
                self, 
                "Error", 
                "No se pudo identificar la nota seleccionada"
            )
            return
        
        # Confirmar eliminación
        nota_texto = self.notes_table.item(row, 1).text()
        preview = nota_texto[:50] + "..." if len(nota_texto) > 50 else nota_texto
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la nota:\n\n'{preview}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 🔥 USAR NOTE SERVICE PARA ELIMINAR
            resultado = self.note_service.delete_note(note_id)
            
            if resultado["success"]:
                self._load_notes()
                QMessageBox.information(self, "Eliminada", resultado["message"])
            else:
                QMessageBox.warning(self, "Error", resultado["message"])

    def _load_notes(self):
        """🔥 CORREGIDO: Carga notas usando NoteService y guarda ID en UserRole"""
        self.notes_table.setRowCount(0)
        
        # 🔥 USAR NOTE SERVICE
        notas = self.note_service.get_notes(self.member.get('id'))
        
        for row, (note_id, fecha_hora, nota) in enumerate(notas):
            self.notes_table.insertRow(row)
            
            # Formatear fecha para display
            try:
                fecha_obj = datetime.strptime(fecha_hora, Config.DATETIME_FORMAT)
                fecha_display = fecha_obj.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_display = fecha_hora
            
            # Columna 0: Fecha/Hora (visible)
            item_fecha = QTableWidgetItem(fecha_display)
            # 🔥 GUARDAR ID EN UserRole PARA PODER ELIMINAR DESPUÉS
            item_fecha.setData(Qt.ItemDataRole.UserRole, note_id)
            self.notes_table.setItem(row, 0, item_fecha)
            
            # Columna 1: Nota (visible)
            item_nota = QTableWidgetItem(nota)
            self.notes_table.setItem(row, 1, item_nota)

    # ========== AVATAR ==========
    def _refresh_avatar(self):
        """Renderiza avatar circular"""
        foto = self.member.get('foto_path')
        size = 90
        
        if foto:
            try:
                img = QPixmap(foto).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                           Qt.TransformationMode.SmoothTransformation)
                # Crear máscara circular
                result = QPixmap(size, size)
                result.fill(Qt.GlobalColor.transparent)
                painter = QPainter(result)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, size, size)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, img)
                painter.end()
                self.avatar_label.setPixmap(result)
            except:
                self._avatar_placeholder()
        else:
            self._avatar_placeholder()

    def _avatar_placeholder(self):
        """Avatar por defecto"""
        size = 90
        pix = QPixmap(size, size)
        pix.fill(QColor("#374151"))
        self.avatar_label.setPixmap(pix)

    def _avatar_menu(self, event):
        """Menú contextual del avatar"""
        menu = QMenu(self)
        menu.addAction("📷 Cambiar foto", self._upload_photo)
        if self.member.get('foto_path'):
            menu.addAction("🗑️ Eliminar foto", self._delete_photo)
        menu.exec(self.mapToGlobal(event.pos()))

    def _upload_photo(self):
        """Sube nueva foto"""
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar foto", "", "Imágenes (*.png *.jpg *.jpeg)")
        if path:
            self.member['foto_path'] = path
            self._refresh_avatar()
            MemberService().update_member_photo(self.member.get('codigo'), path)
            QMessageBox.information(self, "Foto", "Foto actualizada correctamente")

    def _delete_photo(self):
        """Elimina foto"""
        self.member['foto_path'] = None
        self._refresh_avatar()
        MemberService().update_member_photo(self.member.get('codigo'), None)
        QMessageBox.information(self, "Foto", "Foto eliminada")

    def create_benefits_tab(self):
        """Crea la pestaña de beneficios detallados"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🎁 Beneficios y Privilegios")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #e5e7eb;
        """)
        layout.addWidget(header)
        
        # Info de categoría actual
        if self.current_categoria_id:
            categoria = self.category_service.get_category_by_id(self.current_categoria_id)
            if categoria:
                cat_info = QFrame()
                cat_info.setStyleSheet(f"""
                    QFrame {{
                        background: {categoria['color_hex']}22;
                        border: 2px solid {categoria['color_hex']};
                        border-radius: 8px;
                        padding: 16px;
                    }}
                """)
                
                cat_layout = QVBoxLayout(cat_info)
                
                cat_name = QLabel(f"Categoría Actual: {categoria['nombre']}")
                cat_name.setStyleSheet(f"""
                    font-size: 16px;
                    font-weight: bold;
                    color: {categoria['color_hex']};
                """)
                cat_layout.addWidget(cat_name)
                
                if categoria.get('descripcion'):
                    cat_desc = QLabel(categoria['descripcion'])
                    cat_desc.setStyleSheet("color: #94a3b8; font-size: 13px;")
                    cat_desc.setWordWrap(True)
                    cat_layout.addWidget(cat_desc)
                
                layout.addWidget(cat_info)
        
        # Lista de beneficios
        benefits_label = QLabel("Beneficios Activos:")
        benefits_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #cbd5e1;
            margin-top: 10px;
        """)
        layout.addWidget(benefits_label)
        
        # Obtener beneficios
        miembro_id = self.member.get('id')
        benefits = self.benefit_service.get_member_benefits(miembro_id) if miembro_id else []
        
        if benefits:
            for benefit in benefits:
                benefit_frame = self._create_benefit_detail_widget(benefit)
                layout.addWidget(benefit_frame)
        else:
            no_benefits = QLabel("No tienes beneficios configurados en tu categoría")
            no_benefits.setStyleSheet("color: #64748b; font-size: 13px; padding: 20px;")
            layout.addWidget(no_benefits)
        
        layout.addStretch()
        
        return widget

    def _create_benefit_detail_widget(self, benefit):
        """Crea widget detallado para un beneficio"""
        from PyQt6.QtGui import QFont
        
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setSpacing(16)
        
        # Icono
        icon_label = QLabel(benefit.get('icono', '•'))
        icon_label.setStyleSheet("""
            font-size: 32px;
            min-width: 40px;
            max-width: 40px;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Nombre
        from PyQt6.QtGui import QFont
        name_label = QLabel(benefit.get('nombre', 'Beneficio'))
        name_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #e5e7eb;")
        info_layout.addWidget(name_label)
        
        # Descripción
        if benefit.get('descripcion'):
            desc_label = QLabel(benefit['descripcion'])
            desc_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
            desc_label.setWordWrap(True)
            info_layout.addWidget(desc_label)
        
        # Valor configurado
        config = benefit.get('config', {})
        if config.get('enabled'):
            value_text = self._format_benefit_value_detailed(benefit)
            if value_text:
                value_label = QLabel(value_text)
                value_label.setStyleSheet("""
                    color: #3b82f6;
                    font-size: 13px;
                    font-weight: 600;
                    margin-top: 4px;
                """)
                info_layout.addWidget(value_label)
        
        layout.addLayout(info_layout, 1)
        
        # Estado
        status_label = QLabel("✅ Activo" if config.get('enabled') else "○ Inactivo")
        status_label.setStyleSheet(
            "color: #22c55e; font-size: 12px; font-weight: 500;" 
            if config.get('enabled') 
            else "color: #64748b; font-size: 12px;"
        )
        layout.addWidget(status_label)
        
        return frame

    def _format_benefit_value_detailed(self, benefit):
        """Formatea el valor del beneficio con más detalle"""
        config = benefit.get('config', {})
        tipo = benefit.get('tipo_valor', '')
        
        if tipo == 'percentage':
            porcentaje = config.get('descuento_porcentaje', 0)
            if porcentaje == 100:
                return "🎉 100% GRATIS"
            elif porcentaje > 0:
                return f"💰 {porcentaje}% de descuento"
        
        elif tipo == 'numeric':
            cantidad = config.get('cantidad', 0)
            if cantidad > 0:
                return f"📊 Hasta {cantidad}"
        
        elif tipo == 'boolean':
            if config.get('enabled'):
                return "✓ Incluido"
        
        return ""

