# -*- coding: utf-8 -*-
"""
Vista de gestión de miembros con paginación y sincronización por señales
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from services.member_service import MemberService
from services.plan_service import PlanService
from ui.payment_dialog import PaymentDialog
from ui.member_360_view import Member360Dialog

class MembersView(QWidget):
    """Vista principal de gestión de miembros con paginación"""
    
    PAGE_SIZE = 50  # Registros por página
    
    def __init__(self):
        super().__init__()
        self.service = MemberService()
        self.plan_service = PlanService()
        self.layout = QVBoxLayout(self)
        
        # Referencia a AttendanceView (se asigna desde MainWindow)
        self.attendance_view = None
        
        # Variables de paginación
        self.all_members = []
        self.filtered_members = []
        self.current_page = 1
        self.total_pages = 1

        self._setup_form_group()
        self._setup_table()
        self._setup_pagination_controls()
        self.load_members()

    def _setup_form_group(self):
        """Formulario de registro de nuevos miembros"""
        form_group = QGroupBox("➕ Nuevo Registro")
        form_layout = QGridLayout()
        form_group.setLayout(form_layout)

        form_layout.addWidget(QLabel("Nombre Completo:"), 0, 0)
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: Juan Perez")
        form_layout.addWidget(self.input_nombre, 0, 1)

        form_layout.addWidget(QLabel("DNI (Solo números):"), 1, 0)
        self.input_dni = QLineEdit()
        self.input_dni.setPlaceholderText("Ej: 12345678")
        form_layout.addWidget(self.input_dni, 1, 1)

        form_layout.addWidget(QLabel("Contacto:"), 2, 0)
        self.input_contacto = QLineEdit()
        self.input_contacto.setPlaceholderText("Ej: 999-999-999")
        form_layout.addWidget(self.input_contacto, 2, 1)

        form_layout.addWidget(QLabel("Email:"), 3, 0)
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Ej: juan@email.com")
        form_layout.addWidget(self.input_email, 3, 1)

        form_layout.addWidget(QLabel("Dirección:"), 4, 0)
        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Ej: Av. Siempre Viva 123")
        form_layout.addWidget(self.input_direccion, 4, 1)

        self.btn_register = QPushButton("Registrar Miembro")
        self.btn_register.setStyleSheet(
            "background-color: #38a169; color: white; font-weight: bold; padding: 10px;"
        )
        self.btn_register.clicked.connect(self.register_member)
        form_layout.addWidget(self.btn_register, 5, 0, 1, 2)

        self.layout.addWidget(form_group)
        self.layout.addSpacing(10)

    def _setup_table(self):
        """Tabla de listado de miembros"""
        label = QLabel("📋 Listado de Miembros")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔎 Buscar por nombre, DNI o código...")
        self.search_input.textChanged.connect(self.filter_members)
        self.layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Código", "Nombre", "DNI", "Contacto", "Membresía"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.table)

        # Doble clic abre perfil 360
        self.table.cellDoubleClicked.connect(self.open_member_profile)

        action_layout = QHBoxLayout()
        
        self.btn_view_payments = QPushButton("💰 Registrar Pago/Ver Historial")
        self.btn_view_payments.setStyleSheet(
            "background-color: #2b6cb0; color: white; font-weight: bold;"
        )
        self.btn_view_payments.clicked.connect(self.open_payment_dialog)
        action_layout.addWidget(self.btn_view_payments)

        self.btn_view_profile = QPushButton("👤 Ver Perfil 360")
        self.btn_view_profile.setStyleSheet(
            "background-color: #2b6cb0; color: white; font-weight: bold;"
        )
        self.btn_view_profile.clicked.connect(self.open_member_profile_from_button)
        action_layout.addWidget(self.btn_view_profile)

        action_layout.addStretch(1)
        self.layout.addLayout(action_layout)
    
    def _setup_pagination_controls(self):
        """Controles de paginación"""
        pagination_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("⬅ Anterior")
        self.btn_prev.setStyleSheet(
            "background-color: #4a5568; color: white; font-weight: bold; padding: 8px 16px;"
        )
        self.btn_prev.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.btn_prev)
        
        self.lbl_page_info = QLabel("Página 1 de 1")
        self.lbl_page_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_page_info.setStyleSheet("font-weight: bold; font-size: 13px;")
        pagination_layout.addWidget(self.lbl_page_info)
        
        self.btn_next = QPushButton("Siguiente ➡")
        self.btn_next.setStyleSheet(
            "background-color: #4a5568; color: white; font-weight: bold; padding: 8px 16px;"
        )
        self.btn_next.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.btn_next)
        
        self.layout.addLayout(pagination_layout)

    def register_member(self):
        """Registra un nuevo miembro"""
        nombre = self.input_nombre.text()
        dni = self.input_dni.text()
        contacto = self.input_contacto.text()
        email = self.input_email.text()
        direccion = self.input_direccion.text()

        try:
            resultado = self.service.register_member(nombre, dni, contacto, email, direccion)

            if resultado.get("success"):
                QMessageBox.information(self, "Registro Exitoso", resultado["message"])
                self.input_nombre.clear()
                self.input_dni.clear()
                self.input_contacto.clear()
                self.input_email.clear()
                self.input_direccion.clear()
            else:
                QMessageBox.warning(self, "Error de Registro", resultado["message"])

        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error inesperado:\n{str(e)}")

        self.load_members()

    def load_members(self):
        """Carga todos los miembros y muestra la página actual"""
        self.all_members = self.service.get_all_members_with_status()
        self.filtered_members = self.all_members.copy()
        self.current_page = 1
        self._calculate_pagination()
        self._display_current_page()

    def _calculate_pagination(self):
        """Calcula el total de páginas según los miembros filtrados"""
        total_members = len(self.filtered_members)
        self.total_pages = max(1, (total_members + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        
        # Ajustar página actual si está fuera de rango
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

    def _display_current_page(self):
        """Muestra solo los miembros de la página actual"""
        self.table.setRowCount(0)
        
        start_idx = (self.current_page - 1) * self.PAGE_SIZE
        end_idx = start_idx + self.PAGE_SIZE
        page_members = self.filtered_members[start_idx:end_idx]

        for row_number, miembro in enumerate(page_members):
            self.table.insertRow(row_number)
            miembro_id, nombre, dni, contacto, codigo, estado = miembro

            self.table.setItem(row_number, 0, QTableWidgetItem(codigo))
            self.table.setItem(row_number, 1, QTableWidgetItem(nombre))
            self.table.setItem(row_number, 2, QTableWidgetItem(dni))
            self.table.setItem(row_number, 3, QTableWidgetItem(contacto))

            item_estado = QTableWidgetItem(estado)
            if "Válida" in estado:
                item_estado.setForeground(Qt.GlobalColor.green)
            elif "Vencida" in estado:
                item_estado.setForeground(Qt.GlobalColor.red)
            else:
                item_estado.setForeground(Qt.GlobalColor.gray)

            self.table.setItem(row_number, 4, item_estado)
        
        self._update_pagination_controls()

    def _update_pagination_controls(self):
        """Actualiza el estado de los controles de paginación"""
        self.lbl_page_info.setText(f"Página {self.current_page} de {self.total_pages}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)

    def previous_page(self):
        """Navega a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self._display_current_page()

    def next_page(self):
        """Navega a la página siguiente"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._display_current_page()

    def filter_members(self):
        """Filtra miembros según búsqueda y actualiza paginación"""
        filtro = self.search_input.text().lower()
        
        if not filtro:
            self.filtered_members = self.all_members.copy()
        else:
            self.filtered_members = [
                miembro for miembro in self.all_members
                if filtro in miembro[4].lower() or  # código
                   filtro in miembro[1].lower() or  # nombre
                   filtro in miembro[2].lower()     # dni
            ]
        
        self.current_page = 1
        self._calculate_pagination()
        self._display_current_page()

    def open_payment_dialog(self):
        """Abre diálogo de pago para miembro seleccionado"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(
                self, 
                "Advertencia", 
                "Por favor, seleccione un miembro para registrar un pago"
            )
            return

        row = selected_rows[0].row()
        codigo_membresia = self.table.item(row, 0).text()
        miembro_data = self.service.find_member_by_identifier(codigo_membresia)

        if not miembro_data:
            QMessageBox.critical(self, "Error", "No se pudo encontrar el miembro seleccionado")
            return

        miembro_id = miembro_data[0]
        miembro_nombre = miembro_data[1]
        miembro_dni = miembro_data[2]

        dialog = PaymentDialog(
            miembro_id=miembro_id,
            miembro_nombre=miembro_nombre,
            miembro_dni=miembro_dni,
            codigo_membresia=codigo_membresia,
            parent=self
        )
        
        # 🔥 CONECTAR SEÑAL
        dialog.pago_registrado.connect(self.load_members)

        if dialog.exec() == dialog.DialogCode.Accepted:
            self.load_members()

    def open_member_profile(self, row, column=None):
        """Abre perfil 360 del miembro (desde doble clic)"""
        codigo_membresia = self.table.item(row, 0).text()
        miembro_data = self.service.find_member_by_identifier(codigo_membresia)

        if not miembro_data:
            QMessageBox.critical(self, "Error", "No se pudo encontrar el miembro seleccionado")
            return

        # Armar diccionario con datos del miembro
        member_data = {
            "id": miembro_data[0],
            "nombre": miembro_data[1],
            "dni": miembro_data[2],
            "contacto": miembro_data[3],
            "email": miembro_data[4],
            "direccion": miembro_data[5],
            "codigo": miembro_data[6],
            "estado": miembro_data[7],
            "foto_path": miembro_data[8],
            "nivel": "Básico",
            "cliente_desde": f"Cliente desde {miembro_data[1]}"  # Placeholder
        }

        dlg = Member360Dialog(member_data, self)

        # 🔥 CONECTAR SEÑALES PARA SINCRONIZACIÓN COMPLETA
        self._connect_member_360_signals(dlg)

        if dlg.exec() == dlg.DialogCode.Accepted:
            self.load_members()

    def open_member_profile_from_button(self):
        """Abre perfil 360 desde botón"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(
                self, 
                "Advertencia", 
                "Por favor, seleccione un miembro para ver perfil"
            )
            return

        row = selected_rows[0].row()
        self.open_member_profile(row)

    def _connect_member_360_signals(self, dlg):
        """
        Conecta todas las señales del Member360Dialog para sincronización.
        MÉTODO CENTRALIZADO - Evita duplicación de código.
        """
        # Sincronizar asistencias
        if hasattr(self, "attendance_view") and self.attendance_view:
            # Member360 → AttendanceView
            dlg.asistencia_registrada.connect(self.attendance_view.load_log)
            # AttendanceView → Member360
            self.attendance_view.asistencia_registrada.connect(dlg._filter_asistencias)
        
        # Sincronizar pagos y estado de membresía
        dlg.pago_registrado.connect(self.load_members)
        
        # Actualizar tabla cuando se registra asistencia (afecta estado)
        dlg.asistencia_registrada.connect(self.load_members)
