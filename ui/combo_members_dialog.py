# -*- coding: utf-8 -*-
"""
Diálogo para Agregar Miembros a un Plan Combo - DARK THEME
Permite buscar y agregar co-titulares que compartirán la membresía
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QFrame, QMessageBox,
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from models.member_model import MemberModel
from services.combo_service import ComboService
from core.logger import logger

class ComboMembersDialog(QDialog):
    """Diálogo para agregar miembros a un plan combo - DARK THEME"""
    
    members_selected = pyqtSignal(list)  # Emite lista de miembro_ids
    
    def __init__(self, parent=None, plan_nombre="", plan_max_personas=2, 
                 monto_total=0.0, pagador_id=None, pagador_nombre=""):
        super().__init__(parent)
        
        self.plan_nombre = plan_nombre
        self.plan_max_personas = int(plan_max_personas)  # 🔥 FIX: Asegurar que sea int
        self.monto_total = monto_total
        self.pagador_id = pagador_id
        self.pagador_nombre = pagador_nombre
        
        self.member_model = MemberModel()
        self.combo_service = ComboService()
        
        self.selected_members = []  # Lista de dicts con info de miembros
        
        self.setWindowTitle("👥 Agregar Miembros al Combo")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        
        # 🔥 DARK THEME
        self.setStyleSheet("""
            QDialog {
                background: #0f172a;
                color: #e5e7eb;
            }
            QLabel {
                color: #e5e7eb;
            }
            QLineEdit {
                background: #1e293b;
                color: #f1f5f9;
                border: 2px solid #475569;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:disabled {
                background: #4b5563;
                color: #9ca3af;
            }
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("👥 Agregar Miembros al Combo")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f1f5f9;
            padding-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # Info del plan - 🔥 COMPACTO EN UNA LÍNEA
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(6)
        
        # 🔥 Header compacto en una sola línea con separadores
        header_text = (
            f"📋 <b>{self.plan_nombre}</b> &nbsp;•&nbsp; "
            f"👥 {self.plan_max_personas} personas &nbsp;•&nbsp; "
            f"💰 S/ {self.monto_total:.2f}"
        )
        header_label = QLabel(header_text)
        header_label.setTextFormat(Qt.TextFormat.RichText)
        header_label.setStyleSheet("""
            font-size: 13px; 
            color: #cbd5e1;
            padding: 4px 0;
            background: transparent;
        """)
        info_layout.addWidget(header_label)
        
        layout.addWidget(info_frame)
        
        # Instrucciones
        instrucciones = QLabel(
            f"Agregue {self.plan_max_personas - 1} miembro(s) adicional(es) que compartirán esta membresía.\n"
            "Busque por código o DNI."
        )
        instrucciones.setStyleSheet("color: #94a3b8; font-size: 13px; background: transparent;")
        instrucciones.setWordWrap(True)
        layout.addWidget(instrucciones)
        
        # Scroll area para miembros
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1e293b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #475569;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
        """)
        
        self.members_container = QWidget()
        self.members_container.setStyleSheet("background: transparent;")
        self.members_layout = QVBoxLayout(self.members_container)
        self.members_layout.setSpacing(16)
        self.members_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.members_container)
        layout.addWidget(scroll, 1)
        
        # Agregar pagador
        self._add_pagador_widget()
        
        # Agregar slots para miembros adicionales
        self.member_slots = []
        for i in range(1, self.plan_max_personas):
            self._add_member_slot(i)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #475569;
                color: white;
                padding: 12px 28px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #64748b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        self.confirm_btn = QPushButton("✓ Confirmar Combo")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background: #22c55e;
                color: white;
                padding: 12px 28px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #16a34a;
            }
            QPushButton:disabled {
                background: #4b5563;
                color: #9ca3af;
            }
        """)
        self.confirm_btn.clicked.connect(self._on_confirm)
        self.confirm_btn.setEnabled(False)
        buttons_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(buttons_layout)
    
    def _add_pagador_widget(self):
        """Agrega widget con info del pagador"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #1e3a5f;
                border: 2px solid #3b82f6;
                border-radius: 10px;
                padding: 16px;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        
        icon_label = QLabel("👤")
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        title = QLabel("Miembro 1 (quien registra el pago):")
        title.setStyleSheet("font-size: 12px; color: #93c5fd; font-weight: 600; background: transparent;")
        info_layout.addWidget(title)
        
        nombre = QLabel(f"✓ {self.pagador_nombre}")
        nombre.setStyleSheet("font-size: 14px; color: #f1f5f9; font-weight: 700; background: transparent;")
        info_layout.addWidget(nombre)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.members_layout.addWidget(container)
    
    def _add_member_slot(self, numero):
        """Agrega un slot para buscar miembro"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border: 2px solid #334155;
                border-radius: 10px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        
        # Título
        title_layout = QHBoxLayout()
        icon = QLabel("👤")
        icon.setStyleSheet("font-size: 20px; background: transparent;")
        title_layout.addWidget(icon)
        
        title = QLabel(f"Miembro {numero + 1}:")
        title.setStyleSheet("font-size: 13px; font-weight: 600; color: #cbd5e1; background: transparent;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Búsqueda
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar por código o DNI...")
        search_layout.addWidget(search_input, 1)
        
        search_btn = QPushButton("🔍 Buscar")
        search_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        search_btn.clicked.connect(
            lambda: self._search_member(numero, search_input, result_label)
        )
        search_layout.addWidget(search_btn)
        
        # Enter para buscar
        search_input.returnPressed.connect(search_btn.click)
        
        layout.addLayout(search_layout)
        
        # Resultado
        result_label = QLabel("")
        result_label.setStyleSheet("font-size: 12px; color: #94a3b8; background: transparent;")
        result_label.setWordWrap(True)
        layout.addWidget(result_label)
        
        self.members_layout.addWidget(container)
        
        # Guardar referencias
        self.member_slots.append({
            'numero': numero,
            'container': container,
            'search_input': search_input,
            'result_label': result_label,
            'member_data': None
        })
    
    def _search_member(self, slot_numero, search_input, result_label):
        """Busca un miembro por código o DNI"""
        search_term = search_input.text().strip()
        
        if not search_term:
            result_label.setText("⚠️ Ingrese un código o DNI")
            result_label.setStyleSheet("color: #f59e0b; font-size: 12px; background: transparent;")
            return
        
        # 🔥 FIX: Usar método correcto
        miembro_data = self.member_model.find_member_by_identifier(search_term)
        
        if not miembro_data:
            result_label.setText(f"❌ No se encontró miembro con código/DNI: {search_term}")
            result_label.setStyleSheet("color: #ef4444; font-size: 12px; background: transparent;")
            self._update_slot_member(slot_numero, None)
            return
        
        # Convertir tupla a dict
        miembro = {
            'id': miembro_data[0],
            'nombre': miembro_data[1],
            'dni': miembro_data[2],
            'codigo': miembro_data[6],
            'estado': miembro_data[7]
        }
        
        # Validar que no sea el pagador
        if miembro['id'] == self.pagador_id:
            result_label.setText("❌ No puede agregar al mismo pagador")
            result_label.setStyleSheet("color: #ef4444; font-size: 12px; background: transparent;")
            self._update_slot_member(slot_numero, None)
            return
        
        # Validar que no esté ya agregado
        if any(m['id'] == miembro['id'] for m in self.selected_members):
            result_label.setText("❌ Este miembro ya está agregado al combo")
            result_label.setStyleSheet("color: #ef4444; font-size: 12px; background: transparent;")
            self._update_slot_member(slot_numero, None)
            return
        
        # Éxito
        result_label.setText(f"✓ {miembro['nombre']} (DNI: {miembro['dni']})")
        result_label.setStyleSheet("color: #22c55e; font-size: 13px; font-weight: 600; background: transparent;")
        
        self._update_slot_member(slot_numero, miembro)
    
    def _update_slot_member(self, slot_numero, member_data):
        """Actualiza el miembro seleccionado en un slot"""
        for slot in self.member_slots:
            if slot['numero'] == slot_numero:
                slot['member_data'] = member_data
                break
        
        # Actualizar lista de seleccionados
        self.selected_members = [
            slot['member_data'] for slot in self.member_slots 
            if slot['member_data'] is not None
        ]
        
        # Habilitar botón si se seleccionaron todos
        required = self.plan_max_personas - 1
        self.confirm_btn.setEnabled(len(self.selected_members) == required)
    
    def _on_confirm(self):
        """Confirma la selección de miembros"""
        if len(self.selected_members) != self.plan_max_personas - 1:
            QMessageBox.warning(
                self,
                "Selección incompleta",
                f"Debe seleccionar {self.plan_max_personas - 1} miembro(s) adicional(es)"
            )
            return
        
        # Mostrar resumen
        resumen = f"Se agregarán {len(self.selected_members)} miembro(s) adicional(es) al combo:\n\n"
        
        for member in self.selected_members:
            resumen += f"• {member['nombre']} ({member['codigo']})\n"
        
        resumen += f"\nTodos compartirán la membresía del plan: {self.plan_nombre}"
        
        reply = QMessageBox.question(
            self,
            "Confirmar Combo",
            resumen,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.accept()
    
    def get_selected_members(self):
        """Retorna lista de IDs de miembros seleccionados (sin incluir pagador)"""
        return [m['id'] for m in self.selected_members]