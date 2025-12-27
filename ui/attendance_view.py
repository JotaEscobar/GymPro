# -*- coding: utf-8 -*-
"""
Vista de Check-in / Asistencias con sincronización por señales
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from services.attendance_service import AttendanceService
from datetime import datetime
from core.config import Config

class AttendanceView(QWidget):
    """
    Vista para registro de asistencias.
    Emite señal cuando se registra o elimina una asistencia.
    """
    
    # 🔥 SEÑAL PARA SINCRONIZACIÓN
    asistencia_registrada = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.service = AttendanceService()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._setup_input_area()
        self._setup_table()
        self._setup_delete_button()
        self.load_log()

    def _setup_input_area(self):
        """Área de entrada de DNI/Código"""
        input_layout = QVBoxLayout()
        input_button_layout = QHBoxLayout()

        label = QLabel("🔒 Escribe DNI o Código de Membresía:")
        label.setStyleSheet("font-weight: bold;")
        input_button_layout.addWidget(label)

        self.identifier_input = QLineEdit()
        self.identifier_input.setPlaceholderText("Ej: 12345678 o JP123")
        self.identifier_input.setStyleSheet("font-size: 16px; padding: 10px;")
        self.identifier_input.returnPressed.connect(self.mark_entry)
        input_button_layout.addWidget(self.identifier_input)

        self.btn_mark = QPushButton("Marcar Entrada")
        self.btn_mark.setStyleSheet(
            "background-color: #89b4fa; color: #1e1e2e; font-weight: bold; padding: 10px;"
        )
        self.btn_mark.clicked.connect(self.mark_entry)
        input_button_layout.addWidget(self.btn_mark)

        input_layout.addLayout(input_button_layout)

        self.lbl_detailed_status = QLabel("...")
        self.lbl_detailed_status.setStyleSheet(
            "font-size: 14pt; font-style: italic; padding: 5px; margin-top: 10px;"
        )
        input_layout.addWidget(self.lbl_detailed_status)

        self.layout.addLayout(input_layout)
        self.layout.addSpacing(20)

    def _setup_table(self):
        """Tabla de entradas registradas hoy"""
        label = QLabel(
            f"⏰ Entradas Registradas Hoy ({datetime.now().strftime(Config.DISPLAY_DATE_FORMAT)})"
        )
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Nombre", "Plan", "Válido hasta", "Hora de Entrada"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)
        self.layout.addStretch()

    def _setup_delete_button(self):
        """Botón para eliminar entrada"""
        delete_layout = QHBoxLayout()
        delete_layout.addStretch()

        self.btn_delete = QPushButton("🗑️ Eliminar Entrada Seleccionada")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #c92a2a;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #a51111;
            }
        """)
        self.btn_delete.clicked.connect(self.delete_selected_entry)

        delete_layout.addWidget(self.btn_delete)
        self.layout.addLayout(delete_layout)

    def mark_entry(self):
        """
        Marca la entrada de un miembro y emite señal para sincronización.
        """
        identifier = self.identifier_input.text().strip()

        if not identifier:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese un DNI o Código")
            return

        try:
            resultado = self.service.register_check_in(identifier)
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error inesperado:\n{str(e)}")
            return

        status = resultado.get('status')
        message = resultado.get('message')
        alerta = resultado.get('alerta')

        self.identifier_input.clear()
        self.load_log()

        # 🔥 EMITIR SEÑAL PARA SINCRONIZACIÓN
        if status == 'Éxito':
            self.asistencia_registrada.emit()

        msg = QMessageBox()
        msg.setWindowTitle("Resultado de Asistencia")

        if status == 'Éxito':
            miembro_nombre = resultado.get('miembro_nombre', 'Miembro')
            detailed_text = f"¡ACCESO CONCEDIDO! Bienvenido(a) {miembro_nombre}."
            self.lbl_detailed_status.setText(detailed_text)
            self.lbl_detailed_status.setStyleSheet(
                "color: #a6e3a1; font-size: 14pt; font-style: italic; font-weight: bold;"
            )
            msg.setIcon(QMessageBox.Icon.Information)
            if alerta:
                QMessageBox.warning(self, "Alerta de Vencimiento", alerta)

        elif status in ['Vencido', 'Sin Plan']:
            self.lbl_detailed_status.setText(message)
            self.lbl_detailed_status.setStyleSheet(
                "color: #f38ba8; font-size: 14pt; font-style: italic; font-weight: bold;"
            )
            msg.setIcon(QMessageBox.Icon.Critical)

        else:
            self.lbl_detailed_status.setText(message)
            self.lbl_detailed_status.setStyleSheet(
                "color: orange; font-size: 14pt; font-style: italic; font-weight: bold;"
            )
            msg.setIcon(QMessageBox.Icon.Warning)

        msg.setText(message)
        msg.exec()

    def load_log(self):
        """Carga el log de asistencias de hoy"""
        registros = self.service.get_todays_log()
        self.table.setRowCount(0)

        for row_index, (codigo, nombre, plan, vencimiento, entrada) in enumerate(registros):
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QTableWidgetItem(codigo))
            self.table.setItem(row_index, 1, QTableWidgetItem(nombre))
            self.table.setItem(row_index, 2, QTableWidgetItem(plan))

            item_venc = QTableWidgetItem(vencimiento)
            try:
                fecha_venc = datetime.strptime(vencimiento, Config.DATE_FORMAT)
                if fecha_venc >= datetime.now():
                    item_venc.setForeground(QColor("green"))
                else:
                    item_venc.setForeground(QColor("red"))
            except:
                pass
            self.table.setItem(row_index, 3, item_venc)

            self.table.setItem(row_index, 4, QTableWidgetItem(entrada))

    def delete_selected_entry(self):
        """
        Elimina la entrada seleccionada y emite señal para sincronización.
        """
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, 
                "Sin selección", 
                "Seleccione una fila para eliminar la entrada"
            )
            return

        codigo = self.table.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la última entrada registrada para el miembro con código {codigo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                resultado = self.service.delete_last_check_in_by_code(codigo)
                if resultado:
                    QMessageBox.information(self, "Eliminado", "Entrada eliminada correctamente")
                    
                    # 🔥 EMITIR SEÑAL
                    self.asistencia_registrada.emit()
                else:
                    QMessageBox.warning(self, "No encontrado", "No se encontró entrada para eliminar")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la entrada:\n{str(e)}")

            self.load_log()
