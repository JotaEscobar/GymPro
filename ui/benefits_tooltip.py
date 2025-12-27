# -*- coding: utf-8 -*-
"""
Tooltip flotante para mostrar beneficios completos
Componente reutilizable y optimizado
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from services.benefit_service import BenefitService

class BenefitsTooltip(QDialog):
    """Tooltip flotante que muestra TODOS los beneficios de un miembro"""
    
    def __init__(self, parent=None, miembro_id=None):
        """
        Args:
            parent: Widget padre
            miembro_id: ID del miembro
        """
        super().__init__(parent)
        self.miembro_id = miembro_id
        self.benefit_service = BenefitService()
        
        self._setup_ui()
        self._load_benefits()
    
    def _setup_ui(self):
        """Configura la interfaz del tooltip"""
        # Configuración de ventana
        self.setWindowFlags(
            Qt.WindowType.Popup | 
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container con sombra
        container = QFrame()
        container.setObjectName("tooltipContainer")
        container.setStyleSheet("""
            QFrame#tooltipContainer {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)  # 🔥 Más compacto
        container_layout.setSpacing(6)  # 🔥 Menos espacio
        
        # Header
        header = QLabel("🎁 Beneficios Activos")
        header.setStyleSheet("""
            color: #f1f5f9;
            font-size: 12px;  /* 🔥 Más pequeño */
            font-weight: bold;
            padding-bottom: 3px;
            border-bottom: 1px solid #334155;
        """)
        container_layout.addWidget(header)
        
        # Lista de beneficios
        self.benefits_container = QVBoxLayout()
        self.benefits_container.setSpacing(5)  # 🔥 Menos espacio
        container_layout.addLayout(self.benefits_container)
        
        main_layout.addWidget(container)
        
        # 🔥 Ancho más compacto
        self.setFixedWidth(300)
    
    def _load_benefits(self):
        """Carga y muestra TODOS los beneficios del miembro"""
        if not self.miembro_id:
            self._show_empty_state()
            return
        
        benefits = self.benefit_service.get_member_benefits(self.miembro_id)
        
        if not benefits:
            self._show_empty_state()
            return
        
        # Separar por habilitados y no habilitados
        enabled_benefits = [b for b in benefits if b.get('config', {}).get('enabled', False)]
        disabled_benefits = [b for b in benefits if not b.get('config', {}).get('enabled', False)]
        
        # Mostrar habilitados
        if enabled_benefits:
            enabled_label = QLabel("✅ Activos")
            enabled_label.setStyleSheet("""
                color: #22c55e;
                font-size: 10px;  /* 🔥 Más pequeño */
                font-weight: 600;
                padding-top: 3px;
            """)
            self.benefits_container.addWidget(enabled_label)
            
            for benefit in enabled_benefits:
                self._add_benefit_item(benefit, enabled=True)
        
        # Mostrar no habilitados
        if disabled_benefits:
            if enabled_benefits:  # Separador si hay ambos tipos
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("background: #334155; margin: 4px 0;")  # 🔥 Menos margen
                self.benefits_container.addWidget(separator)
            
            disabled_label = QLabel("○ Disponibles")
            disabled_label.setStyleSheet("""
                color: #94a3b8;
                font-size: 10px;  /* 🔥 Más pequeño */
                font-weight: 600;
                padding-top: 3px;
            """)
            self.benefits_container.addWidget(disabled_label)
            
            for benefit in disabled_benefits:
                self._add_benefit_item(benefit, enabled=False)
    
    def _add_benefit_item(self, benefit, enabled=True):
        """
        Agrega un item de beneficio al tooltip (ultra compacto)
        
        Args:
            benefit: Dict con info del beneficio
            enabled: Si el beneficio está habilitado
        """
        # Container del item
        item_layout = QHBoxLayout()
        item_layout.setSpacing(5)  # 🔥 Menos espacio
        
        # Icono
        icon_label = QLabel(benefit.get('icono', '•'))
        icon_label.setStyleSheet(f"""
            font-size: 14px;  /* 🔥 Más pequeño */
            color: {'#22c55e' if enabled else '#64748b'};
        """)
        icon_label.setFixedWidth(18)  # 🔥 Más pequeño
        item_layout.addWidget(icon_label)
        
        # Nombre y valor
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)  # 🔥 Sin espacio
        
        name_label = QLabel(benefit.get('nombre', 'Beneficio'))
        name_label.setStyleSheet(f"""
            color: {'#f1f5f9' if enabled else '#94a3b8'};
            font-size: 11px;  /* 🔥 Compacto */
            font-weight: 500;
        """)
        text_layout.addWidget(name_label)
        
        # Valor del beneficio
        if enabled:
            value_text = self._format_benefit_value(benefit)
            if value_text:
                value_label = QLabel(value_text)
                value_label.setStyleSheet("""
                    color: #fbbf24;
                    font-size: 9px;  /* 🔥 Muy pequeño */
                    font-weight: 500;
                """)
                text_layout.addWidget(value_label)
        
        item_layout.addLayout(text_layout, 1)
        
        # Estado (check o círculo)
        status_label = QLabel("✓" if enabled else "○")
        status_label.setFixedWidth(14)  # 🔥 Más pequeño
        status_label.setStyleSheet(f"""
            font-size: 12px;  /* 🔥 Más pequeño */
            color: {'#22c55e' if enabled else '#64748b'};
        """)
        item_layout.addWidget(status_label)
        
        self.benefits_container.addLayout(item_layout)
    
    def _format_benefit_value(self, benefit):
        """
        Formatea el valor del beneficio para mostrar
        
        Args:
            benefit: Dict con info del beneficio
            
        Returns:
            str: Texto formateado
        """
        config = benefit.get('config', {})
        tipo = benefit.get('tipo_valor', '')
        
        if tipo == 'percentage':
            porcentaje = config.get('descuento_porcentaje', 0)
            if porcentaje == 100:
                return "Gratis"
            elif porcentaje > 0:
                return f"{porcentaje}% descuento"
        
        elif tipo == 'numeric':
            cantidad = config.get('cantidad', 0)
            if cantidad > 0:
                return f"Hasta {cantidad}"
        
        return ""
    
    def _show_empty_state(self):
        """Muestra estado vacío cuando no hay beneficios"""
        label = QLabel("Sin beneficios configurados")
        label.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            padding: 8px;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.benefits_container.addWidget(label)
    
    def show_near_widget(self, widget):
        """
        Muestra el tooltip cerca de un widget
        
        Args:
            widget: Widget de referencia
        """
        # Calcular posición
        global_pos = widget.mapToGlobal(widget.rect().bottomLeft())
        
        # Ajustar para que aparezca debajo y un poco a la izquierda
        x = global_pos.x() - 20
        y = global_pos.y() + 5
        
        self.move(x, y)
        self.show()