# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para planes
"""
from models.plan_model import PlanModel
from core.logger import logger

class PlanService:
    """Servicio para gestión de planes/tarifas"""
    
    def __init__(self):
        self.model = PlanModel()

    def _validate_plan_data(self, nombre, precio, dias, personas):
        """
        Valida los datos de un plan.
        
        Args:
            nombre: Nombre del plan
            precio: Precio del plan
            dias: Duración en días
            personas: Cantidad de personas
            
        Raises:
            ValueError: Si algún dato es inválido
        """
        try:
            precio_num = float(precio)
            dias_num = int(dias)
            personas_num = int(personas)
        except ValueError:
            raise ValueError("Precio, Días y Personas deben ser números válidos")
            
        if precio_num <= 0 or dias_num <= 0 or personas_num <= 0:
            raise ValueError("Precio, Días y Personas deben ser mayores a cero")
            
        if not nombre.strip():
            raise ValueError("El nombre del plan no puede estar vacío")
        
        return precio_num, dias_num, personas_num

    def create_plan(self, nombre, precio, dias, personas, inicio_venta, fin_venta, descripcion, categoria_id=None):
        """
        Crea un nuevo plan con validación de datos.
        
        Args:
            nombre: Nombre del plan
            precio: Precio del plan
            dias: Duración en días
            personas: Cantidad de personas
            inicio_venta: Fecha inicio de venta
            fin_venta: Fecha fin de venta
            descripcion: Descripción del plan
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            precio_num, dias_num, personas_num = self._validate_plan_data(
                nombre, precio, dias, personas
            )
            
            resultado = self.model.insert_plan(
                nombre.strip(), 
                precio_num, 
                dias_num, 
                personas_num, 
                inicio_venta, 
                fin_venta, 
                descripcion,
                categoria_id  # ← NUEVO parámetro
            )
            
            if resultado.get("success"):
                logger.info(f"Plan creado: {nombre}")
            
            return resultado
            
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }

    def get_all_plans(self, include_inactive=False):
        """
        Retorna la lista de planes.
        
        Args:
            include_inactive: Si True, incluye planes inactivos
            
        Returns:
            list: Lista de tuplas con datos de planes
        """
        return self.model.get_all_plans(include_inactive)

    def update_plan(self, plan_id, nombre, precio, dias, personas, inicio_venta, fin_venta, descripcion, estado, categoria_id=None):
        """
        Actualiza un plan con validación.
        
        Args:
            plan_id: ID del plan
            nombre: Nuevo nombre
            precio: Nuevo precio
            dias: Nueva duración
            personas: Nueva cantidad personas
            inicio_venta: Nueva fecha inicio
            fin_venta: Nueva fecha fin
            descripcion: Nueva descripción
            estado: Nuevo estado
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            plan_id = int(plan_id)
            estado = int(estado)
            
            precio_num, dias_num, personas_num = self._validate_plan_data(
                nombre, precio, dias, personas
            )
            
            resultado = self.model.update_plan(
                plan_id, 
                nombre.strip(), 
                precio_num, 
                dias_num, 
                personas_num, 
                inicio_venta, 
                fin_venta, 
                descripcion, 
                estado,
                categoria_id  # ← NUEVO parámetro
            )
            
            if resultado.get("success"):
                logger.info(f"Plan actualizado: ID={plan_id}")
            
            return resultado
            
        except ValueError as e:
            return {
                "success": False,
                "message": f"Error de validación: {e}"
            }

    def delete_plan(self, plan_id):
        """
        Elimina un plan, con chequeo de pagos asociados.
        
        Args:
            plan_id: ID del plan
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            plan_id = int(plan_id)
        except ValueError:
            return {
                "success": False,
                "message": "ID de plan no válido"
            }

        resultado = self.model.delete_plan(plan_id)
        
        if resultado.get("success"):
            logger.info(f"Plan eliminado: ID={plan_id}")
        
        return resultado
