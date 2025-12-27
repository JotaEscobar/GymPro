# -*- coding: utf-8 -*-
"""
Servicio de Lógica de Negocio para Beneficios
"""
from models.benefit_model import BenefitModel
from core.response import Result
from core.logger import logger
from typing import List, Dict, Any, Optional

class BenefitService:
    """Servicio para gestión de beneficios y su configuración"""
    
    def __init__(self):
        self.model = BenefitModel()
        self.logger = logger
        
    def get_all_benefit_types(self) -> List[Dict]:
        """
        Obtiene todos los tipos de beneficios disponibles.
        
        Returns:
            List[Dict]: Lista de tipos de beneficios
        """
        try:
            rows = self.model.get_all_benefit_types()
            
            benefits = []
            for row in rows:
                benefits.append({
                    "id": row[0],
                    "nombre": row[1],
                    "codigo": row[2],
                    "tipo_valor": row[3],
                    "descripcion": row[4],
                    "icono": row[5],
                    "activo": bool(row[6])
                })
            
            return benefits
            
        except Exception as e:
            logger.error(f"Error al obtener tipos de beneficios: {e}")
            return []
    
    def get_category_benefits(self, categoria_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los beneficios configurados para una categoría.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            List[Dict]: Beneficios con su configuración
        """
        try:
            return self.model.get_benefits_by_category(categoria_id)
        except Exception as e:
            logger.error(f"Error al obtener beneficios de categoría {categoria_id}: {e}")
            return []
    
    def configure_benefit(self, categoria_id: int, benefit_code: str, 
                         config: Dict[str, Any]) -> Result:
        """
        Configura un beneficio para una categoría.
        
        Args:
            categoria_id: ID de la categoría
            benefit_code: Código del beneficio (ej: "classes_access")
            config: Configuración del beneficio
            
        Returns:
            Result indicando éxito/error
            
        Ejemplo:
            config = {
                "enabled": True,
                "descuento_porcentaje": 50
            }
        """
        try:
            # Validar que el beneficio exista
            benefit_type = self.model.get_benefit_type_by_code(benefit_code)
            if not benefit_type:
                return Result.fail(f"Tipo de beneficio '{benefit_code}' no encontrado", "NOT_FOUND")
            
            benefit_type_id = benefit_type[0]
            tipo_valor = benefit_type[3]
            
            # Validar configuración según tipo
            validation_result = self._validate_config(tipo_valor, config)
            if not validation_result["success"]:
                return Result.fail(validation_result["message"], "VALIDATION_ERROR")
            
            # Guardar configuración
            self.model.set_category_benefit(categoria_id, benefit_type_id, config)
            
            logger.info(f"Beneficio '{benefit_code}' configurado para categoría {categoria_id}")
            
            return Result.ok("Beneficio configurado exitosamente", {"benefit_code": benefit_code})
            
        except Exception as e:
            logger.error(f"Error al configurar beneficio: {e}")
            return Result.fail(f"Error al configurar beneficio: {str(e)}", "CONFIG_ERROR")
    
    def _validate_config(self, tipo_valor: str, config: Dict[str, Any]) -> Dict:
        """
        Valida la configuración según el tipo de beneficio.
        
        Args:
            tipo_valor: "boolean", "numeric" o "percentage"
            config: Configuración a validar
            
        Returns:
            Dict con success y message
        """
        # enabled debe estar presente
        if "enabled" not in config:
            return {"success": False, "message": "Falta el campo 'enabled'"}
        
        if not isinstance(config["enabled"], bool):
            return {"success": False, "message": "'enabled' debe ser boolean"}
        
        # Si está deshabilitado, no validar más
        if not config["enabled"]:
            return {"success": True, "message": "OK"}
        
        # Validaciones específicas por tipo
        if tipo_valor == "numeric":
            if "cantidad" not in config:
                return {"success": False, "message": "Falta el campo 'cantidad' para tipo numérico"}
            
            try:
                cantidad = int(config["cantidad"])
                if cantidad < 0:
                    return {"success": False, "message": "La cantidad debe ser positiva"}
            except (ValueError, TypeError):
                return {"success": False, "message": "La cantidad debe ser un número entero"}
        
        elif tipo_valor == "percentage":
            if "descuento_porcentaje" not in config:
                return {"success": False, "message": "Falta el campo 'descuento_porcentaje'"}
            
            try:
                porcentaje = int(config["descuento_porcentaje"])
                if porcentaje < 0 or porcentaje > 100:
                    return {"success": False, "message": "El porcentaje debe estar entre 0 y 100"}
            except (ValueError, TypeError):
                return {"success": False, "message": "El descuento debe ser un número entero"}
        
        return {"success": True, "message": "OK"}
    
    def delete_benefit_config(self, categoria_id: int, benefit_code: str) -> Result:
        """
        Elimina la configuración de un beneficio para una categoría.
        
        Args:
            categoria_id: ID de la categoría
            benefit_code: Código del beneficio
            
        Returns:
            Result indicando éxito/error
        """
        try:
            # Obtener benefit_type_id
            benefit_type = self.model.get_benefit_type_by_code(benefit_code)
            if not benefit_type:
                return Result.fail("Beneficio no encontrado", "NOT_FOUND")
            
            benefit_type_id = benefit_type[0]
            
            success = self.model.delete_category_benefit(categoria_id, benefit_type_id)
            
            if success:
                logger.info(f"Configuración de '{benefit_code}' eliminada para categoría {categoria_id}")
                return Result.ok("Configuración eliminada")
            else:
                return Result.fail("No se pudo eliminar la configuración", "DELETE_ERROR")
            
        except Exception as e:
            logger.error(f"Error al eliminar configuración: {e}")
            return Result.fail(f"Error: {str(e)}", "DELETE_ERROR")
    
    def get_member_benefits(self, miembro_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene los beneficios activos de un miembro.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            List[Dict]: Beneficios activos del miembro
        """
        try:
            return self.model.get_member_benefits(miembro_id)
        except Exception as e:
            logger.error(f"Error al obtener beneficios del miembro {miembro_id}: {e}")
            return []
    
    def check_member_has_benefit(self, miembro_id: int, benefit_code: str) -> Dict[str, Any]:
        """
        Verifica si un miembro tiene un beneficio específico.
        
        Args:
            miembro_id: ID del miembro
            benefit_code: Código del beneficio a verificar
            
        Returns:
            Dict con has_benefit, config y detalles
            
        Ejemplo:
            {
                "has_benefit": True,
                "config": {"enabled": True, "cantidad": 4},
                "nombre": "Invitados Permitidos"
            }
        """
        try:
            beneficios = self.model.get_member_benefits(miembro_id)
            
            for beneficio in beneficios:
                if beneficio["codigo"] == benefit_code:
                    return {
                        "has_benefit": True,
                        "config": beneficio["config"],
                        "nombre": beneficio["nombre"],
                        "icono": beneficio["icono"]
                    }
            
            return {
                "has_benefit": False,
                "config": {},
                "nombre": None,
                "icono": None
            }
            
        except Exception as e:
            logger.error(f"Error al verificar beneficio '{benefit_code}' para miembro {miembro_id}: {e}")
            return {
                "has_benefit": False,
                "config": {},
                "nombre": None,
                "icono": None
            }
    
    def get_benefit_value(self, miembro_id: int, benefit_code: str, default: Any = None) -> Any:
        """
        Obtiene el valor de un beneficio para un miembro.
        
        Args:
            miembro_id: ID del miembro
            benefit_code: Código del beneficio
            default: Valor por defecto si no tiene el beneficio
            
        Returns:
            El valor configurado o default
            
        Ejemplo:
            # Para "guests_allowed":
            cantidad = benefit_service.get_benefit_value(123, "guests_allowed", 0)
            # Retorna: 4 (si es Premium) o 0 (si no tiene)
        """
        check = self.check_member_has_benefit(miembro_id, benefit_code)
        
        if not check["has_benefit"]:
            return default
        
        config = check["config"]
        
        # Retornar el valor según el tipo
        if "cantidad" in config:
            return config["cantidad"]
        elif "descuento_porcentaje" in config:
            return config["descuento_porcentaje"]
        elif "enabled" in config:
            return config["enabled"]
        
        return default

    def create_benefit_type(self, data):
        """
        Crea un nuevo tipo de beneficio.
        
        Args:
            data: Dict con codigo, nombre, icono, tipo_valor, descripcion
            
        Returns:
            Result object
        """
        try:
            # Validar que no exista
            existing = self.model.get_benefit_type_by_code(data['codigo'])
            if existing:
                return Result(
                    success=False,
                    message=f"Ya existe un beneficio con el código '{data['codigo']}'"
                )
            
            # Insertar
            self.model.insert('benefit_types', data)
            
            self.logger.info(f"Tipo de beneficio creado: {data['codigo']}")
            
            return Result(
                success=True,
                message="Tipo de beneficio creado exitosamente"
            )
        
        except Exception as e:
            self.logger.error(f"Error al crear tipo de beneficio: {e}")
            return Result(
                success=False,
                message=f"Error al crear tipo de beneficio: {str(e)}"
            )

    def update_benefit_type(self, codigo, data):
        """
        Actualiza un tipo de beneficio existente.
        
        Args:
            codigo: Código del beneficio
            data: Dict con nombre, icono, tipo_valor, descripcion
            
        Returns:
            Result object
        """
        try:
            # Remover código de data si existe (no se puede cambiar)
            update_data = {k: v for k, v in data.items() if k != 'codigo'}
            
            updated = self.model.update(
                'benefit_types',
                update_data,
                {'codigo': codigo}
            )
            
            if updated:
                self.logger.info(f"Tipo de beneficio actualizado: {codigo}")
                return Result(
                    success=True,
                    message="Tipo de beneficio actualizado exitosamente"
                )
            else:
                return Result(
                    success=False,
                    message="No se encontró el tipo de beneficio o no hubo cambios"
                )
        
        except Exception as e:
            self.logger.error(f"Error al actualizar tipo de beneficio: {e}")
            return Result(
                success=False,
                message=f"Error al actualizar tipo de beneficio: {str(e)}"
            )

    def delete_benefit_type(self, codigo):
        """
        Elimina un tipo de beneficio.
        También elimina todas las configuraciones asociadas.
        
        Args:
            codigo: Código del beneficio
            
        Returns:
            Result object
        """
        try:
            with self.model.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Eliminar configuraciones asociadas
                cursor.execute(
                    "DELETE FROM category_benefits WHERE benefit_codigo = ?",
                    (codigo,)
                )
                
                # Eliminar tipo
                cursor.execute(
                    "DELETE FROM benefit_types WHERE codigo = ?",
                    (codigo,)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"Tipo de beneficio eliminado: {codigo}")
                    return Result(
                        success=True,
                        message="Tipo de beneficio eliminado exitosamente"
                    )
                else:
                    return Result(
                        success=False,
                        message="No se encontró el tipo de beneficio"
                    )
        
        except Exception as e:
            self.logger.error(f"Error al eliminar tipo de beneficio: {e}")
            return Result(
                success=False,
                message=f"Error al eliminar tipo de beneficio: {str(e)}"
            )
