# -*- coding: utf-8 -*-
"""
Modelo para gestión de Planes Combo (Nx1)
Permite asignar múltiples beneficiarios a un solo pago
"""
from typing import List, Tuple, Optional
from core.base_model import BaseModel

class ComboModel(BaseModel):
    """Modelo para operaciones CRUD de beneficiarios en combos"""
    
    def add_member_to_combo(self, payment_id: int, miembro_id: int, es_titular: bool = False) -> int:
        """
        Agrega un miembro como beneficiario de un pago combo.
        
        Args:
            payment_id: ID del pago
            miembro_id: ID del miembro beneficiario
            es_titular: True si es quien pagó
            
        Returns:
            int: ID del registro
            
        Raises:
            sqlite3.IntegrityError: Si el miembro ya está en este combo
        """
        data = {
            'payment_id': payment_id,
            'miembro_id': miembro_id,
            'es_titular': 1 if es_titular else 0
        }
        
        return self.insert('payment_members', data)
    
    def get_combo_members(self, payment_id: int) -> List[Tuple]:
        """
        Obtiene todos los beneficiarios de un pago combo.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            List[Tuple]: (id, payment_id, miembro_id, nombre_completo, codigo, es_titular, fecha_asignacion)
        """
        query = """
            SELECT 
                pm.id,
                pm.payment_id,
                pm.miembro_id,
                m.nombre_completo,
                m.codigo,
                pm.es_titular,
                pm.fecha_asignacion
            FROM payment_members pm
            JOIN members m ON pm.miembro_id = m.id
            WHERE pm.payment_id = ?
            ORDER BY pm.es_titular DESC, m.nombre_completo ASC
        """
        
        return self.execute_query(query, (payment_id,))
    
    def get_member_combo_payments(self, miembro_id: int) -> List[Tuple]:
        """
        Obtiene todos los pagos combo en los que el miembro es beneficiario.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            List[Tuple]: (payment_id, plan_nombre, fecha_pago, fecha_vencimiento, 
                         es_titular, titular_nombre, titular_codigo)
        """
        query = """
            SELECT 
                pm.payment_id,
                pl.nombre AS plan_nombre,
                p.fecha_pago,
                p.fecha_vencimiento,
                pm.es_titular,
                m_titular.nombre_completo AS titular_nombre,
                m_titular.codigo AS titular_codigo
            FROM payment_members pm
            JOIN payments p ON pm.payment_id = p.id
            JOIN plans pl ON p.plan_id = pl.id
            LEFT JOIN payment_members pm_titular ON p.id = pm_titular.payment_id AND pm_titular.es_titular = 1
            LEFT JOIN members m_titular ON pm_titular.miembro_id = m_titular.id
            WHERE pm.miembro_id = ?
            ORDER BY p.fecha_pago DESC
        """
        
        return self.execute_query(query, (miembro_id,))
    
    def is_member_in_combo(self, payment_id: int, miembro_id: int) -> bool:
        """
        Verifica si un miembro ya está en un combo específico.
        
        Args:
            payment_id: ID del pago
            miembro_id: ID del miembro
            
        Returns:
            bool: True si ya está en el combo
        """
        query = """
            SELECT COUNT(*) FROM payment_members
            WHERE payment_id = ? AND miembro_id = ?
        """
        
        result = self.execute_query(query, (payment_id, miembro_id), fetch_one=True)
        return result[0] > 0 if result else False
    
    def count_combo_members(self, payment_id: int) -> int:
        """
        Cuenta cuántos beneficiarios tiene un combo.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            int: Cantidad de beneficiarios (incluye titular)
        """
        query = "SELECT COUNT(*) FROM payment_members WHERE payment_id = ?"
        result = self.execute_query(query, (payment_id,), fetch_one=True)
        return result[0] if result else 0
    
    def remove_member_from_combo(self, payment_id: int, miembro_id: int) -> bool:
        """
        Remueve un beneficiario de un combo.
        ADVERTENCIA: No permite remover al titular.
        
        Args:
            payment_id: ID del pago
            miembro_id: ID del miembro a remover
            
        Returns:
            bool: True si se removió
            
        Raises:
            ValueError: Si se intenta remover al titular
        """
        # Verificar que no sea el titular
        query = """
            SELECT es_titular FROM payment_members
            WHERE payment_id = ? AND miembro_id = ?
        """
        result = self.execute_query(query, (payment_id, miembro_id), fetch_one=True)
        
        if result and result[0] == 1:
            raise ValueError("No se puede remover al titular del combo")
        
        where = {
            'payment_id': payment_id,
            'miembro_id': miembro_id
        }
        
        return self.delete('payment_members', where)
    
    def get_titular(self, payment_id: int) -> Optional[Tuple]:
        """
        Obtiene el titular de un pago combo.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            Tuple: (miembro_id, nombre_completo, codigo) o None
        """
        query = """
            SELECT 
                m.id,
                m.nombre_completo,
                m.codigo
            FROM payment_members pm
            JOIN members m ON pm.miembro_id = m.id
            WHERE pm.payment_id = ? AND pm.es_titular = 1
        """
        
        return self.execute_query(query, (payment_id,), fetch_one=True)
    
    def get_beneficiarios(self, payment_id: int) -> List[Tuple]:
        """
        Obtiene solo los beneficiarios (sin el titular) de un combo.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            List[Tuple]: (miembro_id, nombre_completo, codigo)
        """
        query = """
            SELECT 
                m.id,
                m.nombre_completo,
                m.codigo
            FROM payment_members pm
            JOIN members m ON pm.miembro_id = m.id
            WHERE pm.payment_id = ? AND pm.es_titular = 0
            ORDER BY m.nombre_completo ASC
        """
        
        return self.execute_query(query, (payment_id,))
    
    def has_active_combo_membership(self, miembro_id: int) -> bool:
        """
        Verifica si un miembro tiene una membresía activa mediante combo.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            bool: True si tiene combo activo
        """
        query = """
            SELECT COUNT(*)
            FROM payment_members pm
            JOIN payments p ON pm.payment_id = p.id
            WHERE pm.miembro_id = ?
            AND p.fecha_vencimiento >= DATE('now')
        """
        
        result = self.execute_query(query, (miembro_id,), fetch_one=True)
        return result[0] > 0 if result else False
    
    def get_active_combo_info(self, miembro_id: int) -> Optional[Tuple]:
        """
        Obtiene información del combo activo de un miembro.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            Tuple: (payment_id, plan_nombre, fecha_vencimiento, es_titular, 
                   titular_nombre, titular_codigo) o None
        """
        query = """
            SELECT 
                pm.payment_id,
                pl.nombre AS plan_nombre,
                p.fecha_vencimiento,
                pm.es_titular,
                m_titular.nombre_completo AS titular_nombre,
                m_titular.codigo AS titular_codigo
            FROM payment_members pm
            JOIN payments p ON pm.payment_id = p.id
            JOIN plans pl ON p.plan_id = pl.id
            LEFT JOIN payment_members pm_titular ON p.id = pm_titular.payment_id AND pm_titular.es_titular = 1
            LEFT JOIN members m_titular ON pm_titular.miembro_id = m_titular.id
            WHERE pm.miembro_id = ?
            AND p.fecha_vencimiento >= DATE('now')
            ORDER BY p.fecha_vencimiento DESC
            LIMIT 1
        """
        
        return self.execute_query(query, (miembro_id,), fetch_one=True)
