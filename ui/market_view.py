# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox, QHeaderView, 
    QFrame, QAbstractItemView, QDialog, QScrollArea, QStackedWidget,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QKeySequence, QShortcut

from services.producto_service import ProductoService
from services.venta_service import VentaService
from services.member_service import MemberService
from services.benefit_service import BenefitService
from services.caja_service import CajaService
from ui.inventario_dialog import InventarioDialog
from ui.historial_ventas_dialog import HistorialVentasDialog

class MarketView(QWidget):
    def __init__(self):
        super().__init__()
        self.producto_service = ProductoService()
        self.venta_service = VentaService()
        self.member_service = MemberService()
        self.benefit_service = BenefitService()
        self.caja_service = CajaService()
        
        self.carrito = [] 
        self.cliente_actual = None 
        self.descuento_global = 0
        self.categoria_activa = None
        
        # Stack: 0=Bloqueo, 1=Venta
        self.stack = QStackedWidget()
        self._setup_locked_screen()
        self._setup_market_screen()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.stack)
        
        # Atajos de Teclado (Funcionan en toda la ventana)
        self.shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        self.shortcut_f2.activated.connect(self._open_inventario)
        
        self.shortcut_f3 = QShortcut(QKeySequence("F3"), self)
        self.shortcut_f3.activated.connect(self._open_historial)
        
        self.shortcut_enter = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.shortcut_enter.activated.connect(self._cobrar)
        
        self.shortcut_enter2 = QShortcut(QKeySequence(Qt.Key.Key_Enter), self) # Numpad Enter
        self.shortcut_enter2.activated.connect(self._cobrar)

        # Timer Caja
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_caja)
        self.timer.start(2000)
        self._check_caja()

    def _setup_locked_screen(self):
        p = QWidget()
        p.setStyleSheet("background: #0f172a;")
        l = QVBoxLayout(p)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("🔒")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        txt = QLabel("CAJA CERRADA")
        txt.setStyleSheet("font-size: 24px; font-weight: bold; color: #ef4444; margin-top: 15px;")
        txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub = QLabel("Abra turno en el módulo 'Caja' para vender.")
        sub.setStyleSheet("font-size: 14px; color: #94a3b8;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        l.addWidget(icon)
        l.addWidget(txt)
        l.addWidget(sub)
        self.stack.addWidget(p)

    def _setup_market_screen(self):
        p = QWidget()
        main = QVBoxLayout(p)
        main.setContentsMargins(10,10,10,10)
        main.setSpacing(10)
        
        # Toolbar
        top = QHBoxLayout()
        t = QLabel("🛒 Punto de Venta")
        t.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        top.addWidget(t)
        top.addStretch()
        
        b_inv = QPushButton("📦 Inventario (F2)")
        b_inv.setStyleSheet("background: #334155; color: white; padding: 6px 12px; border-radius: 4px;")
        b_inv.clicked.connect(self._open_inventario)
        
        b_his = QPushButton("📜 Historial (F3)")
        b_his.setStyleSheet("background: #334155; color: white; padding: 6px 12px; border-radius: 4px;")
        b_his.clicked.connect(self._open_historial)
        
        top.addWidget(b_inv)
        top.addWidget(b_his)
        main.addLayout(top)
        
        # Area Trabajo
        work = QHBoxLayout()
        
        # --- IZQUIERDA ---
        left = QVBoxLayout()
        
        # Buscador
        search_f = QFrame()
        search_f.setStyleSheet("background: #1e293b; border-radius: 6px;")
        sl = QHBoxLayout(search_f)
        sl.setContentsMargins(5,2,5,2)
        sl.addWidget(QLabel("🔍"))
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Buscar producto...")
        self.inp_search.setStyleSheet("border:none; background:transparent; color:white; font-size:14px;")
        self.inp_search.textChanged.connect(self._filtrar)
        sl.addWidget(self.inp_search)
        left.addWidget(search_f)
        
        # Categorías
        self.cat_area = QWidget()
        self.cat_layout = QHBoxLayout(self.cat_area)
        self.cat_layout.setContentsMargins(0,0,0,0)
        self.cat_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(40)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setWidget(self.cat_area)
        left.addWidget(scroll)
        
        # Tabla Catalogo (Con SKU)
        self.table_cat = QTableWidget()
        self.table_cat.setColumnCount(5)
        self.table_cat.setHorizontalHeaderLabels(["SKU", "Producto", "Precio", "Stock", ""])
        self.table_cat.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_cat.verticalHeader().setVisible(False)
        self.table_cat.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_cat.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_cat.doubleClicked.connect(self._add_cart)
        self.table_cat.setStyleSheet("QTableWidget { background: #0f172a; border: 1px solid #334155; border-radius: 6px; }")
        self.table_cat.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.table_cat)
        
        # Panel Atajos
        info = QFrame()
        info.setStyleSheet("background: #1e293b; border-radius: 6px; padding: 5px;")
        il = QHBoxLayout(info)
        il.addWidget(QLabel("⌨️ <b>F2:</b> Inventario  |  <b>F3:</b> Historial  |  <b>Enter:</b> Cobrar"))
        left.addWidget(info)
        
        work.addLayout(left, 65)
        
        # --- DERECHA (POS) ---
        right = QVBoxLayout()
        
        # Cliente
        card = QFrame()
        card.setStyleSheet("background: #1e293b; border-radius: 6px;")
        cl = QVBoxLayout(card)
        self.lbl_cli = QLabel("Visitante")
        self.lbl_cli.setStyleSheet("font-size: 16px; font-weight: bold; color: #facc15;")
        btn_cli = QPushButton("Cambiar / Buscar")
        btn_cli.setStyleSheet("background: #334155; border: 1px solid #475569; padding: 4px; color: #cbd5e1;")
        btn_cli.clicked.connect(self._buscar_cliente)
        self.lbl_desc = QLabel("Sin descuentos")
        self.lbl_desc.setStyleSheet("color: #64748b; font-size: 11px;")
        
        cl.addWidget(QLabel("Cliente Actual:"))
        cl.addWidget(self.lbl_cli)
        cl.addWidget(self.lbl_desc)
        cl.addWidget(btn_cli)
        right.addWidget(card)
        
        # Carrito
        self.table_cart = QTableWidget()
        self.table_cart.setColumnCount(4)
        self.table_cart.setHorizontalHeaderLabels(["Prod", "Cant", "Total", ""])
        self.table_cart.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_cart.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table_cart.setColumnWidth(3, 30)
        self.table_cart.verticalHeader().setVisible(False)
        self.table_cart.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_cart.setStyleSheet("background: #1e293b; border: none; border-radius: 6px;")
        right.addWidget(self.table_cart)
        
        # Panel Pago
        pay = QFrame()
        pay.setStyleSheet("background: #0f172a; border-top: 2px solid #334155;")
        pl = QVBoxLayout(pay)
        
        self.lbl_total = QLabel("S/ 0.00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_total.setStyleSheet("font-size: 32px; font-weight: bold; color: #22c55e;")
        pl.addWidget(self.lbl_total)
        
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Efectivo", "Yape", "Plin", "POS/Banco"])
        self.combo_metodo.setStyleSheet("padding: 8px; background: #334155; color: white;")
        pl.addWidget(self.combo_metodo)
        
        # Botones Acción
        btn_row = QHBoxLayout()
        
        btn_clean = QPushButton("🗑️ Limpiar")
        btn_clean.setFixedHeight(50)
        btn_clean.setStyleSheet("background: #ef4444; color: white; font-weight: bold; border-radius: 6px;")
        btn_clean.clicked.connect(self._limpiar_todo)
        
        btn_pay = QPushButton("COBRAR")
        btn_pay.setFixedHeight(50)
        btn_pay.setStyleSheet("background: #3b82f6; color: white; font-size: 18px; font-weight: bold; border-radius: 6px;")
        btn_pay.clicked.connect(self._cobrar)
        
        btn_row.addWidget(btn_clean, 1)
        btn_row.addWidget(btn_pay, 3)
        pl.addLayout(btn_row)
        
        right.addWidget(pay)
        work.addLayout(right, 35)
        
        main.addLayout(work)
        self.stack.addWidget(p)
        
        self._load_cats()
        self._load_top10()

    # --- LÓGICA ---
    def _check_caja(self):
        is_open = self.caja_service.get_sesion_abierta() is not None
        self.stack.setCurrentIndex(1 if is_open else 0)

    def _load_cats(self):
        # Limpiar
        while self.cat_layout.count():
            item = self.cat_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        cats = self.producto_service.get_categorias()
        # Ordenar Otros al final
        otros = [c for c in cats if "otro" in c[1].lower()]
        norm = [c for c in cats if "otro" not in c[1].lower()]
        final_cats = norm + otros
        
        self._add_cat_btn("Todo", None, True)
        for c in final_cats:
            self._add_cat_btn(c[1], c[0], False)
        self.cat_layout.addStretch()

    def _add_cat_btn(self, text, cid, active):
        lbl = QLabel(text)
        lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        style = "padding: 5px; font-size: 14px;"
        if active: style += " font-weight: bold; color: #3b82f6; border-bottom: 2px solid #3b82f6;"
        else: style += " color: #94a3b8;"
        lbl.setStyleSheet(style)
        lbl.mousePressEvent = lambda e: self._set_cat(cid, lbl)
        self.cat_layout.addWidget(lbl)

    def _set_cat(self, cid, lbl):
        self.categoria_activa = cid
        # Reset estilos
        for i in range(self.cat_layout.count()):
            w = self.cat_layout.itemAt(i).widget()
            if isinstance(w, QLabel):
                w.setStyleSheet("padding: 5px; font-size: 14px; color: #94a3b8;")
        
        lbl.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold; color: #3b82f6; border-bottom: 2px solid #3b82f6;")
        
        if cid is None: self._load_top10()
        else:
            prods = self.producto_service.get_all_productos()
            filtered = [p for p in prods if p[4] == cid]
            self._fill_table(filtered)

    def _load_top10(self):
        prods = self.venta_service.get_productos_mas_vendidos(limit=20)
        if not prods:
            prods = self.producto_service.get_all_productos()[:20]
        else:
            ids = [p[0] for p in prods]
            all_p = self.producto_service.get_all_productos()
            prods = [p for p in all_p if p[0] in ids]
        self._fill_table(prods)

    def _filtrar(self, txt):
        if not txt:
            if self.categoria_activa: return
            self._load_top10()
            return
        prods = self.producto_service.search_productos(txt)
        self._fill_table(prods)

    def _fill_table(self, prods):
        self.table_cat.setRowCount(0)
        for r, p in enumerate(prods):
            self.table_cat.insertRow(r)
            # SKU (0), Nombre (1), Precio (2), Stock (3), Btn (4)
            self.table_cat.setItem(r, 0, QTableWidgetItem(str(p[1]))) # SKU
            self.table_cat.setItem(r, 1, QTableWidgetItem(p[3]))
            self.table_cat.setItem(r, 2, QTableWidgetItem(f"S/ {p[6]:.2f}"))
            
            st = QTableWidgetItem(str(p[7]))
            if p[7] <= p[8]: st.setForeground(QColor("#ef4444"))
            self.table_cat.setItem(r, 3, st)
            
            add = QTableWidgetItem("➕")
            add.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_cat.setItem(r, 4, add)
            
            self.table_cat.item(r, 0).setData(Qt.ItemDataRole.UserRole, p)

    def _add_cart(self):
        row = self.table_cat.currentRow()
        if row < 0: return
        p = self.table_cat.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if p[7] <= 0: return
        
        for item in self.carrito:
            if item['data'][0] == p[0]:
                item['cant'] += 1
                self._render_cart()
                return
        
        self.carrito.append({'data': p, 'cant': 1})
        self._render_cart()

    def _render_cart(self):
        self.table_cart.setRowCount(0)
        tot = 0
        for r, item in enumerate(self.carrito):
            self.table_cart.insertRow(r)
            p = item['data']
            cant = item['cant']
            price = p[6] * (1 - self.descuento_global/100)
            sub = price * cant
            tot += sub
            
            self.table_cart.setItem(r, 0, QTableWidgetItem(p[3]))
            self.table_cart.setItem(r, 1, QTableWidgetItem(str(cant)))
            self.table_cart.setItem(r, 2, QTableWidgetItem(f"{sub:.2f}"))
            
            btn = QPushButton("(-)")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("color: #ef4444; border:none; font-weight:bold;")
            btn.clicked.connect(lambda ch, idx=r: self._del_item(idx))
            self.table_cart.setCellWidget(r, 3, btn)
            
        self.lbl_total.setText(f"S/ {tot:.2f}")

    def _del_item(self, idx):
        self.carrito.pop(idx)
        self._render_cart()

    def _limpiar_todo(self):
        if not self.carrito: return
        if QMessageBox.question(self, "Limpiar", "¿Borrar todo?") == QMessageBox.StandardButton.Yes:
            self.carrito = []
            self.cliente_actual = None
            self.descuento_global = 0
            self.lbl_cli.setText("Visitante")
            self.lbl_desc.setText("Sin descuentos")
            self._render_cart()

    def _cobrar(self):
        if not self.carrito: return
        if not self.caja_service.get_sesion_abierta():
            QMessageBox.warning(self, "Caja Cerrada", "No se puede vender.")
            return
            
        items = []
        tot = 0
        for i in self.carrito:
            p = i['data']
            cant = i['cant']
            price = p[6]
            desc = self.descuento_global
            sub = (price * (1 - desc/100)) * cant
            tot += sub
            items.append({
                'producto_id': p[0], 'cantidad': cant, 'precio_unit': price,
                'descuento_porcentaje': desc, 'subtotal': sub
            })
            
        cli_type = 'miembro' if self.cliente_actual else 'visitante'
        cli_id = self.cliente_actual[0] if self.cliente_actual else None
        metodo = {"Efectivo":"efectivo", "Yape":"yape", "Plin":"plin", "POS/Banco":"pos_banco"}[self.combo_metodo.currentText()]
        
        res = self.venta_service.procesar_venta(cli_type, cli_id, tot, metodo, items)
        
        if res.success:
            QMessageBox.information(self, "Éxito", "Venta registrada")
            self.carrito = []
            self._render_cart()
            self._load_top10()
        else:
            QMessageBox.critical(self, "Error", res.message)

    def _buscar_cliente(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Buscar")
        l = QVBoxLayout(dlg)
        inp = QLineEdit()
        inp.setPlaceholderText("DNI")
        l.addWidget(inp)
        btn = QPushButton("Buscar")
        l.addWidget(btn)
        
        def buscar():
            m = self.member_service.find_member_by_identifier(inp.text())
            if m:
                self.cliente_actual = m
                self.lbl_cli.setText(m[1])
                benefits = self.benefit_service.get_member_benefits(m[0])
                for b in benefits:
                    if b['config'].get('enabled') and 'market' in b.get('nombre','').lower():
                        self.descuento_global = b['config'].get('descuento_porcentaje', 0)
                self.lbl_desc.setText(f"Desc: {self.descuento_global}%")
                self._render_cart()
                dlg.accept()
            else: QMessageBox.warning(dlg, "Error", "No encontrado")
            
        btn.clicked.connect(buscar)
        dlg.exec()

    def _open_inventario(self):
        InventarioDialog(self).exec()
        self._load_top10()

    def _open_historial(self):
        HistorialVentasDialog(self).exec()
        self._load_top10()