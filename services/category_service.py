# -*- coding: utf-8 -*-
"""
Servicio de Lógica de Negocio para Categorías de Membresía
"""
from models.category_model import CategoryModel
from core.response import Result
from core.logger import logger
from typing import List, Dict, Optional

class CategoryService:
    """Servicio para gestión de categorías de membresía"""
    
    def __init__(self):
        self.model = CategoryModel()
    
    def create_category(self, nombre: str, color_hex: str, orden: int, 
                       descripcion: str = None) -> Result:
        """
        Crea una nueva categoría con validaciones.
        
        Args:
            nombre: Nombre de la categoría (3-50 caracteres)
            color_hex: Color en formato #RRGGBB
            orden: Orden de visualización (positivo)
            descripcion: Descripción opcional
            
        Returns:
            Result con categoria_id en data
        """
        try:
            # Validar nombre
            nombre = nombre.strip()
            if not nombre or len(nombre) < 3:
                return Result.fail("El nombre debe tener al menos 3 caracteres", "VALIDATION_ERROR")
            
            if len(nombre) > 50:
                return Result.fail("El nombre no puede exceder 50 caracteres", "VALIDATION_ERROR")
            
            # Validar que no exista
            existing = self.model.get_category_by_name(nombre)
            if existing:
                return Result.fail(f"Ya existe una categoría con el nombre '{nombre}'", "DUPLICATE_ERROR")
            
            # Validar color
            if not color_hex.startswith('#') or len(color_hex) != 7:
                return Result.fail("Color inválido. Formato esperado: #RRGGBB", "VALIDATION_ERROR")
            
            # Validar orden
            if orden < 0:
                return Result.fail("El orden debe ser un número positivo", "VALIDATION_ERROR")
            
            # Insertar
            categoria_id = self.model.insert_category(nombre, color_hex, orden, descripcion)
            
            logger.info(f"Categoría creada: {nombre} (ID: {categoria_id})")
            
            return Result.ok(
                f"Categoría '{nombre}' creada exitosamente",
                {"categoria_id": categoria_id}
            )
            
        except Exception as e:
            logger.error(f"Error al crear categoría: {e}")
            return Result.fail(f"Error al crear categoría: {str(e)}", "CREATE_ERROR")
    
    def get_all_categories(self, include_inactive: bool = False) -> List[Dict]:
        """
        Obtiene todas las categorías como lista de diccionarios.
        
        Args:
            include_inactive: Incluir categorías inactivas
            
        Returns:
            List[Dict]: Lista de categorías
        """
        try:
            rows = self.model.get_all_categories(include_inactive)
            
            categories = []
            for row in rows:
                categories.append({
                    "id": row[0],
                    "nombre": row[1],
                    "color_hex": row[2],
                    "orden": row[3],
                    "descripcion": row[4],
                    "activo": bool(row[5])
                })
            
            return categories
            
        except Exception as e:
            logger.error(f"Error al obtener categorías: {e}")
            return []
    
    def get_category_by_id(self, categoria_id: int) -> Optional[Dict]:
        """
        Obtiene una categoría por ID.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            Dict con datos de la categoría o None
        """
        try:
            row = self.model.get_category_by_id(categoria_id)
            
            if row:
                return {
                    "id": row[0],
                    "nombre": row[1],
                    "color_hex": row[2],
                    "orden": row[3],
                    "descripcion": row[4],
                    "activo": bool(row[5])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener categoría {categoria_id}: {e}")
            return None
    
    def update_category(self, categoria_id: int, nombre: str, color_hex: str,
                       orden: int, descripcion: str = None, activo: bool = True) -> Result:
        """
        Actualiza una categoría con validaciones.
        
        Args:
            categoria_id: ID de la categoría
            nombre: Nuevo nombre
            color_hex: Nuevo color
            orden: Nuevo orden
            descripcion: Nueva descripción
            activo: Nuevo estado
            
        Returns:
            Result indicando éxito/error
        """
        try:
            # Validar que exista
            existing = self.model.get_category_by_id(categoria_id)
            if not existing:
                return Result.fail("Categoría no encontrada", "NOT_FOUND")
            
            # Validar nombre
            nombre = nombre.strip()
            if not nombre or len(nombre) < 3:
                return Result.fail("El nombre debe tener al menos 3 caracteres", "VALIDATION_ERROR")
            
            # Validar que no exista otro con el mismo nombre
            duplicate = self.model.get_category_by_name(nombre)
            if duplicate and duplicate[0] != categoria_id:
                return Result.fail(f"Ya existe otra categoría con el nombre '{nombre}'", "DUPLICATE_ERROR")
            
            # Validar color
            if not color_hex.startswith('#') or len(color_hex) != 7:
                return Result.fail("Color inválido. Formato esperado: #RRGGBB", "VALIDATION_ERROR")
            
            # Validar orden
            if orden < 0:
                return Result.fail("El orden debe ser un número positivo", "VALIDATION_ERROR")
            
            # Actualizar
            success = self.model.update_category(
                categoria_id, nombre, color_hex, orden, descripcion, activo
            )
            
            if success:
                logger.info(f"Categoría actualizada: {nombre} (ID: {categoria_id})")
                return Result.ok(f"Categoría '{nombre}' actualizada exitosamente")
            else:
                return Result.fail("No se pudo actualizar la categoría", "UPDATE_ERROR")
            
        except Exception as e:
            logger.error(f"Error al actualizar categoría {categoria_id}: {e}")
            return Result.fail(f"Error al actualizar: {str(e)}", "UPDATE_ERROR")
    
    def delete_category(self, categoria_id: int, hard_delete: bool = False) -> Result:
        """
        Elimina una categoría (soft o hard delete).
        
        Args:
            categoria_id: ID de la categoría
            hard_delete: Si True, eliminación permanente
            
        Returns:
            Result indicando éxito/error
        """
        try:
            # Validar que exista
            existing = self.model.get_category_by_id(categoria_id)
            if not existing:
                return Result.fail("Categoría no encontrada", "NOT_FOUND")
            
            nombre = existing[1]
            
            if hard_delete:
                # Verificar que no tenga planes asociados
                count = self.model.count_plans_by_category(categoria_id)
                if count > 0:
                    return Result.fail(
                        f"No se puede eliminar: {count} planes asociados a '{nombre}'",
                        "HAS_DEPENDENCIES"
                    )
                
                self.model.hard_delete_category(categoria_id)
                logger.info(f"Categoría eliminada permanentemente: {nombre} (ID: {categoria_id})")
                return Result.ok(f"Categoría '{nombre}' eliminada permanentemente")
            else:
                # Soft delete
                self.model.delete_category(categoria_id)
                logger.info(f"Categoría desactivada: {nombre} (ID: {categoria_id})")
                return Result.ok(f"Categoría '{nombre}' desactivada")
            
        except Exception as e:
            logger.error(f"Error al eliminar categoría {categoria_id}: {e}")
            return Result.fail(f"Error al eliminar: {str(e)}", "DELETE_ERROR")
    
    def get_category_stats(self, categoria_id: int) -> Dict:
        """
        Obtiene estadísticas de una categoría.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            Dict con estadísticas
        """
        try:
            count_plans = self.model.count_plans_by_category(categoria_id)
            
            return {
                "planes_asociados": count_plans,
                "puede_eliminar": count_plans == 0
            }
            
        except Exception as e:
            logger.error(f"Error al obtener stats de categoría {categoria_id}: {e}")
            return {
                "planes_asociados": 0,
                "puede_eliminar": False
            }
