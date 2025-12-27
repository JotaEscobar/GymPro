# -*- coding: utf-8 -*-
"""
Clase de respuesta estándar para operaciones del sistema
"""
from typing import Any, Optional
from dataclasses import dataclass

@dataclass
class Result:
    """
    Respuesta estándar de operaciones.
    Unifica el formato de retorno de todos los servicios.
    """
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    
    @classmethod
    def ok(cls, message: str = "Operación exitosa", data: Any = None):
        """
        Crea un resultado exitoso.
        
        Args:
            message: Mensaje descriptivo del éxito
            data: Datos adicionales (opcional)
            
        Returns:
            Result: Instancia con success=True
        """
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def fail(cls, message: str, error_code: str = None):
        """
        Crea un resultado de fallo.
        
        Args:
            message: Mensaje descriptivo del error
            error_code: Código de error para categorización (opcional)
            
        Returns:
            Result: Instancia con success=False
        """
        return cls(success=False, message=message, error_code=error_code)
    
    def to_dict(self) -> dict:
        """
        Convierte el resultado a diccionario.
        Útil para serialización JSON (futuro API REST).
        
        Returns:
            dict: Representación en diccionario
        """
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error_code": self.error_code
        }
    
    def __bool__(self):
        """Permite usar Result en contextos booleanos"""
        return self.success

# Ejemplo de uso:
# resultado = Result.ok("Usuario creado", data={"id": 123})
# if resultado:
#     print(resultado.message)
#     print(resultado.data)
