# -*- coding: utf-8 -*-
"""
Modelo para gestión de planes/tarifas
"""
import sqlite3
from core.base_model import BaseModel

class PlanModel(BaseModel):
    """Modelo para operaciones CRUD de planes"""

    def insert_plan(self, nombre, precio, dias, personas, inicio, fin, desc, categoria_id=None):
        """
        Crea un nuevo plan/tarifa.
        
        Args:
            nombre: Nombre del plan
            precio: Precio del plan
            dias: Duración en días
            personas: Cantidad de personas (combos)
            inicio: Fecha inicio de venta
            fin: Fecha fin de venta
            desc: Descripción del plan
            categoria_id: ID de categoría (opcional)
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            data = {
                'nombre_plan': nombre,
                'precio': precio,
                'duracion_dias': dias,
                'cantidad_personas': personas,
                'fecha_inicio_venta': inicio,
                'fecha_fin_venta': fin,
                'descripcion': desc,
                'estado': 1,
                'categoria_id': categoria_id  # ← NUEVO
            }
            
            plan_id = self.insert('plans', data)
            
            self.logger.info(f"Plan creado: ID={plan_id}, Nombre={nombre}")
            
            return {
                "success": True,
                "message": "Plan creado correctamente",
                "plan_id": plan_id
            }
            
        except ValueError as e:
            if "UNIQUE constraint failed" in str(e):
                return {
                    "success": False,
                    "message": "Ya existe un plan con ese nombre"
                }
            return {
                "success": False,
                "message": f"Error al crear plan: {e}"
            }

    def get_all_plans(self, include_inactive=False):
        """
        Obtiene todos los planes.
        
        Args:
            include_inactive: Si True, incluye planes inactivos
            
        Returns:
            list: Lista de tuplas con datos de planes
        """
        query = """
            SELECT id, nombre_plan, precio, duracion_dias, cantidad_personas, 
                   fecha_inicio_venta, fecha_fin_venta, descripcion, estado, categoria_id 
            FROM plans
        """
        
        if not include_inactive:
            query += " WHERE estado = 1"
            
        query += " ORDER BY precio ASC"
        
        return self.execute_query(query)

    def get_plan_by_id(self, plan_id):
        """
        Obtiene un plan por su ID.
        
        Args:
            plan_id: ID del plan
            
        Returns:
            tuple: Datos del plan o None
        """
        query = """
            SELECT id, nombre_plan, precio, duracion_dias, cantidad_personas, 
                   fecha_inicio_venta, fecha_fin_venta, descripcion, estado, categoria_id 
            FROM plans
            WHERE id = ?
        """
        return self.execute_query(query, (plan_id,), fetch_one=True)

    def update_plan(self, plan_id, nombre, precio, dias, personas, inicio, fin, desc, estado, categoria_id=None):
        """
        Actualiza un plan existente.
        
        Args:
            plan_id: ID del plan
            nombre: Nuevo nombre
            precio: Nuevo precio
            dias: Nueva duración
            personas: Nueva cantidad de personas
            inicio: Nueva fecha inicio venta
            fin: Nueva fecha fin venta
            desc: Nueva descripción
            estado: Nuevo estado (1=activo, 0=inactivo)
            categoria_id: ID de categoría (opcional)
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            data = {
                'nombre_plan': nombre,
                'precio': precio,
                'duracion_dias': dias,
                'cantidad_personas': personas,
                'fecha_inicio_venta': inicio,
                'fecha_fin_venta': fin,
                'descripcion': desc,
                'estado': estado,
                'categoria_id': categoria_id  # ← NUEVO
            }
            
            updated = self.update('plans', data, {'id': plan_id})
            
            if updated:
                self.logger.info(f"Plan actualizado: ID={plan_id}")
                return {
                    "success": True,
                    "message": "Plan actualizado correctamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontró el plan o no hubo cambios"
                }
                
        except ValueError as e:
            if "UNIQUE constraint failed" in str(e):
                return {
                    "success": False,
                    "message": "Ya existe otro plan con ese nombre"
                }
            return {
                "success": False,
                "message": f"Error al actualizar plan: {e}"
            }

    def delete_plan(self, plan_id):
        """
        Elimina un plan por ID.
        Verifica que no tenga pagos asociados antes de eliminar.
        
        Args:
            plan_id: ID del plan a eliminar
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si hay pagos asociados
            cursor.execute(
                "SELECT COUNT(*) FROM payments WHERE plan_id = ?",
                (plan_id,)
            )
            count = cursor.fetchone()[0]
            
            if count > 0:
                return {
                    "success": False,
                    "message": f"No se puede eliminar: El plan tiene {count} pagos asociados. Cámbielo a inactivo en su lugar."
                }
            
            # Si no hay pagos, eliminar
            deleted = self.delete('plans', {'id': plan_id})
            
            if deleted:
                self.logger.info(f"Plan eliminado: ID={plan_id}")
                return {
                    "success": True,
                    "message": "Plan eliminado correctamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontró el plan"
                }