# -*- coding: utf-8 -*-
"""
Servicio de Lógica de Negocio para Planes Combo (Nx1)
"""
from models.combo_model import ComboModel
from models.member_model import MemberModel
from models.plan_model import PlanModel
from core.response import Result
from core.logger import logger
from typing import List, Dict, Tuple

class ComboService:
    """Servicio para gestión de combos (planes múltiples beneficiarios)"""
    
    def __init__(self):
        self.combo_model = ComboModel()
        self.member_model = MemberModel()
        self.plan_model = PlanModel()
    
    def register_combo_payment(self, payment_id: int, titular_id: int, 
                              beneficiarios_ids: List[int], plan_id: int) -> Result:
        """
        Registra un pago combo prorrateando el monto entre todos los miembros.
        Cada miembro obtiene su propio registro de pago con el monto correspondiente.
        
        Ejemplo: Plan S/ 100 para 2 personas → S/ 50 cada uno
        
        Args:
            payment_id: ID del pago ya registrado del titular
            titular_id: ID del miembro titular (quien registró el pago)
            beneficiarios_ids: Lista de IDs de los demás miembros del combo
            plan_id: ID del plan
            
        Returns:
            Result indicando éxito/error
        """
        try:
            # Obtener información del plan
            plan = self.plan_model.get_plan_by_id(plan_id)
            if not plan:
                return Result.fail("Plan no encontrado", "NOT_FOUND")
            
            max_personas = plan[4]  # 🔥 FIX: columna cantidad_personas (índice 4)
            
            # Validar cantidad de miembros
            total_personas = 1 + len(beneficiarios_ids)  # 1 titular + demás miembros
            
            if total_personas > max_personas:
                return Result.fail(
                    f"El plan permite máximo {max_personas} personas. "
                    f"Intentando registrar {total_personas}",
                    "EXCEEDED_LIMIT"
                )
            
            # Obtener datos del pago del titular
            from models.payment_model import PaymentModel
            payment_model = PaymentModel()
            titular_payment = payment_model.get_payment_by_id(payment_id)
            
            if not titular_payment:
                return Result.fail("Pago del titular no encontrado", "NOT_FOUND")
            
            # Datos del pago original
            monto_total = float(titular_payment[5])  # monto_pagado total
            fecha_pago = titular_payment[3]  # fecha_pago
            fecha_vencimiento = titular_payment[4]  # fecha_vencimiento
            
            # 🔥 PRORRATEO AUTOMÁTICO: Dividir el monto entre todos los miembros
            monto_por_persona = round(monto_total / total_personas, 2)
            
            # Ajustar el monto del titular al monto prorrateado
            with payment_model.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE payments SET monto_pagado = ? WHERE id = ?",
                    (monto_por_persona, payment_id)
                )
                conn.commit()
            
            logger.info(f"Monto prorrateado: S/ {monto_total:.2f} / {total_personas} = S/ {monto_por_persona:.2f} por persona")
            
            # Registrar titular en payment_members
            self.combo_model.add_member_to_combo(payment_id, titular_id, es_titular=True)
            
            # Registrar los demás miembros del combo
            for miembro_id in beneficiarios_ids:
                # Validar que no sea el mismo titular
                if miembro_id == titular_id:
                    return Result.fail(
                        "El titular no puede agregarse como miembro adicional",
                        "VALIDATION_ERROR"
                    )
                
                # 🔥 Validar que el miembro exista (consulta directa, sin método adicional)
                with self.member_model.get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT nombre FROM members WHERE id = ?", (miembro_id,))
                    miembro = cursor.fetchone()
                
                if not miembro:
                    return Result.fail(
                        f"Miembro ID {miembro_id} no encontrado",
                        "NOT_FOUND"
                    )
                
                miembro_nombre = miembro[0]
                
                # Validar que no esté duplicado
                if self.combo_model.is_member_in_combo(payment_id, miembro_id):
                    return Result.fail(
                        f"El miembro {miembro_nombre} ya está en este combo",
                        "DUPLICATE_ERROR"
                    )
                
                # 🔥 CREAR PAGO INDIVIDUAL CON MONTO PRORRATEADO
                miembro_payment_result = payment_model.register_payment(
                    miembro_id=miembro_id,
                    plan_id=plan_id,
                    monto_pagado=monto_por_persona,  # Monto prorrateado
                    fecha_pago=fecha_pago,
                    fecha_vencimiento=fecha_vencimiento
                )
                
                if not miembro_payment_result.get("success"):
                    logger.error(f"Error al crear pago para miembro {miembro_id}: {miembro_payment_result.get('message')}")
                    return Result.fail(
                        f"Error al registrar pago de {miembro_nombre}",
                        "PAYMENT_ERROR"
                    )
                
                miembro_payment_id = miembro_payment_result.get("payment_id")
                
                # 🔥 IMPORTANTE: Vincular en payment_members de DOS formas:
                # 1. El miembro con su propio payment_id (como titular de su pago)
                self.combo_model.add_member_to_combo(miembro_payment_id, miembro_id, es_titular=True)
                
                # 2. El miembro también vinculado al payment_id del titular (tracking del combo)
                self.combo_model.add_member_to_combo(payment_id, miembro_id, es_titular=False)
                
                logger.info(
                    f"Pago creado para {miembro_nombre} (ID {miembro_id}): "
                    f"payment_id={miembro_payment_id}, monto=S/ {monto_por_persona:.2f}"
                )
            
            logger.info(
                f"Combo registrado exitosamente: Payment {payment_id}, {total_personas} personas, "
                f"S/ {monto_por_persona:.2f} c/u (Total: S/ {monto_total:.2f})"
            )
            
            return Result.ok(
                f"Combo registrado: {total_personas} personas × S/ {monto_por_persona:.2f} = S/ {monto_total:.2f}",
                {
                    "payment_id": payment_id,
                    "total_personas": total_personas,
                    "monto_total": monto_total,
                    "monto_por_persona": monto_por_persona,
                    "miembros_adicionales": len(beneficiarios_ids)
                }
            )
            
        except Exception as e:
            logger.error(f"Error al registrar combo: {e}")
            return Result.fail(f"Error al registrar combo: {str(e)}", "REGISTER_ERROR")
    
    def add_beneficiario_to_existing_combo(self, payment_id: int, 
                                          miembro_id: int, plan_id: int) -> Result:
        """
        Agrega un beneficiario a un combo existente.
        
        Args:
            payment_id: ID del pago combo
            miembro_id: ID del nuevo beneficiario
            plan_id: ID del plan
            
        Returns:
            Result indicando éxito/error
        """
        try:
            # Verificar límite del plan
            plan = self.plan_model.get_plan_by_id(plan_id)
            if not plan:
                return Result.fail("Plan no encontrado", "NOT_FOUND")
            
            max_personas = plan[4]  # 🔥 FIX: cantidad_personas
            current_count = self.combo_model.count_combo_members(payment_id)
            
            if current_count >= max_personas:
                return Result.fail(
                    f"Combo completo. Máximo {max_personas} personas",
                    "EXCEEDED_LIMIT"
                )
            
            # Validar que el miembro exista
            miembro = self.member_model.find_member_by_id(miembro_id)
            if not miembro:
                return Result.fail("Miembro no encontrado", "NOT_FOUND")
            
            # Validar que no esté ya en el combo
            if self.combo_model.is_member_in_combo(payment_id, miembro_id):
                return Result.fail(
                    f"{miembro['nombre_completo']} ya está en este combo",
                    "DUPLICATE_ERROR"
                )
            
            # Agregar
            self.combo_model.add_member_to_combo(payment_id, miembro_id, es_titular=False)
            
            logger.info(f"Beneficiario {miembro_id} agregado al combo {payment_id}")
            
            return Result.ok(
                f"{miembro['nombre_completo']} agregado al combo",
                {"beneficiario_id": miembro_id}
            )
            
        except Exception as e:
            logger.error(f"Error al agregar beneficiario: {e}")
            return Result.fail(f"Error: {str(e)}", "ADD_ERROR")
    
    def remove_beneficiario(self, payment_id: int, miembro_id: int) -> Result:
        """
        Remueve un beneficiario de un combo.
        No permite remover al titular.
        
        Args:
            payment_id: ID del pago
            miembro_id: ID del beneficiario a remover
            
        Returns:
            Result indicando éxito/error
        """
        try:
            success = self.combo_model.remove_member_from_combo(payment_id, miembro_id)
            
            if success:
                logger.info(f"Beneficiario {miembro_id} removido del combo {payment_id}")
                return Result.ok("Beneficiario removido del combo")
            else:
                return Result.fail("No se pudo remover el beneficiario", "REMOVE_ERROR")
            
        except ValueError as e:
            return Result.fail(str(e), "VALIDATION_ERROR")
        except Exception as e:
            logger.error(f"Error al remover beneficiario: {e}")
            return Result.fail(f"Error: {str(e)}", "REMOVE_ERROR")
    
    def get_combo_details(self, payment_id: int) -> Dict:
        """
        Obtiene detalles completos de un combo.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            Dict con titular, beneficiarios y totales
        """
        try:
            members = self.combo_model.get_combo_members(payment_id)
            
            titular = None
            beneficiarios = []
            
            for member in members:
                member_data = {
                    "id": member[2],
                    "nombre": member[3],
                    "codigo": member[4],
                    "fecha_asignacion": member[6]
                }
                
                if member[5]:  # es_titular
                    titular = member_data
                else:
                    beneficiarios.append(member_data)
            
            return {
                "payment_id": payment_id,
                "titular": titular,
                "beneficiarios": beneficiarios,
                "total_personas": len(members),
                "es_combo": len(members) > 1
            }
            
        except Exception as e:
            logger.error(f"Error al obtener detalles del combo {payment_id}: {e}")
            return {
                "payment_id": payment_id,
                "titular": None,
                "beneficiarios": [],
                "total_personas": 0,
                "es_combo": False
            }
    
    def get_member_combo_status(self, miembro_id: int) -> Dict:
        """
        Obtiene el estado de combo de un miembro.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            Dict con información de combo activo
        """
        try:
            combo_info = self.combo_model.get_active_combo_info(miembro_id)
            
            if combo_info:
                return {
                    "tiene_combo_activo": True,
                    "payment_id": combo_info[0],
                    "plan_nombre": combo_info[1],
                    "fecha_vencimiento": combo_info[2],
                    "es_titular": bool(combo_info[3]),
                    "titular_nombre": combo_info[4] if not combo_info[3] else None,
                    "titular_codigo": combo_info[5] if not combo_info[3] else None
                }
            else:
                return {
                    "tiene_combo_activo": False,
                    "payment_id": None,
                    "plan_nombre": None,
                    "fecha_vencimiento": None,
                    "es_titular": False,
                    "titular_nombre": None,
                    "titular_codigo": None
                }
            
        except Exception as e:
            logger.error(f"Error al obtener estado de combo del miembro {miembro_id}: {e}")
            return {"tiene_combo_activo": False}
    
    def validate_beneficiario_available(self, miembro_id: int) -> Result:
        """
        Valida si un miembro puede ser agregado como beneficiario a un combo.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            Result indicando si está disponible
        """
        try:
            # Verificar que el miembro exista
            miembro = self.member_model.find_member_by_id(miembro_id)
            if not miembro:
                return Result.fail("Miembro no encontrado", "NOT_FOUND")
            
            # Verificar si ya tiene membresía activa
            # (Opcional: el gym puede decidir si permitir o no)
            if self.combo_model.has_active_combo_membership(miembro_id):
                return Result.fail(
                    f"{miembro['nombre_completo']} ya tiene una membresía activa",
                    "ALREADY_ACTIVE"
                )
            
            return Result.ok(
                f"{miembro['nombre_completo']} disponible",
                {"miembro": miembro}
            )
            
        except Exception as e:
            logger.error(f"Error al validar beneficiario {miembro_id}: {e}")
            return Result.fail(f"Error: {str(e)}", "VALIDATION_ERROR")
