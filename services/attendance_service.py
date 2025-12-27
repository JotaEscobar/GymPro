# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para asistencias
"""
from datetime import datetime
from models.attendance_model import AttendanceModel
from services.member_service import MemberService
from services.payment_service import PaymentService
from core.config import Config
from core.logger import logger

class AttendanceService:
    """Servicio para gestión de asistencias"""
    
    def __init__(self):
        self.model = AttendanceModel()
        self.member_service = MemberService()
        self.payment_service = PaymentService()

    def register_check_in(self, member_identifier):
        """
        Registra la asistencia del miembro si cumple con los requisitos.
        Evita segunda marcación el mismo día.
        USA VALIDACIÓN UNIFICADA DE MEMBRESÍA.
        
        Args:
            member_identifier: DNI o código de membresía
            
        Returns:
            dict: {
                'status': str,
                'message': str,
                'alerta': str o None,
                'miembro_nombre': str (opcional),
                'fecha_vencimiento': str (opcional)
            }
        """
        # Buscar miembro
        miembro_data = self.member_service.find_member_by_identifier(member_identifier)

        if not miembro_data:
            return {
                'status': 'Error',
                'message': "Miembro no encontrado por DNI o Código",
                'alerta': None
            }

        miembro_id = miembro_data[0]
        miembro_nombre = miembro_data[1]

        # ✅ USAR VALIDACIÓN UNIFICADA
        validacion = self.payment_service.validate_membership_status(miembro_id)
        
        status = validacion['status']
        alerta = validacion['alerta']
        fecha_vencimiento = validacion['fecha_vencimiento']

        # Si está vencido o sin plan, denegar acceso
        if status == Config.STATUS_EXPIRED:
            logger.warning(
                f"Acceso denegado: {miembro_nombre} ({member_identifier}) - Membresía vencida"
            )
            return {
                'status': 'Vencido',
                'message': f"Acceso Denegado. La membresía de {miembro_nombre} expiró el {fecha_vencimiento}",
                'alerta': alerta
            }
        
        if status == Config.STATUS_NO_PLAN:
            logger.warning(
                f"Acceso denegado: {miembro_nombre} ({member_identifier}) - Sin plan activo"
            )
            return {
                'status': 'Sin Plan',
                'message': f"Acceso Denegado. {miembro_nombre} no tiene un plan activo",
                'alerta': alerta
            }

        # Registrar asistencia con validación de duplicado
        fecha_check_in = datetime.now().strftime(Config.DATETIME_FORMAT)

        try:
            self.model.insert_check_in(miembro_id, fecha_check_in)
            
            logger.info(
                f"Asistencia registrada: {miembro_nombre} ({member_identifier})"
            )
            
            message = f"Acceso concedido. Tu plan vence: {fecha_vencimiento}"

            return {
                'status': 'Éxito',
                'message': message,
                'alerta': alerta,
                'miembro_nombre': miembro_nombre,
                'fecha_vencimiento': fecha_vencimiento
            }
            
        except ValueError as ve:
            if "Ya registró asistencia hoy" in str(ve):
                return {
                    'status': 'YaMarcado',
                    'message': "Ya registró asistencia hoy",
                    'alerta': None
                }
            return {
                'status': 'Error',
                'message': f"No se pudo registrar la asistencia: {str(ve)}",
                'alerta': None
            }
        except Exception as e:
            logger.error(f"Error al registrar asistencia: {e}")
            return {
                'status': 'Error',
                'message': f"Error al registrar asistencia: {str(e)}",
                'alerta': None
            }

    def get_todays_log(self):
        """
        Obtiene el log de asistencia de hoy desde el modelo.
        
        Returns:
            list: Lista de tuplas con datos de asistencias de hoy
        """
        return self.model.get_todays_log()

    def delete_last_check_in_by_code(self, codigo_membresia):
        """
        Elimina la última entrada registrada para el miembro con el código dado.
        
        Args:
            codigo_membresia: Código de membresía
            
        Returns:
            bool: True si se eliminó, False si no había entradas
        """
        miembro_data = self.member_service.find_member_by_identifier(codigo_membresia)
        
        if not miembro_data:
            return False

        miembro_id = miembro_data[0]
        return self.model.delete_last_check_in(miembro_id)
    
    def get_log_by_member_and_range(self, miembro_id, desde, hasta):
        """
        Obtiene el log de asistencias de un miembro en un rango de fechas.
        
        Args:
            miembro_id: ID del miembro
            desde: Fecha inicio (YYYY-MM-DD)
            hasta: Fecha fin (YYYY-MM-DD)
            
        Returns:
            list: Lista de tuplas (fecha_hora_entrada, nombre_plan)
        """
        return self.model.get_log_by_member_and_range(miembro_id, desde, hasta)
