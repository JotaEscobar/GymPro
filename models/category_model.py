# -*- coding: utf-8 -*-
"""
Modelo para gestión de Categorías de Membresía
"""
from core.base_model import BaseModel
from typing import Optional, List, Tuple

class CategoryModel(BaseModel):
    """Modelo para operaciones CRUD de categorías de membresía"""
    
    def insert_category(self, nombre: str, color_hex: str, orden: int, descripcion: str = None) -> int:
        """
        Inserta una nueva categoría.
        
        Args:
            nombre: Nombre de la categoría
            color_hex: Color en formato hex (#RRGGBB)
            orden: Orden de visualización
            descripcion: Descripción opcional
            
        Returns:
            int: ID de la categoría insertada
            
        Raises:
            ValueError: Si el nombre ya existe
        """
        data = {
            'nombre': nombre,
            'color_hex': color_hex,
            'orden': orden,
            'descripcion': descripcion,
            'activo': 1
        }
        
        return self.insert('membership_categories', data)
    
    def get_all_categories(self, include_inactive: bool = False) -> List[Tuple]:
        """
        Obtiene todas las categorías ordenadas por 'orden'.
        
        Args:
            include_inactive: Si True, incluye categorías inactivas
            
        Returns:
            List[Tuple]: (id, nombre, color_hex, orden, descripcion, activo)
        """
        query = """
            SELECT id, nombre, color_hex, orden, descripcion, activo
            FROM membership_categories
        """
        
        if not include_inactive:
            query += " WHERE activo = 1"
        
        query += " ORDER BY orden ASC, nombre ASC"
        
        return self.execute_query(query)
    
    def get_category_by_id(self, categoria_id: int) -> Optional[Tuple]:
        """
        Obtiene una categoría por ID.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            Tuple: (id, nombre, color_hex, orden, descripcion, activo) o None
        """
        query = """
            SELECT id, nombre, color_hex, orden, descripcion, activo
            FROM membership_categories
            WHERE id = ?
        """
        return self.execute_query(query, (categoria_id,), fetch_one=True)
    
    def get_category_by_name(self, nombre: str) -> Optional[Tuple]:
        """
        Obtiene una categoría por nombre.
        
        Args:
            nombre: Nombre de la categoría
            
        Returns:
            Tuple: (id, nombre, color_hex, orden, descripcion, activo) o None
        """
        query = """
            SELECT id, nombre, color_hex, orden, descripcion, activo
            FROM membership_categories
            WHERE nombre = ?
        """
        return self.execute_query(query, (nombre,), fetch_one=True)
    
    def update_category(self, categoria_id: int, nombre: str, color_hex: str, 
                       orden: int, descripcion: str = None, activo: bool = True) -> bool:
        """
        Actualiza una categoría.
        
        Args:
            categoria_id: ID de la categoría
            nombre: Nuevo nombre
            color_hex: Nuevo color
            orden: Nuevo orden
            descripcion: Nueva descripción
            activo: Nuevo estado
            
        Returns:
            bool: True si se actualizó
        """
        data = {
            'nombre': nombre,
            'color_hex': color_hex,
            'orden': orden,
            'descripcion': descripcion,
            'activo': 1 if activo else 0
        }
        
        return self.update('membership_categories', data, {'id': categoria_id})
    
    def delete_category(self, categoria_id: int) -> bool:
        """
        Elimina una categoría (soft delete - marcar como inactiva).
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            bool: True si se marcó como inactiva
        """
        return self.update('membership_categories', {'activo': 0}, {'id': categoria_id})
    
    def hard_delete_category(self, categoria_id: int) -> bool:
        """
        Elimina permanentemente una categoría.
        ADVERTENCIA: Solo si no tiene planes asociados.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            bool: True si se eliminó
            
        Raises:
            ValueError: Si tiene planes asociados
        """
        # Verificar si hay planes asociados
        query = "SELECT COUNT(*) FROM plans WHERE categoria_id = ?"
        result = self.execute_query(query, (categoria_id,), fetch_one=True)
        
        if result and result[0] > 0:
            raise ValueError(f"No se puede eliminar: {result[0]} planes asociados a esta categoría")
        
        return self.delete('membership_categories', {'id': categoria_id})
    
    def count_plans_by_category(self, categoria_id: int) -> int:
        """
        Cuenta cuántos planes están asociados a una categoría.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            int: Cantidad de planes
        """
        query = "SELECT COUNT(*) FROM plans WHERE categoria_id = ?"
        result = self.execute_query(query, (categoria_id,), fetch_one=True)
        return result[0] if result else 0
