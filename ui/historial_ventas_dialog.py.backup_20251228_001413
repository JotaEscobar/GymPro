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
        
        # KPIs (Guardamos referencias directas a los Labels)
        kpi_layout = QHBoxLayout()
        self.card_total_frame, self.lbl_total_val = self._create_card("Ventas Periodo")
        self.card_count_frame, self.lbl_count_val = self._create_card("Transacciones")
        
        kpi_layout.addWidget(self.card_total_frame)
        kpi_layout.addWidget(self.card_count_frame)
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

    def _create_card(self, title):
        frame = QFrame()
        frame.setStyleSheet("background: #1e293b; border-radius: 8px; padding: 15px;")
        l = QVBoxLayout(frame)
        t = QLabel(title)
        t.setStyleSheet("color: #94a3b8; font-size: 14px;")
        v = QLabel("...")
        v.setStyleSheet("font-size: 24px; font-weight: bold; color: #22c55e;")
        l.addWidget(t)
        l.addWidget(v)
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
                
        self.lbl_total_val.setText(f"S/ {tot:.2f}")
        self.lbl_count_val.setText(str(cnt))

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
        row = self.table.currentRow()
        if row < 0: return
        vid = int(self.table.item(row, 0).text())
        data = self.service.get_venta_detalle(vid)
        if not data: return
        
        v = data['venta']
        txt = f"TICKET #{str(v[0]).zfill(8)}\nFECHA: {v[1]}\nCLIENTE: {v[4]}\n\n"
        for d in data['detalle']:
            txt += f"{d[4]} x {d[2]} = {d[7]:.2f}\n"
        txt += f"\nTOTAL: S/ {v[5]:.2f}\nPAGO: {v[6].upper()}"
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Ticket")
        t = QTextEdit(txt)
        t.setFont(QFont("Courier New", 12))
        l = QVBoxLayout(dlg)
        l.addWidget(t)
        dlg.exec()