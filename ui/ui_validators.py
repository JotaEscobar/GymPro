# -*- coding: utf-8 -*-
"""
Validadores para campos de entrada en PyQt6
Proporciona feedback visual inmediato al usuario
"""
from PyQt6.QtGui import QValidator
from PyQt6.QtCore import QRegularExpression
import re

class DNIValidator(QValidator):
    """
    Validador para DNI peruano (8 dígitos).
    Uso: input_dni.setValidator(DNIValidator())
    """
    
    def validate(self, text, pos):
        """
        Valida entrada de DNI.
        
        Returns:
            State.Invalid: No permitir entrada
            State.Intermediate: Permitir pero no es válido aún
            State.Acceptable: Entrada válida completa
        """
        if not text:
            return QValidator.State.Intermediate, text, pos
        
        # Solo permitir dígitos
        if not text.isdigit():
            return QValidator.State.Invalid, text, pos
        
        # Máximo 8 dígitos
        if len(text) > 8:
            return QValidator.State.Invalid, text, pos
        
        # Exactamente 8 = válido
        if len(text) == 8:
            return QValidator.State.Acceptable, text, pos
        
        # Menos de 8 = intermedio (aún escribiendo)
        return QValidator.State.Intermediate, text, pos


class PriceValidator(QValidator):
    """
    Validador para precios (formato: 123.45).
    Permite hasta 2 decimales.
    """
    
    def validate(self, text, pos):
        """Valida entrada de precio"""
        if not text:
            return QValidator.State.Intermediate, text, pos
        
        # Patrón: dígitos + opcional(punto + hasta 2 decimales)
        pattern = r'^\d+(\.\d{0,2})?$'
        
        if re.match(pattern, text):
            return QValidator.State.Acceptable, text, pos
        
        # Si está incompleto pero válido hasta ahora
        if re.match(r'^\d*\.?\d{0,2}$', text):
            return QValidator.State.Intermediate, text, pos
        
        return QValidator.State.Invalid, text, pos


class PhoneValidator(QValidator):
    """
    Validador para teléfonos.
    Permite: números, espacios, guiones, paréntesis, +
    """
    
    def validate(self, text, pos):
        """Valida entrada de teléfono"""
        if not text:
            return QValidator.State.Intermediate, text, pos
        
        # Permitir números, espacios, guiones, paréntesis, +
        pattern = r'^[\d\s\-\(\)\+]+$'
        
        if re.match(pattern, text):
            # Contar solo dígitos
            digits = re.sub(r'\D', '', text)
            
            # Mínimo 6 dígitos para ser válido
            if len(digits) >= 6:
                return QValidator.State.Acceptable, text, pos
            else:
                return QValidator.State.Intermediate, text, pos
        
        return QValidator.State.Invalid, text, pos


class IntegerValidator(QValidator):
    """
    Validador para enteros positivos.
    """
    
    def __init__(self, min_value=1, max_value=999999):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, text, pos):
        """Valida entrada de entero positivo"""
        if not text:
            return QValidator.State.Intermediate, text, pos
        
        if not text.isdigit():
            return QValidator.State.Invalid, text, pos
        
        try:
            value = int(text)
            
            if value > self.max_value:
                return QValidator.State.Invalid, text, pos
            
            if value >= self.min_value:
                return QValidator.State.Acceptable, text, pos
            
            # Menor al mínimo pero aún escribiendo
            return QValidator.State.Intermediate, text, pos
            
        except ValueError:
            return QValidator.State.Invalid, text, pos


class NameValidator(QValidator):
    """
    Validador para nombres de personas.
    Permite: letras, espacios, acentos, ñ
    """
    
    def validate(self, text, pos):
        """Valida entrada de nombre"""
        if not text:
            return QValidator.State.Intermediate, text, pos
        
        # Permitir letras (con acentos), ñ, espacios
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        
        if re.match(pattern, text):
            if len(text) >= 2:
                return QValidator.State.Acceptable, text, pos
            else:
                return QValidator.State.Intermediate, text, pos
        
        return QValidator.State.Invalid, text, pos
