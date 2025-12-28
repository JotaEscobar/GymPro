# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QLabel, 
                             QFileDialog, QMessageBox, QWidget, QComboBox, QLineEdit,
                             QFormLayout, QDoubleSpinBox, QSpinBox, QAbstractSpinBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QCursor
from services.producto_service import ProductoService
from services.proveedor_service import ProveedorService
from services.inventario_service import InventarioService
from ui.proveedores_dialog import ProveedoresDialog

class InventarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📦 Gestión de Inventario")
        self.setMinimumSize(1100, 700)
        self.service = ProductoService()
        self.prov_service = ProveedorService()
        self.inv_service = InventarioService()
        self.filter_low_stock = False
        
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: white; }
            QTableWidget { background-color: #1e293b; color: white; border: 1px solid #334155; }
            QPushButton { background-color: #3b82f6; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold; }
            QLabel { color: #e2e8f0; }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox { 
                background-color: #1e293b; color: white; padding: 6px; 
                border: 1px solid #475569; border-radius: 4px; 
            }
        """)
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        h = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("🔎 Buscar...")
        self.inp_search.textChanged.connect(self._load_data)
        h.addWidget(self.inp_search, 2)
        
        self.combo_cat = QComboBox()
        self.combo_cat.addItem("Todas", None)
        cats = self.service.get_categorias()
        for c in cats: self.combo_cat.addItem(c[1], c[0])
        self.combo_cat.currentIndexChanged.connect(self._load_data)
        h.addWidget(self.combo_cat, 1)
        h.addSpacing(20)
        
        btn_n = QPushButton("➕ Nuevo")
        btn_n.setStyleSheet("background-color: #10b981;")
        btn_n.clicked.connect(lambda: self._open_form(None))
        h.addWidget(btn_n)
        
        btn_xl = QPushButton("📤 Carga Masiva")
        btn_xl.setStyleSheet("background-color: #f59e0b; color: black;")
        btn_xl.clicked.connect(self._importar_excel)
        h.addWidget(btn_xl)
        
        btn_pv = QPushButton("🚚 Proveedores")
        btn_pv.setStyleSheet("background-color: #6366f1;")
        btn_pv.clicked.connect(self._open_proveedores)
        h.addWidget(btn_pv)
        layout.addLayout(h)
        
        # Banner Alerta
        self.alert = QFrame()
        self.alert.setStyleSheet("background: #f59e0b; border-radius: 4px; margin: 5px 0;")
        self.alert.setVisible(False)
        self.alert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.alert.mouseDoubleClickEvent = self._toggle_filter
        l = QHBoxLayout(self.alert)
        l.setContentsMargins(10,5,10,5)
        self.lbl_alert = QLabel("⚠️ Alerta")
        self.lbl_alert.setStyleSheet("color: black; font-weight: bold;")
        l.addWidget(self.lbl_alert)
        layout.addWidget(self.alert)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Producto", "Categoría", "Costo", "Precio", "Stock", "Estado", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_table_click)
        layout.addWidget(self.table)

    def _load_data(self):
        term = self.inp_search.text().lower()
        cid = self.combo_cat.currentData()
        
        if term: prods = self.service.search_productos(term)
        else: prods = self.service.get_all_productos()
        
        if cid: prods = [p for p in prods if p[4] == cid]
        
        low = sum(1 for p in prods if p[7] <= p[8])
        if low > 0:
            self.alert.setVisible(True)
            self.lbl_alert.setText(f"⚠️ {low} productos bajo stock (Doble clic para filtrar)")
        else: self.alert.setVisible(False)
        
        if self.filter_low_stock:
            prods = [p for p in prods if p[7] <= p[8]]
            self.lbl_alert.setText("⚠️ Mostrando solo bajo stock (Doble clic para quitar filtro)")
            
        self.table.setRowCount(0)
        for r, p in enumerate(prods):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(p[3]))
            self.table.setItem(r, 1, QTableWidgetItem(p[5]))
            costo = p[12] if len(p)>12 else 0
            self.table.setItem(r, 2, QTableWidgetItem(f"S/ {costo:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"S/ {p[6]:.2f}"))
            
            st = QTableWidgetItem(str(p[7]))
            st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if p[7]<=0: st.setForeground(QColor("#ef4444"))
            elif p[7]<=p[8]: st.setForeground(QColor("#f59e0b"))
            self.table.setItem(r, 4, st)
            self.table.setItem(r, 5, QTableWidgetItem("Activo" if p[10] else "Inactivo"))
            
            # Botones Acciones
            w = QWidget()
            wl = QHBoxLayout(w)
            wl.setContentsMargins(0,0,0,0)
            btn_adj = QPushButton("⚡ Ajuste")
            btn_adj.setStyleSheet("background: #0ea5e9; font-size: 11px; padding: 4px;")
            btn_adj.clicked.connect(lambda ch, pd=p: self._open_adjustment(pd))
            
            btn_hist = QPushButton("📜")
            btn_hist.setToolTip("Ver Kardex")
            btn_hist.setStyleSheet("background: #64748b; padding: 4px;")
            btn_hist.clicked.connect(lambda ch, pid=p[0]: self._show_kardex(pid))
            
            wl.addWidget(btn_adj)
            wl.addWidget(btn_hist)
            self.table.setCellWidget(r, 6, w)
            
            self.table.item(r, 0).setData(Qt.ItemDataRole.UserRole, p)

    def _toggle_filter(self, e):
        self.filter_low_stock = not self.filter_low_stock
        self._load_data()

    def _on_table_click(self):
        row = self.table.currentRow()
        if row < 0: return
        self._open_form(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))

    def _open_form(self, p_data):
        dlg = QDialog(self)
        dlg.setWindowTitle("Producto")
        dlg.setFixedSize(500, 550)
        dlg.setStyleSheet(self.styleSheet())
        f = QFormLayout(dlg)
        
        inp_nom = QLineEdit(p_data[3] if p_data else "")
        combo_cat = QComboBox()
        for c in self.service.get_categorias(): combo_cat.addItem(c[1], c[0])
        if p_data: 
            idx = combo_cat.findData(p_data[4])
            if idx>=0: combo_cat.setCurrentIndex(idx)
            
        combo_prov = QComboBox()
        combo_prov.addItem("Sin Proveedor", None)
        for pr in self.prov_service.get_all(): combo_prov.addItem(pr[1], pr[0])
        if p_data and len(p_data)>13:
            idx = combo_prov.findData(p_data[13])
            if idx>=0: combo_prov.setCurrentIndex(idx)
            
        def mk_spin(float_val=False):
            s = QDoubleSpinBox() if float_val else QSpinBox()
            s.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            if float_val: s.setRange(0, 99999.99)
            else: s.setRange(0, 99999)
            return s
            
        s_costo = mk_spin(True)
        s_costo.setValue(p_data[12] if p_data and len(p_data)>12 else 0)
        s_precio = mk_spin(True)
        s_precio.setValue(p_data[6] if p_data else 0)
        s_stock = mk_spin(False)
        s_stock.setValue(p_data[7] if p_data else 0)
        if p_data: s_stock.setEnabled(False)
        s_min = mk_spin(False)
        s_min.setValue(p_data[8] if p_data else 0)
        
        inp_bar = QLineEdit(p_data[2] if p_data else "")
        
        # Orden Excel
        f.addRow("Nombre:", inp_nom)
        f.addRow("Categoría:", combo_cat)
        f.addRow("Precio Venta:", s_precio)
        f.addRow("Stock Inicial:", s_stock)
        f.addRow("Stock Mínimo:", s_min)
        f.addRow("Cód. Barras:", inp_bar)
        f.addRow("Costo Compra:", s_costo)
        f.addRow("Proveedor:", combo_prov)
        
        btn = QPushButton("Guardar")
        btn.clicked.connect(lambda: self._save(dlg, p_data, inp_nom, combo_cat, s_precio, s_stock, s_min, inp_bar, s_costo, combo_prov))
        f.addRow(btn)
        dlg.exec()

    def _save(self, dlg, p_data, nom, cat, prec, st, min_st, bar, cost, prov):
        if not nom.text(): return
        args = {
            'nombre': nom.text(), 'categoria_id': cat.currentData(),
            'precio': prec.value(), 'stock_minimo': min_st.value(),
            'codigo_barras': bar.text(), 'precio_compra': cost.value(),
            'proveedor_id': prov.currentData()
        }
        if p_data:
            res = self.service.update_producto(p_data[0], **args)
        else:
            args['stock_inicial'] = st.value()
            res = self.service.create_producto(**args)
            
        if res.success:
            dlg.accept()
            self._load_data()
        else: QMessageBox.critical(dlg, "Error", res.message)

    def _open_adjustment(self, p_data):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Ajuste: {p_data[3]}")
        dlg.setFixedSize(300, 250)
        dlg.setStyleSheet(self.styleSheet())
        l = QVBoxLayout(dlg)
        
        l.addWidget(QLabel(f"Stock Actual: {p_data[7]}"))
        
        c_tipo = QComboBox()
        c_tipo.addItems(["Entrada (Compra/Devolución)", "Salida (Merma/Uso)"])
        l.addWidget(c_tipo)
        
        spin = QSpinBox()
        spin.setRange(1, 9999)
        l.addWidget(QLabel("Cantidad:"))
        l.addWidget(spin)
        
        motivo = QLineEdit()
        motivo.setPlaceholderText("Motivo del ajuste...")
        l.addWidget(motivo)
        
        btn = QPushButton("Aplicar Ajuste")
        l.addWidget(btn)
        
        def apply():
            tipo = "entrada" if c_tipo.currentIndex() == 0 else "salida"
            res = self.inv_service.registrar_movimiento(
                p_data[0], tipo, spin.value(), motivo.text(), "ajuste_manual"
            )
            if res.success:
                QMessageBox.information(dlg, "Éxito", "Stock actualizado")
                dlg.accept()
                self._load_data()
            else: QMessageBox.critical(dlg, "Error", res.message)
            
        btn.clicked.connect(apply)
        dlg.exec()

    def _show_kardex(self, pid):
        dlg = QDialog(self)
        dlg.setWindowTitle("Kardex Producto")
        dlg.setFixedSize(600, 400)
        dlg.setStyleSheet(self.styleSheet())
        l = QVBoxLayout(dlg)
        
        t = QTableWidget()
        t.setColumnCount(4)
        t.setHorizontalHeaderLabels(["Fecha", "Tipo", "Cant", "Motivo"])
        t.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        l.addWidget(t)
        
        movs = self.inv_service.get_movimientos_producto(pid)
        t.setRowCount(0)
        for r, m in enumerate(movs):
            t.insertRow(r)
            t.setItem(r, 0, QTableWidgetItem(m[0]))
            t.setItem(r, 1, QTableWidgetItem(m[1].upper()))
            t.setItem(r, 2, QTableWidgetItem(str(m[2])))
            t.setItem(r, 3, QTableWidgetItem(m[5]))
        dlg.exec()

    def _importar_excel(self):
        QMessageBox.information(self, "Info", "Columnas requeridas:\nNombre, Categoria, PrecioVenta, Stock, Minimo, Barras, PrecioCompra, Proveedor")
        path, _ = QFileDialog.getOpenFileName(self, "Excel", "", "*.xlsx")
        if path:
            self.service.importar_productos_masivo(path)
            self._load_data()

    def _open_proveedores(self):
        ProveedoresDialog(self).exec()