# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QComboBox, 
                             QMessageBox, QHeaderView, QFormLayout, QLabel)
from PyQt6.QtCore import Qt
from services.proveedor_service import ProveedorService

class ProveedoresDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Proveedores")
        self.setMinimumSize(900, 600)
        self.service = ProveedorService()
        self._setup_ui()
        self._load_data()
        
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: white; }
            QLineEdit, QComboBox { background-color: #1e293b; color: white; border: 1px solid #334155; padding: 6px; }
            QTableWidget { background-color: #1e293b; color: white; border: 1px solid #334155; }
            QPushButton { background-color: #3b82f6; color: white; padding: 8px; border-radius: 4px; font-weight: bold; }
        """)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Filtros
        top = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("🔎 Buscar proveedor...")
        self.inp_search.textChanged.connect(self._load_data)
        top.addWidget(self.inp_search, 2)
        
        self.combo_cat = QComboBox()
        self.combo_cat.addItem("Todas las categorías", None)
        # Aquí idealmente cargarías categorías únicas de la BD, por ahora simple:
        top.addWidget(self.combo_cat, 1)
        
        btn_reg = QPushButton("➕ Nuevo")
        btn_reg.setStyleSheet("background-color: #10b981;")
        btn_reg.clicked.connect(lambda: self._open_form())
        top.addWidget(btn_reg)
        layout.addLayout(top)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Empresa", "RUC", "Teléfono", "Categoría", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self.table)
        
        # Eliminar
        btn_del = QPushButton("🗑️ Desactivar Seleccionado")
        btn_del.setStyleSheet("background-color: #ef4444;")
        btn_del.clicked.connect(self._delete_selected)
        layout.addWidget(btn_del)

    def _load_data(self):
        rows = self.service.get_all()
        term = self.inp_search.text().lower()
        
        # Filtrado en memoria
        if term:
            rows = [r for r in rows if term in r[1].lower() or (r[2] and term in r[2])]
            
        self.table.setRowCount(0)
        categories = set()
        
        for r, row in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(row[1]))
            self.table.setItem(r, 1, QTableWidgetItem(row[2] or "-"))
            self.table.setItem(r, 2, QTableWidgetItem(row[4] or "-"))
            cat = row[7] or "General"
            categories.add(cat)
            self.table.setItem(r, 3, QTableWidgetItem(cat))
            self.table.setItem(r, 4, QTableWidgetItem("Activo"))
            self.table.item(r, 0).setData(Qt.ItemDataRole.UserRole, row)
            
        # Actualizar combo si es primera carga
        if self.combo_cat.count() == 1:
            for c in sorted(list(categories)): self.combo_cat.addItem(c, c)

    def _on_edit(self):
        row = self.table.currentRow()
        if row < 0: return
        data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self._open_form(data)

    def _open_form(self, data=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Proveedor")
        dialog.setFixedSize(400, 400)
        dialog.setStyleSheet(self.styleSheet())
        form = QFormLayout(dialog)
        
        inp_empresa = QLineEdit(data[1] if data else "")
        inp_ruc = QLineEdit(data[2] if data else "")
        inp_contacto = QLineEdit(data[3] if data else "")
        inp_telefono = QLineEdit(data[4] if data else "")
        inp_email = QLineEdit(data[5] if data else "")
        inp_dir = QLineEdit(data[6] if data else "")
        inp_cat = QLineEdit(data[7] if data else "")
        
        form.addRow("Empresa *:", inp_empresa)
        form.addRow("RUC:", inp_ruc)
        form.addRow("Contacto:", inp_contacto)
        form.addRow("Teléfono:", inp_telefono)
        form.addRow("Email:", inp_email)
        form.addRow("Dirección:", inp_dir)
        form.addRow("Categoría:", inp_cat)
        
        hbox = QHBoxLayout()
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(lambda: self._save(dialog, data[0] if data else None, {
            'empresa': inp_empresa.text(), 'ruc': inp_ruc.text(), 
            'contacto': inp_contacto.text(), 'telefono': inp_telefono.text(),
            'email': inp_email.text(), 'direccion': inp_dir.text(), 'categoria': inp_cat.text()
        }))
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #64748b;")
        btn_cancel.clicked.connect(dialog.reject)
        
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_cancel)
        form.addRow(hbox)
        dialog.exec()

    def _save(self, dlg, pid, data):
        res = self.service.guardar_proveedor(pid, data)
        if res.success:
            dlg.accept()
            self._load_data()
        else: QMessageBox.critical(dlg, "Error", res.message)

    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0: return
        pid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)[0]
        
        if QMessageBox.question(self, "Confirmar", 
            "¿Desactivar proveedor?") == QMessageBox.StandardButton.Yes:
            self.service.eliminar_proveedor(pid)
            self._load_data()