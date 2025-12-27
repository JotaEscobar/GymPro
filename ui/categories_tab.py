# -*- coding: utf-8 -*-
"""
Tab de Gestión de Categorías de Membresía
Se integra en plans_view como una pestaña adicional
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLabel, QLineEdit, QDialog, QFormLayout,
                             QColorDialog, QSpinBox, QTextEdit, QMessageBox,
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from services.category_service import CategoryService
from core.logger import logger
from ui.manage_benefits_dialog import ManageBenefitsDialog

class CategoriesTab(QWidget):
    """Tab para gestión de categorías de membresía"""
    
    category_changed = pyqtSignal()  # Señal cuando cambia una categoría
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.category_service = CategoryService()
        self._setup_ui()
        self._load_categories()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏷️ Categorías de Membresía")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #f1f5f9;
            background: transparent;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón Nueva Categoría
        new_btn = QPushButton("➕ Nueva Categoría")
        new_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self._on_new_category)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)

        # Botón Gestionar Beneficios
        manage_benefits_btn = QPushButton("⚙️ Gestionar Beneficios")
        manage_benefits_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        manage_benefits_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        manage_benefits_btn.clicked.connect(self._on_manage_benefits)
        header_layout.addWidget(manage_benefits_btn)
        
        # Info
        info = QLabel("Las categorías determinan los beneficios que obtienen los miembros")
        info.setStyleSheet("color: #94a3b8; font-size: 13px; background: transparent;")
        layout.addWidget(info)
        
        # Tabla de categorías
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nombre", "Color", "Orden", "Planes", "Estado", "Acciones"
        ])
        
        # Estilo de tabla
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                gridline-color: #334155;
                color: #e5e7eb;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e5e7eb;
                border-bottom: 1px solid #2d3748;
            }
            QTableWidget::item:selected {
                background: #334155;
                color: #f1f5f9;
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
        
        # Configurar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 200)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
    
    def _load_categories(self):
        """Carga las categorías en la tabla"""
        categories = self.category_service.get_all_categories(include_inactive=True)
        
        self.table.setRowCount(len(categories))
        
        for row, cat in enumerate(categories):
            # Nombre
            name_item = QTableWidgetItem(cat['nombre'])
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            self.table.setItem(row, 0, name_item)
            
            # Color (preview)
            color_widget = QWidget()
            color_layout = QHBoxLayout(color_widget)
            color_layout.setContentsMargins(8, 4, 8, 4)
            
            color_preview = QFrame()
            color_preview.setFixedSize(60, 24)
            color_preview.setStyleSheet(f"""
                background: {cat['color_hex']};
                border-radius: 4px;
                border: 1px solid #e2e8f0;
            """)
            color_layout.addWidget(color_preview)
            color_layout.addStretch()
            
            self.table.setCellWidget(row, 1, color_widget)
            
            # Orden
            orden_item = QTableWidgetItem(str(cat['orden']))
            orden_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, orden_item)
            
            # Planes asociados
            stats = self.category_service.get_category_stats(cat['id'])
            planes_item = QTableWidgetItem(str(stats['planes_asociados']))
            planes_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, planes_item)
            
            # Estado
            if cat['activo']:
                status_item = QTableWidgetItem("● Activo")
                status_item.setForeground(QColor("#22c55e"))
            else:
                status_item = QTableWidgetItem("○ Inactivo")
                status_item.setForeground(QColor("#94a3b8"))
            self.table.setItem(row, 4, status_item)
            
            # Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)
            
            # Botón Editar
            edit_btn = QPushButton("✏️ Editar")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                }
            """)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, c=cat: self._on_edit_category(c))
            actions_layout.addWidget(edit_btn)
            
            # Botón Configurar
            config_btn = QPushButton("⚙️ Beneficios")
            config_btn.setStyleSheet("""
                QPushButton {
                    background: #dbeafe;
                    border: 1px solid #93c5fd;
                    color: #1e40af;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #bfdbfe;
                }
            """)
            config_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            config_btn.clicked.connect(lambda checked, c=cat: self._on_configure_benefits(c))
            actions_layout.addWidget(config_btn)
            
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 5, actions_widget)
            
            # Altura de fila
            self.table.setRowHeight(row, 50)
    
    def _on_new_category(self):
        """Abre diálogo para crear nueva categoría"""
        dialog = CategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            result = self.category_service.create_category(
                nombre=data['nombre'],
                color_hex=data['color_hex'],
                orden=data['orden'],
                descripcion=data['descripcion']
            )
            
            if result.success:
                QMessageBox.information(self, "Éxito", result.message)
                self._load_categories()
                self.category_changed.emit()
            else:
                QMessageBox.warning(self, "Error", result.message)
    
    def _on_edit_category(self, category):
        """Abre diálogo para editar categoría"""
        dialog = CategoryDialog(self, category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            result = self.category_service.update_category(
                categoria_id=category['id'],
                nombre=data['nombre'],
                color_hex=data['color_hex'],
                orden=data['orden'],
                descripcion=data['descripcion'],
                activo=data['activo']
            )
            
            if result.success:
                QMessageBox.information(self, "Éxito", result.message)
                self._load_categories()
                self.category_changed.emit()
            else:
                QMessageBox.warning(self, "Error", result.message)
    
    def _on_configure_benefits(self, category):
        """Abre diálogo de configuración de beneficios"""
        from ui.benefits_config_dialog import BenefitsConfigDialog
        
        dialog = BenefitsConfigDialog(self, category['id'], category['nombre'])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.category_changed.emit()

    def _on_manage_benefits(self):
        """Abre diálogo para gestionar tipos de beneficios"""
        dialog = ManageBenefitsDialog(self)
        dialog.exec()


class CategoryDialog(QDialog):
    """Diálogo para crear/editar categoría"""
    
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.is_edit = category is not None
        
        self.setWindowTitle("Editar Categoría" if self.is_edit else "Nueva Categoría")
        self.setModal(True)
        self.setFixedWidth(450)
        
        self._setup_ui()
        
        if self.is_edit:
            self._load_category_data()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Premium")
        self.nombre_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        form.addRow("Nombre:", self.nombre_input)
        
        # Color
        color_layout = QHBoxLayout()
        
        self.color_input = QLineEdit("#3b82f6")
        self.color_input.setMaxLength(7)
        self.color_input.setFixedWidth(100)
        self.color_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-family: monospace;
            }
        """)
        color_layout.addWidget(self.color_input)
        
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(40, 32)
        self.color_preview.setStyleSheet(f"""
            background: {self.color_input.text()};
            border-radius: 6px;
            border: 1px solid #cbd5e1;
        """)
        color_layout.addWidget(self.color_preview)
        
        color_btn = QPushButton("🎨 Elegir")
        color_btn.clicked.connect(self._pick_color)
        color_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        color_layout.addWidget(color_btn)
        color_layout.addStretch()
        
        self.color_input.textChanged.connect(self._update_color_preview)
        
        form.addRow("Color:", color_layout)
        
        # Orden
        self.orden_input = QSpinBox()
        self.orden_input.setMinimum(0)
        self.orden_input.setMaximum(999)
        self.orden_input.setValue(0)
        self.orden_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
            }
        """)
        form.addRow("Orden:", self.orden_input)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(80)
        self.descripcion_input.setPlaceholderText("Descripción opcional...")
        self.descripcion_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        form.addRow("Descripción:", self.descripcion_input)
        
        # Estado (solo en edición)
        if self.is_edit:
            from PyQt6.QtWidgets import QCheckBox
            self.activo_check = QCheckBox("Categoría activa")
            self.activo_check.setChecked(True)
            self.activo_check.setStyleSheet("font-size: 13px;")
            form.addRow("Estado:", self.activo_check)
        
        layout.addLayout(form)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self._on_save)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
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
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_category_data(self):
        """Carga datos de la categoría en edición"""
        self.nombre_input.setText(self.category['nombre'])
        self.color_input.setText(self.category['color_hex'])
        self.orden_input.setValue(self.category['orden'])
        
        if self.category.get('descripcion'):
            self.descripcion_input.setPlainText(self.category['descripcion'])
        
        if hasattr(self, 'activo_check'):
            self.activo_check.setChecked(self.category['activo'])
    
    def _pick_color(self):
        """Abre selector de color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_input.setText(color.name())
    
    def _update_color_preview(self, color_hex):
        """Actualiza el preview del color"""
        self.color_preview.setStyleSheet(f"""
            background: {color_hex};
            border-radius: 6px;
            border: 1px solid #cbd5e1;
        """)
    
    def _on_save(self):
        """Valida y acepta el diálogo"""
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        if not self.color_input.text().startswith('#'):
            QMessageBox.warning(self, "Error", "Color inválido. Use formato #RRGGBB")
            return
        
        self.accept()
    
    def get_data(self):
        """Retorna los datos del formulario"""
        data = {
            'nombre': self.nombre_input.text().strip(),
            'color_hex': self.color_input.text(),
            'orden': self.orden_input.value(),
            'descripcion': self.descripcion_input.toPlainText().strip() or None
        }
        
        if hasattr(self, 'activo_check'):
            data['activo'] = self.activo_check.isChecked()
        
        return data

