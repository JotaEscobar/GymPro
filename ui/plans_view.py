# -*- coding: utf-8 -*-
"""
Vista de gestión de planes y tarifas
"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from services.plan_service import PlanService
from PyQt6.QtWidgets import QTabWidget
from ui.categories_tab import CategoriesTab

class PlansView(QWidget):
    """Vista para CRUD de planes/tarifas"""
    
    def __init__(self):
        super().__init__()
        self.service = PlanService()
        self.editing_plan_id = None
        self.layout = QVBoxLayout(self)
        
        # Crear tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #334155;
                border-radius: 8px;
                background: #1e293b;
            }
            QTabBar::tab {
                padding: 12px 24px;
                margin-right: 4px;
                background: #0f172a;
                color: #94a3b8;
                border: 1px solid #334155;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: #1e293b;
                color: #f1f5f9;
                border-bottom: 2px solid #3b82f6;
            }
            QTabBar::tab:hover {
                background: #1e293b;
                color: #cbd5e1;
            }
        """)
        
        # Tab 1: Planes (contenido actual)
        plans_widget = QWidget()
        plans_layout = QVBoxLayout(plans_widget)
        
        self._setup_form_group_in_layout(plans_layout)
        self._setup_table_in_layout(plans_layout)
        
        self.tab_widget.addTab(plans_widget, "📋 Planes")
        
        # Tab 2: Categorías
        self.categories_tab = CategoriesTab(self)
        self.categories_tab.category_changed.connect(self.load_plans)
        self.tab_widget.addTab(self.categories_tab, "🏷️ Categorías")
        
        # Agregar tab widget al layout principal
        self.layout.addWidget(self.tab_widget)
        
        # Cargar datos
        self.load_plans()

    def _load_categories_combo(self):
        """Carga las categorías en el combobox"""
        from services.category_service import CategoryService
        
        category_service = CategoryService()
        categories = category_service.get_all_categories()
        
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Sin categoría", None)
        
        for cat in categories:
            self.combo_categoria.addItem(
                f"{cat['nombre']}",
                cat['id']
            )

    def _setup_form_group_in_layout(self, parent_layout):
        """Formulario de creación/edición"""
        form_group = QGroupBox("➕ Crear / ✏️ Editar Plan/Tarifa")
        form_layout = QGridLayout()
        form_group.setLayout(form_layout)

        # FILA 1: Nombre | Precio
        form_layout.addWidget(QLabel("Nombre del Plan:"), 0, 0)
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: Membresía Mensual Estándar")
        form_layout.addWidget(self.input_nombre, 0, 1)

        form_layout.addWidget(QLabel("Precio (Soles):"), 0, 2)
        self.input_precio = QLineEdit()
        self.input_precio.setPlaceholderText("Ej: 60.00")
        form_layout.addWidget(self.input_precio, 0, 3)

        # FILA 2: Duración | Personas Combo
        form_layout.addWidget(QLabel("Duración (Días):"), 1, 0)
        self.input_dias = QLineEdit()
        self.input_dias.setPlaceholderText("Ej: 30")
        form_layout.addWidget(self.input_dias, 1, 1)

        form_layout.addWidget(QLabel("Personas (Combo):"), 1, 2)
        self.input_personas = QLineEdit()
        self.input_personas.setPlaceholderText("Ej: 1")
        form_layout.addWidget(self.input_personas, 1, 3)

        # FILA 3: Venta Inicio | Venta Fin
        form_layout.addWidget(QLabel("Venta (Inicio):"), 2, 0)
        self.input_fecha_inicio = QDateEdit(calendarPopup=True)
        self.input_fecha_inicio.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_inicio.setDate(QDate.currentDate())
        form_layout.addWidget(self.input_fecha_inicio, 2, 1)
        
        form_layout.addWidget(QLabel("Venta (Fin):"), 2, 2)
        self.input_fecha_fin = QDateEdit(calendarPopup=True)
        self.input_fecha_fin.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_fin.setDate(QDate.currentDate().addYears(1))
        form_layout.addWidget(self.input_fecha_fin, 2, 3)

        # FILA 4: Categoría | Activo
        form_layout.addWidget(QLabel("Categoría:"), 3, 0)
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Sin categoría", None)
        self._load_categories_combo()
        form_layout.addWidget(self.combo_categoria, 3, 1)
        
        self.checkbox_activo = QCheckBox("Activo")
        self.checkbox_activo.setChecked(True)
        self.checkbox_activo.setStyleSheet("""
            QCheckBox {
                font-weight: 500;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #cbd5e1;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #22c55e;
                border-color: #22c55e;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)
        form_layout.addWidget(self.checkbox_activo, 3, 2)

        # FILA 5: Descripción (span 3 columnas)
        form_layout.addWidget(QLabel("Descripción:"), 4, 0)
        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Notas adicionales")
        form_layout.addWidget(self.input_descripcion, 4, 1, 1, 3)

        # Botones
        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Crear Plan")
        self.btn_save.setStyleSheet("background-color: #38a169; color: white; font-weight: bold; padding: 10px;")
        self.btn_save.clicked.connect(self.save_plan)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        
        form_layout.addLayout(button_layout, 5, 0, 1, 4)
        
        parent_layout.addWidget(form_group)
        parent_layout.addSpacing(10)

    def _setup_table_in_layout(self, parent_layout):
        """Tabla de planes existentes"""
        label = QLabel("📋 Planes y Tarifas Existentes")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        parent_layout.addWidget(label)

        self.table = QTableWidget()
        self.table.setColumnCount(10)  # Una columna más
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Precio", "Días", "Personas", "Categoría",
            "Inicio", "Fin", "Descripción", "Estado"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.start_edit_plan)
        
        parent_layout.addWidget(self.table)
        
        # Botón eliminar
        action_layout = QHBoxLayout()
        self.btn_delete = QPushButton("🗑️ Eliminar Plan Seleccionado")
        self.btn_delete.setStyleSheet("background-color: #e53e3e; color: white;")
        self.btn_delete.clicked.connect(self.delete_plan)
        
        action_layout.addStretch(1)
        action_layout.addWidget(self.btn_delete)
        self.layout.addLayout(action_layout)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        """Muestra/oculta el botón eliminar según la pestaña activa"""
        # index 0 = Planes, index 1 = Categorías
        if index == 0:
            self.btn_delete.setVisible(True)
        else:
            self.btn_delete.setVisible(False)

    def load_plans(self):
        """Carga planes en la tabla"""
        planes = self.service.get_all_plans(include_inactive=True) 
        self.table.setRowCount(0)
        
        for row_number, plan in enumerate(planes):
            self.table.insertRow(row_number)
            # Ahora hay 10 columnas (se agregó categoria_id)
            plan_id, nombre, precio, dias, personas, inicio, fin, desc, estado, categoria_id = plan
            
            estado_texto = "Activo" if estado == 1 else "Inactivo"
            
            self.table.setItem(row_number, 0, QTableWidgetItem(str(plan_id)))
            self.table.setItem(row_number, 1, QTableWidgetItem(nombre))
            self.table.setItem(row_number, 2, QTableWidgetItem(f"S/ {precio:.2f}"))
            self.table.setItem(row_number, 3, QTableWidgetItem(str(dias)))
            self.table.setItem(row_number, 4, QTableWidgetItem(str(personas)))
            if categoria_id:
                from services.category_service import CategoryService
                from PyQt6.QtGui import QColor, QFont
                
                cat_service = CategoryService()
                cat = cat_service.get_category_by_id(categoria_id)
                if cat:
                    cat_item = QTableWidgetItem(cat['nombre'])
                    cat_item.setForeground(QColor(cat['color_hex']))
                    cat_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                    self.table.setItem(row_number, 5, cat_item)
                else:
                    self.table.setItem(row_number, 5, QTableWidgetItem("-"))
            else:
                self.table.setItem(row_number, 5, QTableWidgetItem("-"))
            self.table.setItem(row_number, 6, QTableWidgetItem(str(inicio or "N/A")))
            self.table.setItem(row_number, 7, QTableWidgetItem(str(fin or "N/A")))
            self.table.setItem(row_number, 8, QTableWidgetItem(desc or ""))
            self.table.setItem(row_number, 9, QTableWidgetItem(estado_texto))
            
            if estado == 0:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row_number, col)
                    if item:  # ← AGREGAR esta validación
                        item.setForeground(Qt.GlobalColor.gray)

    def save_plan(self):
        """Guarda nuevo plan o actualiza existente"""
        nombre = self.input_nombre.text()
        precio = self.input_precio.text()
        dias = self.input_dias.text()
        personas = self.input_personas.text()
        inicio = self.input_fecha_inicio.date().toString(Qt.DateFormat.ISODate)
        fin = self.input_fecha_fin.date().toString(Qt.DateFormat.ISODate)
        descripcion = self.input_descripcion.text()
        estado = 1 if self.checkbox_activo.isChecked() else 0
        
        if self.editing_plan_id is None:
            categoria_id = self.combo_categoria.currentData()
            resultado = self.service.create_plan(nombre, precio, dias, personas, inicio, fin, descripcion, categoria_id)
        else:
            categoria_id = self.combo_categoria.currentData()
            resultado = self.service.update_plan(
                self.editing_plan_id, nombre, precio, dias, personas, inicio, fin, descripcion, estado, categoria_id
            )
        

        if resultado.get("success"):
            QMessageBox.information(self, "Éxito", resultado['message'])
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", resultado['message'])
        
        self.load_plans()

    def start_edit_plan(self):
        """Carga plan para edición"""
        selected = self.table.selectedIndexes()
        if not selected:
            return

        row = selected[0].row()
        plan_id = int(self.table.item(row, 0).text())
        
        self.editing_plan_id = plan_id
        self.input_nombre.setText(self.table.item(row, 1).text())
        self.input_precio.setText(self.table.item(row, 2).text().replace("S/ ", ""))
        self.input_dias.setText(self.table.item(row, 3).text())
        self.input_personas.setText(self.table.item(row, 4).text())

                # Cargar categoría del plan
        planes = self.service.get_all_plans(include_inactive=True)
        plan_data = None
        for p in planes:
            if p[0] == plan_id:
                plan_data = p
                break

        if plan_data and plan_data[9]:  # categoria_id
            index = self.combo_categoria.findData(plan_data[9])
            if index >= 0:
                self.combo_categoria.setCurrentIndex(index)
        else:
            self.combo_categoria.setCurrentIndex(0)  # Sin categoría
        
        inicio = self.table.item(row, 6).text()
        fin = self.table.item(row, 7).text()
        if inicio != "N/A":
            self.input_fecha_inicio.setDate(QDate.fromString(inicio, Qt.DateFormat.ISODate))
        if fin != "N/A":
            self.input_fecha_fin.setDate(QDate.fromString(fin, Qt.DateFormat.ISODate))

        self.input_descripcion.setText(self.table.item(row, 8).text())
        self.checkbox_activo.setChecked(self.table.item(row, 9).text() == "Activo")
        
        self.btn_save.setText("✅ Guardar Cambios")
        self.btn_cancel.setVisible(True)

    def clear_form(self):
        """Limpia formulario"""
        self.editing_plan_id = None
        self.input_nombre.clear()
        self.input_precio.clear()
        self.input_dias.clear()
        self.input_personas.clear()
        self.input_descripcion.clear()
        self.input_fecha_inicio.setDate(QDate.currentDate())
        self.input_fecha_fin.setDate(QDate.currentDate().addYears(1))
        self.checkbox_activo.setChecked(True)
        self.combo_categoria.setCurrentIndex(0)  # Reset a "Sin categoría"
        
        self.btn_save.setText("💾 Crear Plan")
        self.btn_cancel.setVisible(False)
        self.table.clearSelection()

    def delete_plan(self):
        """Elimina plan seleccionado"""
        selected = self.table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione un plan")
            return
            
        row = selected[0].row()
        plan_id = int(self.table.item(row, 0).text())
        nombre = self.table.item(row, 1).text()

        if QMessageBox.question(self, 'Confirmar', f"¿Eliminar '{nombre}'?") == QMessageBox.StandardButton.Yes:
            resultado = self.service.delete_plan(plan_id)
            
            if resultado.get("success"):
                QMessageBox.information(self, "Éxito", resultado['message'])
            else:
                QMessageBox.warning(self, "Advertencia", resultado['message'])
            
            self.load_plans()
            self.clear_form()
