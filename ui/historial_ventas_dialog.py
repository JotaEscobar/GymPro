# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QLabel, 
                             QDateEdit, QFrame, QMessageBox, QAbstractItemView, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont
from services.venta_service import VentaService

class HistorialVentasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Ventas")
        self.setMinimumSize(1000, 700)
        self.service = VentaService()
        
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: white; }
            QTableWidget { background-color: #1e293b; color: white; border: 1px solid #334155; }
            QPushButton { background-color: #3b82f6; color: white; padding: 6px 12px; border-radius: 4px; }
            QDateEdit { background-color: #1e293b; color: white; border: 1px solid #475569; padding: 4px; }
        """)
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # KPIs Mejorados (3 tarjetas con mejor proporción)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        self.card_total_frame, self.lbl_total_val = self._create_card("💰 Ventas Periodo", "#22c55e")
        self.card_count_frame, self.lbl_count_val = self._create_card("📊 Transacciones", "#3b82f6")
        self.card_ticket_frame, self.lbl_ticket_val = self._create_card("🎯 Ticket Promedio", "#f59e0b")
        
        kpi_layout.addWidget(self.card_total_frame)
        kpi_layout.addWidget(self.card_count_frame)
        kpi_layout.addWidget(self.card_ticket_frame)
        layout.addLayout(kpi_layout)
        
        # Filtros
        fl = QHBoxLayout()
        fl.addWidget(QLabel("Desde:"))
        self.date_from = QDateEdit(QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        fl.addWidget(self.date_from)
        fl.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        fl.addWidget(self.date_to)
        btn = QPushButton("Filtrar")
        btn.clicked.connect(self._load_data)
        fl.addWidget(btn)
        fl.addStretch()
        layout.addLayout(fl)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Hora", "Cliente", "Total", "Medio", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnHidden(0, True)
        self.table.doubleClicked.connect(self._show_ticket)
        layout.addWidget(self.table)
        
        # Extornar
        btn_ext = QPushButton("🔄 Anular / Extornar")
        btn_ext.setStyleSheet("background: #ef4444; font-weight: bold; padding: 10px;")
        btn_ext.clicked.connect(self._extornar)
        layout.addWidget(btn_ext)

    def _create_card(self, title, color="#22c55e"):
        """Crea tarjeta KPI optimizada"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border-radius: 8px;
                border: 2px solid #334155;
            }
        """)
        frame.setFixedHeight(90)  # ← REDUCIDO de 120 a 90
        
        l = QVBoxLayout(frame)
        l.setSpacing(5)
        l.setContentsMargins(15, 12, 15, 12)
        
        # Título (fuente más grande)
        t = QLabel(title)
        t.setStyleSheet("color: #94a3b8; font-size: 15px; font-weight: 600;")  # ← 15px (era 13px)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)  # ← CENTRADO
        
        # Valor (centrado)
        v = QLabel("...")
        v.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {color};
            padding: 3px 0;
        """)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)  # ← CENTRADO
        
        l.addWidget(t)
        l.addWidget(v)
        l.addStretch()
        
        return frame, v

    def _load_data(self):
        fi = self.date_from.date().toString("yyyy-MM-dd")
        ff = self.date_to.date().toString("yyyy-MM-dd")
        ventas = self.service.get_ventas(fi, ff)
        
        self.table.setRowCount(0)
        tot = 0
        cnt = 0
        
        for r, v in enumerate(ventas):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(v[0])))
            self.table.setItem(r, 1, QTableWidgetItem(v[1].split(' ')[1]))
            self.table.setItem(r, 2, QTableWidgetItem(v[3] or "Visitante"))
            self.table.setItem(r, 3, QTableWidgetItem(f"S/ {v[4]:.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(v[5].upper()))
            
            est = QTableWidgetItem(v[6].upper())
            est.setForeground(QColor("#22c55e" if v[6]=='completada' else "#ef4444"))
            self.table.setItem(r, 5, est)
            
            if v[6] == 'completada':
                tot += v[4]
                cnt += 1
        
        # Actualizar KPIs
        self.lbl_total_val.setText(f"S/ {tot:.2f}")
        self.lbl_count_val.setText(str(cnt))
        
        # Calcular ticket promedio
        if cnt > 0:
            promedio = tot / cnt
            self.lbl_ticket_val.setText(f"S/ {promedio:.2f}")
        else:
            self.lbl_ticket_val.setText("S/ 0.00")

    def _extornar(self):
        row = self.table.currentRow()
        if row < 0: return
        vid = int(self.table.item(row, 0).text())
        if self.table.item(row, 5).text() != "COMPLETADA":
            return QMessageBox.warning(self, "Error", "Ya anulada")
            
        if QMessageBox.question(self, "Confirmar", "¿Anular venta? Retorna stock y dinero.") == QMessageBox.StandardButton.Yes:
            if self.service.extornar_venta(vid).success:
                QMessageBox.information(self, "Ok", "Anulada")
                self._load_data()

    def _show_ticket(self):
        """Muestra ticket con formato mejorado"""
        row = self.table.currentRow()
        if row < 0: return
        vid = int(self.table.item(row, 0).text())
        data = self.service.get_venta_detalle(vid)
        if not data: return
        
        v = data['venta']
        
        # Construir ticket con formato
        ticket = []
        ticket.append("═" * 50)
        ticket.append("          GYMMANAGER PRO - TICKET DE VENTA")
        ticket.append("═" * 50)
        ticket.append("")
        ticket.append(f"  Ticket Nº: #{str(v[0]).zfill(8)}")
        ticket.append(f"  Fecha:     {v[1]}")
        ticket.append(f"  Cliente:   {v[4] or 'Visitante'}")
        ticket.append("")
        ticket.append("─" * 50)
        ticket.append("  DETALLE DE PRODUCTOS")
        ticket.append("─" * 50)
        ticket.append("")
        
        # Productos con formato tabla
        # Estructura del detalle:
        # 0: id, 1: producto_id, 2: nombre, 3: sku, 
        # 4: cantidad, 5: precio_unitario, 6: descuento_porcentaje, 7: subtotal
        total = 0
        for d in data['detalle']:
            nombre = str(d[2])[:30]  # d[2] = nombre del producto
            cant = d[4]              # d[4] = cantidad
            precio = d[5]            # d[5] = precio_unitario
            subtotal = d[7]          # d[7] = subtotal
            total += subtotal
            
            # Formato: "  Producto                      Cant  P.Unit  Subtotal"
            linea = f"  {nombre:<30} {cant:>4} x {precio:>7.2f} = {subtotal:>8.2f}"
            ticket.append(linea)
        
        ticket.append("")
        ticket.append("─" * 50)
        ticket.append(f"  TOTAL:                                    S/ {total:>8.2f}")
        ticket.append("─" * 50)
        ticket.append(f"  Método de Pago: {v[6].upper()}")
        ticket.append("")
        ticket.append("═" * 50)
        ticket.append("          ¡Gracias por su compra!")
        ticket.append("═" * 50)
        
        txt = "\n".join(ticket)
        
        # Diálogo con estilo
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Ticket #{str(v[0]).zfill(8)}")
        dlg.setMinimumSize(600, 500)
        dlg.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(dlg)
        
        # Área de texto con estilo monoespacio
        text_edit = QTextEdit()
        text_edit.setPlainText(txt)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 11))
        text_edit.setStyleSheet("""
            QTextEdit {
                background: #0f172a;
                color: #e2e8f0;
                border: 2px solid #334155;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        layout.addWidget(text_edit)
        
        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.setStyleSheet("padding: 8px 20px; font-weight: bold;")
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)
        
        dlg.exec()