# -*- coding: utf-8 -*-
"""
Validadores reutilizables para datos del sistema
"""
import re
from typing import Tuple

class Validator:
    """Validadores reutilizables para diferentes tipos de datos"""
    
    @staticmethod
    def validate_dni(dni: str) -> Tuple[bool, str]:
        """
        Valida formato de DNI peruano (8 dígitos).
        
        Args:
            dni: DNI a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not dni or not dni.strip():
            return False, "DNI no puede estar vacío"
        
        dni = dni.strip()
        
        if not dni.isdigit():
            return False, "DNI debe contener solo números"
        
        if len(dni) != 8:
            return False, "DNI debe tener exactamente 8 dígitos"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valida formato de email.
        
        Args:
            email: Email a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not email:
            return True, ""  # Email es opcional
        
        email = email.strip()
        
        # Patrón básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Formato de email inválido"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Valida formato de teléfono.
        
        Args:
            phone: Teléfono a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not phone:
            return True, ""  # Teléfono es opcional
        
        phone = phone.strip()
        
        # Permitir números, espacios, guiones, paréntesis, +
        pattern = r'^[\d\s\-\(\)\+]+$'
        
        if not re.match(pattern, phone):
            return False, "Formato de teléfono inválido (usa solo números, espacios, -, (), +)"
        
        # Verificar longitud mínima de dígitos
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 6:
            return False, "Teléfono debe tener al menos 6 dígitos"
        
        if len(digits) > 15:
            return False, "Teléfono no puede tener más de 15 dígitos"
        
        return True, ""
    
    @staticmethod
    def validate_price(price_str: str) -> Tuple[bool, str, float]:
        """
        Valida y convierte precio.
        
        Args:
            price_str: Precio como string
            
        Returns:
            Tuple[bool, str, float]: (es_válido, mensaje_error, precio_float)
        """
        if not price_str or not price_str.strip():
            return False, "El precio no puede estar vacío", 0.0
        
        try:
            price = float(price_str.strip())
        except ValueError:
            return False, "El precio debe ser un número válido", 0.0
        
        if price <= 0:
            return False, "El precio debe ser mayor a cero", 0.0
        
        if price > 999999.99:
            return False, "El precio es demasiado alto", 0.0
        
        return True, "", price
    
    @staticmethod
    def validate_positive_integer(value_str: str, field_name: str = "Valor") -> Tuple[bool, str, int]:
        """
        Valida y convierte entero positivo.
        
        Args:
            value_str: Valor como string
            field_name: Nombre del campo para mensajes de error
            
        Returns:
            Tuple[bool, str, int]: (es_válido, mensaje_error, valor_int)
        """
        if not value_str or not value_str.strip():
            return False, f"{field_name} no puede estar vacío", 0
        
        try:
            value = int(value_str.strip())
        except ValueError:
            return False, f"{field_name} debe ser un número entero", 0
        
        if value <= 0:
            return False, f"{field_name} debe ser mayor a cero", 0
        
        return True, "", value
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Valida nombre de persona.
        
        Args:
            name: Nombre a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not name or not name.strip():
            return False, "El nombre no puede estar vacío"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"
        
        if len(name) > 100:
            return False, "El nombre es demasiado largo (máximo 100 caracteres)"
        
        # Permitir letras, espacios, acentos, ñ
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(pattern, name):
            return False, "El nombre solo puede contener letras y espacios"
        
        return True, ""
