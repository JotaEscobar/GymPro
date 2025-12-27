# -*- coding: utf-8 -*-
"""
Modelo para gestión de Beneficios y su configuración por categoría
"""
import json
from typing import List, Tuple, Optional, Dict, Any
from core.base_model import BaseModel

class BenefitModel(BaseModel):
    """Modelo para operaciones CRUD de beneficios"""
    
    # ========== TIPOS DE BENEFICIOS ==========
    
    def get_all_benefit_types(self, include_inactive: bool = False) -> List[Tuple]:
        """
        Obtiene todos los tipos de beneficios.
        
        Args:
            include_inactive: Si True, incluye inactivos
            
        Returns:
            List[Tuple]: (id, nombre, codigo, tipo_valor, descripcion, icono, activo)
        """
        query = """
            SELECT id, nombre, codigo, tipo_valor, descripcion, icono, activo
            FROM benefit_types
        """
        
        if not include_inactive:
            query += " WHERE activo = 1"
        
        query += " ORDER BY nombre ASC"
        
        return self.execute_query(query)
    
    def get_benefit_type_by_id(self, benefit_type_id: int) -> Optional[Tuple]:
        """
        Obtiene un tipo de beneficio por ID.
        
        Args:
            benefit_type_id: ID del tipo de beneficio
            
        Returns:
            Tuple o None
        """
        query = """
            SELECT id, nombre, codigo, tipo_valor, descripcion, icono, activo
            FROM benefit_types
            WHERE id = ?
        """
        return self.execute_query(query, (benefit_type_id,), fetch_one=True)
    
    def get_benefit_type_by_code(self, codigo: str) -> Optional[Tuple]:
        """
        Obtiene un tipo de beneficio por código.
        
        Args:
            codigo: Código del beneficio
            
        Returns:
            Tuple o None
        """
        query = """
            SELECT id, nombre, codigo, tipo_valor, descripcion, icono, activo
            FROM benefit_types
            WHERE codigo = ?
        """
        return self.execute_query(query, (codigo,), fetch_one=True)
    
    # ========== BENEFICIOS POR CATEGORÍA ==========
    
    def get_benefits_by_category(self, categoria_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los beneficios configurados para una categoría.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            List[Dict]: Lista de diccionarios con beneficio completo y configuración
            
        Ejemplo:
            [
                {
                    "id": 1,
                    "benefit_type_id": 2,
                    "nombre": "Clases Grupales",
                    "codigo": "classes_access",
                    "tipo_valor": "percentage",
                    "icono": "🧘",
                    "config": {"enabled": True, "descuento_porcentaje": 50}
                },
                ...
            ]
        """
        query = """
            SELECT 
                cb.id,
                cb.benefit_type_id,
                bt.nombre,
                bt.codigo,
                bt.tipo_valor,
                bt.icono,
                bt.descripcion,
                cb.valor_configurado
            FROM category_benefits cb
            JOIN benefit_types bt ON cb.benefit_type_id = bt.id
            WHERE cb.categoria_id = ?
            AND bt.activo = 1
            ORDER BY bt.nombre ASC
        """
        
        rows = self.execute_query(query, (categoria_id,))
        
        beneficios = []
        for row in rows:
            try:
                config = json.loads(row[7]) if row[7] else {}
            except json.JSONDecodeError:
                self.logger.warning(f"Error parseando config de beneficio {row[0]}")
                config = {}
            
            beneficios.append({
                "id": row[0],
                "benefit_type_id": row[1],
                "nombre": row[2],
                "codigo": row[3],
                "tipo_valor": row[4],
                "icono": row[5],
                "descripcion": row[6],
                "config": config
            })
        
        return beneficios
    
    def get_benefit_config(self, categoria_id: int, benefit_code: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración de un beneficio específico para una categoría.
        
        Args:
            categoria_id: ID de la categoría
            benefit_code: Código del beneficio
            
        Returns:
            Dict con la configuración o None si no existe
            
        Ejemplo:
            {"enabled": True, "descuento_porcentaje": 100}
        """
        query = """
            SELECT cb.valor_configurado
            FROM category_benefits cb
            JOIN benefit_types bt ON cb.benefit_type_id = bt.id
            WHERE cb.categoria_id = ? AND bt.codigo = ?
        """
        
        result = self.execute_query(query, (categoria_id, benefit_code), fetch_one=True)
        
        if result and result[0]:
            try:
                return json.loads(result[0])
            except json.JSONDecodeError:
                self.logger.error(f"Error parseando config de {benefit_code}")
                return None
        
        return None
    
    def set_category_benefit(self, categoria_id: int, benefit_type_id: int, 
                            config: Dict[str, Any]) -> int:
        """
        Configura un beneficio para una categoría.
        Si ya existe, actualiza. Si no, inserta.
        
        Args:
            categoria_id: ID de la categoría
            benefit_type_id: ID del tipo de beneficio
            config: Diccionario con configuración
            
        Returns:
            int: ID del registro
            
        Ejemplo:
            config = {"enabled": True, "descuento_porcentaje": 50}
        """
        valor_json = json.dumps(config)
        
        # Verificar si ya existe
        query = """
            SELECT id FROM category_benefits 
            WHERE categoria_id = ? AND benefit_type_id = ?
        """
        existing = self.execute_query(query, (categoria_id, benefit_type_id), fetch_one=True)
        
        if existing:
            # Actualizar
            self.update(
                'category_benefits',
                {'valor_configurado': valor_json},
                {'id': existing[0]}
            )
            return existing[0]
        else:
            # Insertar
            data = {
                'categoria_id': categoria_id,
                'benefit_type_id': benefit_type_id,
                'valor_configurado': valor_json
            }
            return self.insert('category_benefits', data)
    
    def delete_category_benefit(self, categoria_id: int, benefit_type_id: int) -> bool:
        """
        Elimina la configuración de un beneficio para una categoría.
        
        Args:
            categoria_id: ID de la categoría
            benefit_type_id: ID del tipo de beneficio
            
        Returns:
            bool: True si se eliminó
        """
        where = {
            'categoria_id': categoria_id,
            'benefit_type_id': benefit_type_id
        }
        return self.delete('category_benefits', where)
    
    def get_member_benefits(self, miembro_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los beneficios activos de un miembro según su categoría actual.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            List[Dict]: Beneficios del miembro
            
        Nota:
            Requiere que el miembro tenga un pago activo con plan que tenga categoría
        """
        query = """
            SELECT DISTINCT
                bt.codigo,
                bt.nombre,
                bt.tipo_valor,
                bt.icono,
                cb.valor_configurado
            FROM members m
            JOIN payments pay ON m.id = pay.miembro_id
            JOIN plans pl ON pay.plan_id = pl.id
            JOIN membership_categories mc ON pl.categoria_id = mc.id
            JOIN category_benefits cb ON mc.id = cb.categoria_id
            JOIN benefit_types bt ON cb.benefit_type_id = bt.id
            WHERE m.id = ?
            AND pay.fecha_vencimiento >= DATE('now')
            AND mc.activo = 1
            AND bt.activo = 1
            ORDER BY bt.nombre
        """
        
        rows = self.execute_query(query, (miembro_id,))
        
        beneficios = []
        for row in rows:
            try:
                config = json.loads(row[4]) if row[4] else {}
                
                # Solo incluir si está habilitado
                if config.get("enabled", False):
                    beneficios.append({
                        "codigo": row[0],
                        "nombre": row[1],
                        "tipo_valor": row[2],
                        "icono": row[3],
                        "config": config
                    })
            except json.JSONDecodeError:
                self.logger.warning(f"Error parseando config de beneficio {row[0]}")
        
        return beneficios

    def get_benefit_type_by_code(self, codigo):
        """
        Obtiene un tipo de beneficio por su código.
        
        Args:
            codigo: Código del beneficio
            
        Returns:
            dict o None
        """
        query = """
            SELECT codigo, nombre, icono, tipo_valor, descripcion
            FROM benefit_types
            WHERE codigo = ?
        """
        
        result = self.execute_query(query, (codigo,), fetch_one=True)
        
        if result:
            return {
                'codigo': result[0],
                'nombre': result[1],
                'icono': result[2],
                'tipo_valor': result[3],
                'descripcion': result[4]
            }
        return None