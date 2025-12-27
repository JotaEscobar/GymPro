# -*- coding: utf-8 -*-
"""
Diálogo de Configuración de Beneficios por Categoría
Permite habilitar/deshabilitar y configurar valores de beneficios
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QCheckBox, QSpinBox, QSlider,
                             QFrame, QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from services.benefit_service import BenefitService
from core.logger import logger

class BenefitsConfigDialog(QDialog):
    """Diálogo para configurar beneficios de una categoría"""
    
    def __init__(self, parent=None, categoria_id=None, categoria_nombre=""):
        super().__init__(parent)
        self.categoria_id = categoria_id
        self.categoria_nombre = categoria_nombre
        self.benefit_service = BenefitService()
        self.benefit_widgets = {}  # {benefit_code: {widgets}}
        
        self.setWindowTitle(f"Configurar Beneficios - {categoria_nombre}")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        self.setStyleSheet("""
            QDialog {
                background: #0f172a;
                color: #e5e7eb;
            }
            QCheckBox {
                color: #e5e7eb;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #475569;
                border-radius: 4px;
                background: #1e293b;
            }
            QCheckBox::indicator:checked {
                background: #3b82f6;
                border-color: #3b82f6;
            }
            QCheckBox::indicator:hover {
                border-color: #60a5fa;
            }
        """)
        
        self._setup_ui()
        self._load_benefits()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)  # 🔥 REDUCIDO de 20 a 12
        
        # Header
        header = QLabel(f"⚙️ Configuración de Beneficios\n{self.categoria_nombre}")
        header.setStyleSheet("""
            font-size: 16px;
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
        info = QLabel("Active y configure los beneficios que tendrán los miembros de esta categoría")
        info.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 0 10px; background: transparent;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Scroll area para beneficios
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.benefits_container = QWidget()
        self.benefits_layout = QVBoxLayout(self.benefits_container)
        self.benefits_layout.setSpacing(8)  # 🔥 REDUCIDO de 12 a 8
        self.benefits_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.benefits_container)
        layout.addWidget(scroll, 1)
        
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
        
        save_btn = QPushButton("💾 Guardar Configuración")
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
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_benefits(self):
        """Carga los tipos de beneficios y su configuración actual"""
        # Obtener todos los tipos de beneficios
        benefit_types = self.benefit_service.get_all_benefit_types()
        
        # Obtener configuración actual de la categoría
        current_config = self.benefit_service.get_category_benefits(self.categoria_id)
        config_dict = {b['codigo']: b['config'] for b in current_config}
        
        # Crear widget para cada tipo
        for benefit in benefit_types:
            config = config_dict.get(benefit['codigo'], {'enabled': False})
            self._add_benefit_config_widget(benefit, config)
    
    def _add_benefit_config_widget(self, benefit_type, current_config):
        """
        Crea widget de configuración para un tipo de beneficio
        
        Args:
            benefit_type: Dict con info del tipo de beneficio
            current_config: Dict con configuración actual
        """
        # Container del beneficio
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                border: 1px solid #475569;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(8)  # 🔥 REDUCIDO de 12 a 8
        
        # Header del beneficio
        header_layout = QHBoxLayout()
        
        # Checkbox para habilitar/deshabilitar
        enabled_check = QCheckBox()
        enabled_check.setChecked(current_config.get('enabled', False))
        enabled_check.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        header_layout.addWidget(enabled_check)
        
        # Icono y nombre
        icon_label = QLabel(benefit_type.get('icono', '•'))
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        name_label = QLabel(benefit_type['nombre'])
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #f1f5f9; background: transparent;")
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        container_layout.addLayout(header_layout)
        
        # Descripción
        if benefit_type.get('descripcion'):
            desc_label = QLabel(benefit_type['descripcion'])
            desc_label.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
            desc_label.setWordWrap(True)
            container_layout.addWidget(desc_label)
        
        # Widget de valor según tipo
        value_widget = None
        tipo_valor = benefit_type['tipo_valor']
        
        if tipo_valor == 'numeric':
            value_widget = self._create_numeric_widget(current_config)
        elif tipo_valor == 'percentage':
            value_widget = self._create_percentage_widget(current_config)
        
        if value_widget:
            container_layout.addWidget(value_widget)
            value_widget.setEnabled(enabled_check.isChecked())
            enabled_check.toggled.connect(value_widget.setEnabled)
        
        self.benefits_layout.addWidget(container)
        
        # Guardar referencias
        self.benefit_widgets[benefit_type['codigo']] = {
            'enabled': enabled_check,
            'value_widget': value_widget,
            'tipo': tipo_valor
        }
    
    def _create_numeric_widget(self, config):
        """Crea widget para valor numérico (cantidad)"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(30, 8, 0, 0)
        layout.setSpacing(12)
        
        label = QLabel("Cantidad:")
        label.setStyleSheet("color: #475569; font-size: 12px;")
        layout.addWidget(label)
        
        spinbox = QSpinBox()
        spinbox.setMinimum(0)
        spinbox.setMaximum(100)
        spinbox.setValue(config.get('cantidad', 0))
        spinbox.setStyleSheet("""
            QSpinBox {
                padding: 6px;
                border: 1px solid #475569;
                border-radius: 4px;
                min-width: 80px;
                background: #0f172a;
                color: #e5e7eb;
            }
        """)
        layout.addWidget(spinbox)
        
        layout.addStretch()
        
        # Guardar referencia al spinbox
        widget.value_spinbox = spinbox
        
        return widget
    
    def _create_percentage_widget(self, config):
        """Crea widget para valor de porcentaje (descuento)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 8, 0, 0)
        layout.setSpacing(8)
        
        # Label con porcentaje actual
        label = QLabel(f"Descuento: {config.get('descuento_porcentaje', 0)}%")
        label.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: 500; background: transparent;")
        layout.addWidget(label)
        
        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(config.get('descuento_porcentaje', 0))
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(25)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #e2e8f0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3b82f6;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 4px;
            }
        """)
        
        # Actualizar label al mover slider
        slider.valueChanged.connect(
            lambda v: label.setText(f"Descuento: {v}%")
        )
        
        layout.addWidget(slider)
        
        # Shortcuts
        shortcuts_layout = QHBoxLayout()
        shortcuts_layout.setSpacing(8)
        
        for percent in [0, 25, 50, 75, 100]:
            btn = QPushButton(f"{percent}%")
            btn.setStyleSheet("""
                QPushButton {
                    padding: 4px 12px;
                    background: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                }
            """)
            btn.clicked.connect(lambda checked, p=percent: slider.setValue(p))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            shortcuts_layout.addWidget(btn)
        
        shortcuts_layout.addStretch()
        layout.addLayout(shortcuts_layout)
        
        # Guardar referencia al slider
        widget.value_slider = slider
        
        return widget
    
    def _on_save(self):
        """Guarda la configuración de beneficios"""
        try:
            errors = []
            
            for benefit_code, widgets in self.benefit_widgets.items():
                enabled = widgets['enabled'].isChecked()
                
                config = {'enabled': enabled}
                
                if enabled:
                    tipo = widgets['tipo']
                    value_widget = widgets['value_widget']
                    
                    if tipo == 'numeric' and value_widget:
                        config['cantidad'] = value_widget.value_spinbox.value()
                    
                    elif tipo == 'percentage' and value_widget:
                        config['descuento_porcentaje'] = value_widget.value_slider.value()
                
                # Guardar configuración
                result = self.benefit_service.configure_benefit(
                    self.categoria_id,
                    benefit_code,
                    config
                )
                
                if not result.success:
                    errors.append(f"{benefit_code}: {result.message}")
            
            if errors:
                QMessageBox.warning(
                    self,
                    "Errores al guardar",
                    "Algunos beneficios no se guardaron:\n" + "\n".join(errors)
                )
            else:
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Configuración de beneficios guardada para {self.categoria_nombre}"
                )
                self.accept()
        
        except Exception as e:
            logger.error(f"Error al guardar beneficios: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar configuración: {str(e)}"
            )
