# -*- coding: utf-8 -*-
"""
Diálogo para registro de pagos con sincronización por señales
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from services.payment_service import PaymentService
from services.plan_service import PlanService
from datetime import datetime
from core.config import Config
from ui.combo_members_dialog import ComboMembersDialog
from services.combo_service import ComboService


class PaymentDialog(QDialog):
    """
    Diálogo para registrar pagos y ver historial.
    Emite señal cuando se registra un pago exitosamente.
    """
    
    # 🔥 SEÑAL PARA SINCRONIZACIÓN ENTRE VISTAS
    pago_registrado = pyqtSignal()
    
    def __init__(self, miembro_id, miembro_nombre, miembro_dni, codigo_membresia, parent=None):
        super().__init__(parent)

        self.miembro_id = miembro_id
        self.miembro_nombre = miembro_nombre
        self.miembro_dni = miembro_dni
        self.codigo_membresia = codigo_membresia
        self.combo_service = ComboService()
        self.combo_member_ids = []  # IDs de miembros del combo        

        self.payment_service = PaymentService()
        self.plan_service = PlanService()
        self.plans_data = {}

        self.table_history = None

        # Tamaño dinámico según origen
        if parent and parent.__class__.__name__ == "Member360Dialog":
            self.setFixedSize(480, 280)  # Vista 360 → tamaño compacto
            self.setStyleSheet("""
                QLabel {
                    font-size: 11pt;
                }
                QLabel#formTitle {
                    font-size: 12pt;
                    font-weight: bold;
                }
            """)
        else:
            self.setFixedSize(800, 600)  # Vista principal → tamaño completo

        self.setWindowTitle(f"💸 Pago de {miembro_nombre}")
        self.main_layout = QVBoxLayout(self)

        self._setup_info_header()
        self._setup_payment_form()

        if self.miembro_id is not None:
            self._setup_history_table()
            self.load_payment_history()

        self.load_plans_for_combo()

        if self.miembro_id is None:
            self.ocultar_historial()

    def _setup_info_header(self):
        """Encabezado con información del miembro"""
        header_layout = QHBoxLayout()
        lbl_info = QLabel()
        lbl_info.setText(
            f"<b>Miembro:</b> <span style='color:#facc15;'>{self.miembro_nombre}</span> "
            f"(<span style='color:#cad2de;'>{self.codigo_membresia}</span>) &nbsp;&nbsp; "
            f"<b>DNI:</b> <span style='color:#facc15;'>{self.miembro_dni}</span>"
        )
        lbl_info.setTextFormat(Qt.TextFormat.RichText)
        header_layout.addWidget(lbl_info)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

    def _setup_payment_form(self):
        """Formulario de registro de pago"""
        form_label = QLabel("💳 Registrar Nuevo Pago")
        form_label.setObjectName("formTitle")
        self.main_layout.addWidget(form_label)

        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Plan/Tarifa:"), 0, 0)
        self.combo_plan = QComboBox()
        form_layout.addWidget(self.combo_plan, 0, 1)

        form_layout.addWidget(QLabel("Monto Pagado (Soles):"), 1, 0)
        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("Ej: 60.00")
        form_layout.addWidget(self.input_monto, 1, 1)

        # Indicador de plan combo
        self.combo_indicator_label = QLabel()
        self.combo_indicator_label.setStyleSheet("""
            QLabel {
                background: #dbeafe;
                color: #1e40af;
                padding: 6px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 10pt;
            }
        """)
        self.combo_indicator_label.setVisible(False)
        form_layout.addWidget(self.combo_indicator_label, 0, 2)

        form_layout.addWidget(QLabel("Fecha de Pago:"), 2, 0)
        self.input_fecha_pago = QDateEdit(calendarPopup=True)
        self.input_fecha_pago.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_pago.setDate(QDate.currentDate())
        form_layout.addWidget(self.input_fecha_pago, 2, 1)

        boton_layout = QHBoxLayout()

        self.btn_register_payment = QPushButton("✅ Confirmar Pago y Extender Membresía")
        self.btn_register_payment.setStyleSheet(
            "background-color: #38a169; color: white; font-weight: bold; padding: 8px;"
        )
        self.btn_register_payment.setFixedHeight(32)
        self.btn_register_payment.clicked.connect(self.register_payment)
        boton_layout.addWidget(self.btn_register_payment)

        self.btn_close = QPushButton("Cancelar")
        self.btn_close.setStyleSheet(
            "background-color: #b91c1c; color: white; font-weight: bold; padding: 8px;"
        )
        self.btn_close.setFixedHeight(32)
        self.btn_close.clicked.connect(self.reject)
        boton_layout.addWidget(self.btn_close)

        form_layout.addLayout(boton_layout, 3, 0, 1, 2)

        self.main_layout.addLayout(form_layout)

    def _setup_history_table(self):
        """Tabla de historial de pagos"""
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels([
            "ID Pago", "Plan", "Monto", "Fecha Pago", "Vence"
        ])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_history.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_history.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.main_layout.addWidget(self.table_history)

    def load_plans_for_combo(self):
        """Carga los planes activos en el combo"""
        self.plans_data = {}
        planes = self.plan_service.get_all_plans(include_inactive=False)

        self.combo_plan.clear()

        if not planes:
            self.combo_plan.addItem("No hay planes activos")
            self.btn_register_payment.setEnabled(False)
            return

        for id, nombre, precio, dias, personas, _, _, _, _, _ in planes:
            self.combo_plan.addItem(f"{nombre} (S/ {precio:.2f}) - {dias} días", id)
            self.plans_data[id] = {'nombre': nombre, 'precio': precio, 'dias': dias}

        self.combo_plan.currentIndexChanged.connect(self._update_monto_input)
        self.combo_plan.currentIndexChanged.connect(self._on_plan_changed)
        self._update_monto_input()

    def _on_plan_changed(self, index):
        """
        Se ejecuta cuando cambia el plan seleccionado.
        Verifica si es un plan combo para mostrar indicador.
        """
        plan_id = self.combo_plan.currentData()
        
        if not plan_id or plan_id not in self.plans_data:
            self.combo_indicator_label.setVisible(False)
            return
        
        # Obtener info del plan
        from models.plan_model import PlanModel
        plan_model = PlanModel()
        plan = plan_model.get_plan_by_id(plan_id)
        
        if plan and plan[4] > 1:  # personas_combo > 1
            # Es un plan combo
            self.combo_indicator_label.setText(
                f"👥 Plan Combo: {plan[4]} personas"
            )
            self.combo_indicator_label.setVisible(True)
        else:
            self.combo_indicator_label.setVisible(False)

    def _update_monto_input(self):
        """Actualiza el monto según el plan seleccionado"""
        plan_id = self.combo_plan.currentData()
        if plan_id in self.plans_data:
            precio = self.plans_data[plan_id]['precio']
            self.input_monto.setText(str(precio))
        else:
            self.input_monto.clear()

    def register_payment(self):
        """
        Registra el pago y emite señal para sincronización.
        NUEVO: Auto-registra movimiento en cash_movements
        """
        plan_id = self.combo_plan.currentData()
        monto_pagado_str = self.input_monto.text()
        fecha_pago_str = self.input_fecha_pago.date().toString(Qt.DateFormat.ISODate)

        if not plan_id:
            QMessageBox.warning(self, "Error", "Debe seleccionar un plan válido")
            return
        
        # Verificar si es plan combo
        from models.plan_model import PlanModel
        plan_model = PlanModel()
        plan = plan_model.get_plan_by_id(plan_id)

        # Si es combo y aún no se seleccionaron miembros, abrir diálogo
        if plan and plan[4] > 1:  # personas_combo > 1
            if not self.combo_member_ids:
                # Abrir diálogo de combo members
                combo_dialog = ComboMembersDialog(
                    parent=self,
                    plan_nombre=plan[1],  # nombre del plan
                    plan_max_personas=plan[4],  # 🔥 FIX: cantidad_personas (era plan[5])
                    monto_total=float(monto_pagado_str) if monto_pagado_str else 0.0,
                    pagador_id=self.miembro_id,
                    pagador_nombre=self.miembro_nombre
                )
                
                if combo_dialog.exec() == QDialog.DialogCode.Accepted:
                    self.combo_member_ids = combo_dialog.get_selected_members()
                else:
                    # Usuario canceló, no procesar pago
                    return

        resultado = self.payment_service.process_payment(
            self.miembro_id,
            plan_id,
            monto_pagado_str,
            fecha_pago_str
        )

        if resultado.get("success"):
            payment_id = resultado.get('data', {}).get('payment_id')
            
            # 🔥 NUEVO: Auto-registrar en cash_movements
            try:
                from services.caja_service import CajaService
                caja_service = CajaService()
                
                # Obtener método de pago (puedes agregar un QComboBox en el futuro)
                # Por ahora, usamos 'efectivo' como default
                metodo_pago = 'efectivo'  # TODO: Agregar selector de método de pago en UI
                
                caja_service.registrar_movimiento(
                    tipo='ingreso',
                    categoria='membresia',
                    metodo=metodo_pago,
                    monto=float(monto_pagado_str),
                    ref_tipo='payment',
                    ref_id=payment_id,
                    desc=f"Pago membresía - {self.miembro_nombre} ({plan[1]})",
                    usuario_id=None  # TODO: Obtener usuario actual cuando implementemos login
                )
            except Exception as e:
                # No fallar si cash_movements falla
                print(f"Advertencia: No se pudo registrar en cash_movements: {e}")
            
            # Si es combo, registrar miembros
            if self.combo_member_ids and payment_id:
                combo_result = self.combo_service.register_combo_payment(
                    payment_id=payment_id,
                    titular_id=self.miembro_id,
                    beneficiarios_ids=self.combo_member_ids,
                    plan_id=plan_id
                )
                
                if not combo_result.success:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        f"Pago registrado pero hubo un problema al registrar el combo:\n{combo_result.message}"
                    )
            
            QMessageBox.information(self, "Pago Exitoso", resultado['message'])
            
            # Actualizar tabla local si existe
            if self.miembro_id is not None:
                self.load_payment_history()
            
            # 🔥 EMITIR SEÑAL PARA SINCRONIZACIÓN
            self.pago_registrado.emit()
            
            self.accept()
        else:
            QMessageBox.critical(self, "Error de Pago", resultado['message'])

    def load_payment_history(self):
        """Carga el historial de pagos en la tabla"""
        pagos = self.payment_service.get_member_payments(self.miembro_id)
        self.table_history.setRowCount(0)

        for row_number, pago in enumerate(pagos):
            self.table_history.insertRow(row_number)
            id_pago, nombre_plan, monto, f_pago, f_vence = pago

            self.table_history.setItem(row_number, 0, QTableWidgetItem(str(id_pago)))
            self.table_history.setItem(row_number, 1, QTableWidgetItem(nombre_plan))
            self.table_history.setItem(row_number, 2, QTableWidgetItem(f"S/ {monto:.2f}"))
            self.table_history.setItem(row_number, 3, QTableWidgetItem(f_pago))

            item_vence = QTableWidgetItem(f_vence)
            try:
                if f_vence and datetime.strptime(f_vence, Config.DATE_FORMAT).date() < datetime.now().date():
                    item_vence.setForeground(Qt.GlobalColor.red)
                else:
                    item_vence.setForeground(Qt.GlobalColor.darkGreen)
            except:
                pass

            self.table_history.setItem(row_number, 4, item_vence)

    def ocultar_historial(self):
        """Oculta la tabla de historial"""
        if self.table_history:
            self.table_history.hide()
