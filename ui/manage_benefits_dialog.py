# -*- coding: utf-8 -*-
"""
Diálogo para Gestionar Tipos de Beneficios
Permite crear, editar y eliminar tipos de beneficios personalizados
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QComboBox, QTextEdit,
                             QMessageBox, QFormLayout, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from services.benefit_service import BenefitService
from core.logger import logger

class ManageBenefitsDialog(QDialog):
    """Diálogo para gestionar tipos de beneficios"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.benefit_service = BenefitService()
        
        self.setWindowTitle("Gestionar Tipos de Beneficios")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.setStyleSheet("""
            QDialog {
                background: #0f172a;
                color: #e5e7eb;
            }
            QLabel {
                color: #e5e7eb;
            }
            QLineEdit, QTextEdit, QComboBox {
                background: #1e293b;
                color: #e5e7eb;
                border: 1px solid #475569;
                padding: 8px;
                border-radius: 6px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #3b82f6;
            }
        """)
        
        self._setup_ui()
        self._load_benefits()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🎁 Gestión de Tipos de Beneficios")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #f1f5f9;
            padding: 10px;
            background: #1e293b;
            border-radius: 8px;
            border: 1px solid #334155;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Info
        info = QLabel("Define los tipos de beneficios disponibles para asignar a las categorías")
        info.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Tabla de beneficios
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # 🔥 CAMBIADO de 5 a 4
        self.table.setHorizontalHeaderLabels([
            "#", "Nombre", "Tipo", "Acciones"  # 🔥 QUITADO "Código", AGREGADO "#"
        ])
        
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                gridline-color: #334155;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e5e7eb;
            }
            QTableWidget::item:selected {
                background: #3b82f6;
                color: #ffffff;
            }
            QHeaderView::section {
                background: #0f172a;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #334155;
                font-weight: 600;
                color: #cbd5e1;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 🔥 # fijo
        self.table.setColumnWidth(0, 80)  # 🔥 AUMENTADO de 50 a 80
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 🔥 Acciones fijo
        self.table.setColumnWidth(3, 160)  # 🔥 AUMENTADO de 120 a 160
        
        # 🔥 OCULTAR números de fila externos + AUMENTAR altura
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(56)  # Altura de fila
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table, 1)
        
        # Botones inferiores
        bottom_layout = QHBoxLayout()
        
        new_btn = QPushButton("➕ Nuevo Beneficio")
        new_btn.clicked.connect(self._on_new_benefit)
        new_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bottom_layout.addWidget(new_btn)
        
        bottom_layout.addStretch()
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #374151;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
    
    def _load_benefits(self):
        """Carga los tipos de beneficios en la tabla"""
        benefits = self.benefit_service.get_all_benefit_types()
        self.table.setRowCount(0)
        
        for row, benefit in enumerate(benefits):
            self.table.insertRow(row)
            
            # 🔥 # (Orden)
            orden_item = QTableWidgetItem(str(row + 1))
            orden_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, orden_item)
            
            # 🔥 Nombre (con icono)
            nombre_con_icono = f"{benefit.get('icono', '•')} {benefit['nombre']}"
            self.table.setItem(row, 1, QTableWidgetItem(nombre_con_icono))
            
            # Tipo
            tipo_map = {
                'boolean': 'Sí/No',
                'numeric': 'Cantidad',
                'percentage': 'Porcentaje'
            }
            self.table.setItem(row, 2, QTableWidgetItem(tipo_map.get(benefit['tipo_valor'], 'Desconocido')))
            
            # Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(8, 4, 8, 4)  # 🔥 AUMENTADO margen horizontal
            actions_layout.setSpacing(6)  # 🔥 AUMENTADO spacing
            
            edit_btn = QPushButton("✏️ Editar")  # 🔥 AGREGADO texto
            edit_btn.setFixedHeight(32)  # 🔥 QUITADO fixed width
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
            """)
            edit_btn.clicked.connect(lambda checked, b=benefit: self._on_edit_benefit(b))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(32, 32)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #ef4444;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda checked, b=benefit: self._on_delete_benefit(b))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 3, actions_widget)  # 🔥 CAMBIADO de 4 a 3
    
    def _on_new_benefit(self):
        """Abre diálogo para crear nuevo beneficio"""
        dialog = BenefitFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_benefits()
    
    def _on_edit_benefit(self, benefit):
        """Abre diálogo para editar beneficio"""
        dialog = BenefitFormDialog(self, benefit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_benefits()
    
    def _on_delete_benefit(self, benefit):
        """Elimina un tipo de beneficio"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar el tipo de beneficio '{benefit['nombre']}'?\n\n"
            "Esto eliminará todas las configuraciones asociadas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.benefit_service.delete_benefit_type(benefit['codigo'])
            
            if result.success:
                QMessageBox.information(self, "Éxito", result.message)
                self._load_benefits()
            else:
                QMessageBox.warning(self, "Error", result.message)


