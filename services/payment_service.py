# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para pagos
"""
from datetime import datetime, timedelta
from models.payment_model import PaymentModel
from services.plan_service import PlanService
from core.config import Config
from core.logger import logger

class PaymentService:
    """Servicio para procesar pagos y validar membresías"""
    
    def __init__(self):
        self.model = PaymentModel()
        self.plan_service = PlanService()

    def validate_membership_status(self, miembro_id):
        """
        Valida el estado de la membresía de un miembro.
        MÉTODO UNIFICADO - Usado por todos los servicios.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            dict: {
                'status': str (Activo/Vencido/Sin Plan),
                'dias_restantes': int o None,
                'fecha_vencimiento': str o None,
                'alerta': str o None
            }
        """
        fecha_vencimiento_str = self.model.get_latest_expiry_date(miembro_id)
        
        if not fecha_vencimiento_str:
            return {
                'status': Config.STATUS_NO_PLAN,
                'dias_restantes': None,
                'fecha_vencimiento': None,
                'alerta': 'Sin plan activo'
            }
        
        try:
            fecha_vencimiento = datetime.strptime(
                fecha_vencimiento_str, 
                Config.DATE_FORMAT
            ).date()
            fecha_hoy = datetime.now().date()
            dias_restantes = (fecha_vencimiento - fecha_hoy).days
            
            if dias_restantes < 0:
                return {
                    'status': Config.STATUS_EXPIRED,
                    'dias_restantes': dias_restantes,
                    'fecha_vencimiento': fecha_vencimiento_str,
                    'alerta': f'Membresía vencida hace {abs(dias_restantes)} días'
                }
            elif dias_restantes <= Config.ALERT_DAYS_THRESHOLD:
                return {
                    'status': Config.STATUS_ACTIVE,
                    'dias_restantes': dias_restantes,
                    'fecha_vencimiento': fecha_vencimiento_str,
                    'alerta': f'¡Alerta! Tu membresía vence en {dias_restantes} días'
                }
            else:
                return {
                    'status': Config.STATUS_ACTIVE,
                    'dias_restantes': dias_restantes,
                    'fecha_vencimiento': fecha_vencimiento_str,
                    'alerta': None
                }
                
        except ValueError as e:
            logger.error(f"Error al parsear fecha de vencimiento: {e}")
            return {
                'status': Config.STATUS_UNKNOWN,
                'dias_restantes': None,
                'fecha_vencimiento': fecha_vencimiento_str,
                'alerta': 'Error en formato de fecha'
            }

    def process_payment(self, miembro_id, plan_id, monto_pagado, fecha_pago_str):
        """
        Procesa un pago y calcula la nueva fecha de vencimiento.
        Extiende la membresía desde la fecha de vencimiento actual si existe.
        
        Args:
            miembro_id: ID del miembro
            plan_id: ID del plan
            monto_pagado: Monto pagado
            fecha_pago_str: Fecha del pago (YYYY-MM-DD)
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        # Validación de entradas
        try:
            miembro_id = int(miembro_id)
            plan_id = int(plan_id)
            monto_pagado = float(monto_pagado)
            fecha_pago = datetime.strptime(fecha_pago_str, Config.DATE_FORMAT)
        except ValueError as e:
            return {
                "success": False,
                "message": f"Error de validación: {e}"
            }
            
        if monto_pagado <= 0:
            return {
                "success": False,
                "message": "El monto debe ser positivo"
            }

        # Obtener duración del plan
        planes = self.plan_service.get_all_plans(include_inactive=True)
        plan = next((p for p in planes if p[0] == plan_id), None)
        
        if not plan:
            return {
                "success": False,
                "message": "Plan no encontrado"
            }
            
        duracion_dias = plan[3]

        # Determinar fecha de inicio de la nueva vigencia
        current_date_str = datetime.now().strftime(Config.DATE_FORMAT)
        last_expiry_date_str = self.model.get_latest_valid_membership(
            miembro_id, 
            current_date_str
        )
        
        if last_expiry_date_str:
            # Extender desde última fecha de vencimiento
            last_expiry_date = datetime.strptime(
                last_expiry_date_str, 
                Config.DATE_FORMAT
            )
            fecha_inicio_vigencia = last_expiry_date + timedelta(days=1)
        else:
            # Primera membresía: inicia desde fecha de pago
            fecha_inicio_vigencia = fecha_pago

        # Calcular fecha de vencimiento
        fecha_vencimiento = fecha_inicio_vigencia + timedelta(days=duracion_dias - 1)
        
        # Registrar el pago
        resultado = self.model.register_payment(
            miembro_id, 
            plan_id, 
            monto_pagado, 
            fecha_pago.strftime(Config.DATE_FORMAT), 
            fecha_vencimiento.strftime(Config.DATE_FORMAT)
        )

        if resultado.get("success"):
            mensaje = (
                f"Pago registrado correctamente. "
                f"Vigencia: {fecha_inicio_vigencia.strftime(Config.DATE_FORMAT)} "
                f"a {fecha_vencimiento.strftime(Config.DATE_FORMAT)}"
            )
            return {
                "success": True,
                "message": mensaje,
                "data": {
                    "payment_id": resultado.get("payment_id"),
                    "fecha_inicio": fecha_inicio_vigencia.strftime(Config.DATE_FORMAT),
                    "fecha_vencimiento": fecha_vencimiento.strftime(Config.DATE_FORMAT)
                }
            }
        else:
            return resultado

    def get_member_payments(self, miembro_id):
        """Retorna el historial de pagos de un miembro"""
        return self.model.get_member_payments(miembro_id)
    
    def get_payments_by_member_id(self, miembro_id, desde=None, hasta=None):
        """Retorna pagos con filtro de fechas opcional"""
        return self.model.get_payments_by_member_id(miembro_id, desde, hasta)

    def get_payments_by_codigo(self, codigo_membresia, desde=None, hasta=None):
        """Retorna pagos usando código de membresía"""
        return self.model.get_payments_by_codigo(codigo_membresia, desde, hasta)
    
    def get_payment_id_by_fecha_plan_monto(self, codigo_membresia, fecha, plan, monto):
        """Busca ID de pago específico para extornar"""
        return self.model.get_payment_id_by_fecha_plan_monto(
            codigo_membresia, fecha, plan, monto
        )
    
    def delete_payment_by_id(self, id_pago):
        """Elimina (extorna) un pago por ID"""
        return self.model.delete_payment_by_id(id_pago)
