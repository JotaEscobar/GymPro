# -*- coding: utf-8 -*-
"""
Clase base para diálogos con lógica común
Elimina duplicación de código entre PaymentDialog, Member360Dialog, etc.
"""
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt

class BaseDialog(QDialog):
    """
    Clase base para diálogos con funcionalidad común.
    Proporciona helpers para mensajes y configuración de tamaño.
    """
    
    # Configuraciones de tamaño predefinidas
    SIZE_COMPACT = (480, 280)
    SIZE_MEDIUM = (600, 400)
    SIZE_FULL = (800, 600)
    SIZE_LARGE = (1000, 700)
    
    def __init__(self, parent=None, size_mode="auto"):
        """
        Inicializa el diálogo base.
        
        Args:
            parent: Widget padre
            size_mode: "auto", "compact", "medium", "full", "large" o tupla (width, height)
        """
        super().__init__(parent)
        self._setup_size(size_mode)
    
    def _setup_size(self, size_mode):
        """
        Configura el tamaño del diálogo.
        
        Args:
            size_mode: Modo de tamaño o tupla personalizada
        """
        if size_mode == "auto":
            # Auto-detectar según el padre
            if self.parent() and self.parent().__class__.__name__ == "Member360Dialog":
                self.setFixedSize(*self.SIZE_COMPACT)
            else:
                self.setFixedSize(*self.SIZE_FULL)
        elif size_mode == "compact":
            self.setFixedSize(*self.SIZE_COMPACT)
        elif size_mode == "medium":
            self.setFixedSize(*self.SIZE_MEDIUM)
        elif size_mode == "full":
            self.setFixedSize(*self.SIZE_FULL)
        elif size_mode == "large":
            self.setFixedSize(*self.SIZE_LARGE)
        elif isinstance(size_mode, tuple) and len(size_mode) == 2:
            self.setFixedSize(*size_mode)
    
    # ========== HELPERS PARA MENSAJES ==========
    
    def show_success(self, message, title="Éxito"):
        """
        Muestra mensaje de éxito.
        
        Args:
            message: Mensaje a mostrar
            title: Título del diálogo
        """
        QMessageBox.information(self, title, message)
    
    def show_error(self, message, title="Error"):
        """
        Muestra mensaje de error.
        
        Args:
            message: Mensaje a mostrar
            title: Título del diálogo
        """
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, message, title="Advertencia"):
        """
        Muestra mensaje de advertencia.
        
        Args:
            message: Mensaje a mostrar
            title: Título del diálogo
        """
        QMessageBox.warning(self, title, message)
    
    def show_info(self, message, title="Información"):
        """
        Muestra mensaje informativo.
        
        Args:
            message: Mensaje a mostrar
            title: Título del diálogo
        """
        QMessageBox.information(self, title, message)
    
    def confirm_action(self, message, title="Confirmar"):
        """
        Solicita confirmación al usuario.
        
        Args:
            message: Mensaje de confirmación
            title: Título del diálogo
            
        Returns:
            bool: True si el usuario confirmó, False si canceló
        """
        response = QMessageBox.question(
            self, 
            title, 
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Botón por defecto
        )
        return response == QMessageBox.StandardButton.Yes
    
    # ========== HELPERS PARA VALIDACIÓN ==========
    
    def validate_required_fields(self, fields_dict):
        """
        Valida que los campos requeridos no estén vacíos.
        
        Args:
            fields_dict: Diccionario {"nombre_campo": widget}
            
        Returns:
            tuple: (bool, str) - (es_válido, mensaje_error)
        """
        for field_name, widget in fields_dict.items():
            # Obtener texto según el tipo de widget
            if hasattr(widget, 'text'):
                value = widget.text().strip()
            elif hasattr(widget, 'currentText'):
                value = widget.currentText().strip()
            elif hasattr(widget, 'toPlainText'):
                value = widget.toPlainText().strip()
            else:
                continue
            
            if not value:
                return False, f"El campo '{field_name}' no puede estar vacío"
        
        return True, ""
    
    def clear_inputs(self, widgets):
        """
        Limpia una lista de widgets de entrada.
        
        Args:
            widgets: Lista de widgets a limpiar
        """
        for widget in widgets:
            if hasattr(widget, 'clear'):
                widget.clear()
            elif hasattr(widget, 'setCurrentIndex'):
                widget.setCurrentIndex(0)
    
    # ========== HELPERS PARA ESTILOS ==========
    
    def set_input_valid_style(self, widget):
        """Aplica estilo de campo válido"""
        widget.setStyleSheet("border: 2px solid #38a169;")
    
    def set_input_invalid_style(self, widget):
        """Aplica estilo de campo inválido"""
        widget.setStyleSheet("border: 2px solid #f38ba8;")
    
    def set_input_warning_style(self, widget):
        """Aplica estilo de campo con advertencia"""
        widget.setStyleSheet("border: 2px solid #facc15;")
    
    def reset_input_style(self, widget):
        """Resetea estilo de campo"""
        widget.setStyleSheet("")


# ========== EJEMPLO DE USO ==========
"""
# En PaymentDialog.py
from ui.base_dialog import BaseDialog

class PaymentDialog(BaseDialog):
    pago_registrado = pyqtSignal()
    
    def __init__(self, miembro_id, parent=None):
        super().__init__(parent, size_mode="auto")  # Auto-detecta tamaño
        self.miembro_id = miembro_id
        self._setup_ui()
    
    def register_payment(self):
        # Validar campos requeridos
        is_valid, error_msg = self.validate_required_fields({
            "Plan": self.combo_plan,
            "Monto": self.input_monto
        })
        
        if not is_valid:
            self.show_warning(error_msg)
            return
        
        # ... lógica de registro ...
        
        if resultado["success"]:
            self.show_success(resultado["message"])
            self.accept()
        else:
            self.show_error(resultado["message"])
"""