class BenefitFormDialog(QDialog):
    """Diálogo para crear/editar un tipo de beneficio"""
    
    def __init__(self, parent=None, benefit=None):
        super().__init__(parent)
        self.benefit = benefit
        self.benefit_service = BenefitService()
        self.is_edit = benefit is not None
        
        title = "Editar Beneficio" if self.is_edit else "Nuevo Beneficio"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setStyleSheet("""
            QDialog {
                background: #0f172a;
                color: #e5e7eb;
            }
            QLabel {
                color: #e5e7eb;
            }
            QLineEdit, QTextEdit, QComboBox {
                background: #1e293b;
                color: #e5e7eb;
                border: 1px solid #475569;
                padding: 8px;
                border-radius: 6px;
            }
        """)
        
        self._setup_ui()
        
        if self.is_edit:
            self._load_benefit_data()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        
        # 🔥 CÓDIGO OCULTO - Ya no se muestra al usuario
        # self.input_codigo se auto-genera en _on_save()
        
        # Nombre
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("ej: Descuento en Sauna")
        form.addRow("Nombre:", self.input_nombre)  # 🔥 SIN asterisco
        
        # Icono
        self.input_icono = QLineEdit()
        self.input_icono.setPlaceholderText("ej: 🧖 (emoji)")
        form.addRow("Icono:", self.input_icono)
        
        # Tipo de valor
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Sí/No", "Cantidad", "Porcentaje"])
        form.addRow("Tipo de Valor:", self.combo_tipo)  # 🔥 SIN asterisco
        
        # Descripción
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción del beneficio...")
        self.input_descripcion.setMaximumHeight(80)
        form.addRow("Descripción:", self.input_descripcion)
        
        layout.addLayout(form)
        
        # Info
        info = QLabel("El código se genera automáticamente")  # 🔥 CAMBIADO
        info.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(info)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background: #374151;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Guardar")
        save_btn.clicked.connect(self._on_save)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_benefit_data(self):
        """Carga datos del beneficio para edición"""
        # 🔥 Guardar código para usar en _on_save (ya no hay campo visual)
        self.benefit_codigo = self.benefit['codigo']
        
        self.input_nombre.setText(self.benefit['nombre'])
        self.input_icono.setText(self.benefit.get('icono', ''))
        self.input_descripcion.setPlainText(self.benefit.get('descripcion', ''))
        
        tipo_map = {
            'boolean': 0,
            'numeric': 1,
            'percentage': 2
        }
        self.combo_tipo.setCurrentIndex(tipo_map.get(self.benefit['tipo_valor'], 0))
    
    def _on_save(self):
        """Guarda el tipo de beneficio"""
        # Validar
        nombre = self.input_nombre.text().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El Nombre es obligatorio")
            return
        
        # 🔥 AUTO-GENERAR CÓDIGO
        if self.is_edit:
            codigo = self.benefit_codigo  # Usar código existente
        else:
            # Obtener el máximo código existente
            from core.database_manager import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(CAST(SUBSTR(codigo, 4) AS INTEGER)) FROM benefit_types WHERE codigo LIKE 'BEN%'")
            max_code = cursor.fetchone()[0] or 0
            conn.close()
            codigo = f"BEN{str(max_code + 1).zfill(3)}"
        
        # Mapear tipo
        tipo_map = {
            0: 'boolean',
            1: 'numeric',
            2: 'percentage'
        }
        tipo_valor = tipo_map[self.combo_tipo.currentIndex()]
        
        # Datos
        data = {
            'codigo': codigo,
            'nombre': nombre,
            'icono': self.input_icono.text().strip() or '•',
            'tipo_valor': tipo_valor,
            'descripcion': self.input_descripcion.toPlainText().strip()
        }
        
        # Guardar
        if self.is_edit:
            result = self.benefit_service.update_benefit_type(codigo, data)
        else:
            result = self.benefit_service.create_benefit_type(data)
        
        if result.success:
            QMessageBox.information(self, "Éxito", result.message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", result.message)
