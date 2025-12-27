# -*- coding: utf-8 -*-
"""
Modelo para gestión de pagos
"""
import sqlite3
from datetime import datetime
from core.base_model import BaseModel
from core.config import Config

class PaymentModel(BaseModel):
    """Modelo para operaciones CRUD de pagos"""
    
    def register_payment(self, miembro_id, plan_id, monto_pagado, fecha_pago, fecha_vencimiento):
        """
        Registra un nuevo pago en la base de datos.
        
        Args:
            miembro_id: ID del miembro
            plan_id: ID del plan
            monto_pagado: Monto del pago
            fecha_pago: Fecha del pago (YYYY-MM-DD)
            fecha_vencimiento: Fecha de vencimiento (YYYY-MM-DD)
            
        Returns:
            dict: {"success": bool, "message": str, "payment_id": int}
        """
        try:
            data = {
                'miembro_id': miembro_id,
                'plan_id': plan_id,
                'monto_pagado': monto_pagado,
                'fecha_pago': fecha_pago,
                'fecha_vencimiento': fecha_vencimiento
            }
            
            payment_id = self.insert('payments', data)
            
            self.logger.info(
                f"Pago registrado: ID={payment_id}, Miembro={miembro_id}, "
                f"Monto={monto_pagado}, Vence={fecha_vencimiento}"
            )
            
            return {
                "success": True,
                "message": "Pago registrado correctamente",
                "payment_id": payment_id
            }
            
        except ValueError as e:
            error_msg = str(e)
            if "FOREIGN KEY constraint failed" in error_msg:
                return {
                    "success": False,
                    "message": "Error: El miembro o el plan no existen"
                }
            return {
                "success": False,
                "message": f"Error de integridad: {error_msg}"
            }
        except Exception as e:
            self.logger.error(f"Error al registrar pago: {e}")
            return {
                "success": False,
                "message": f"Error al registrar pago: {e}"
            }

    def get_member_payments(self, miembro_id):
        """
        Obtiene el historial de pagos de un miembro ordenado del más reciente al más antiguo.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            list: Lista de tuplas (id_pago, nombre_plan, monto, fecha_pago, fecha_vencimiento)
        """
        query = """
            SELECT 
                p.id, 
                pl.nombre_plan, 
                p.monto_pagado, 
                p.fecha_pago, 
                p.fecha_vencimiento 
            FROM payments p
            JOIN plans pl ON p.plan_id = pl.id
            WHERE p.miembro_id = ?
            ORDER BY p.fecha_pago DESC, p.id DESC
        """
        return self.execute_query(query, (miembro_id,))

    def get_latest_expiry_date(self, miembro_id):
        """
        🔥 MÉTODO CENTRALIZADO - ÚNICA FUENTE DE VERDAD
        Obtiene la fecha de vencimiento más lejana del miembro.
        Usado por MemberService, PaymentService y AttendanceService.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            str: Fecha en formato YYYY-MM-DD o None si no tiene pagos
        """
        query = """
            SELECT MAX(fecha_vencimiento)
            FROM payments
            WHERE miembro_id = ?
        """
        resultado = self.execute_query(query, (miembro_id,), fetch_one=True)
        return resultado[0] if resultado and resultado[0] else None

    def get_payment_by_id(self, payment_id):
        """
        Obtiene un pago por su ID.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            tuple: (id, miembro_id, plan_id, fecha_pago, fecha_vencimiento, monto_pagado) o None
        """
        query = """
            SELECT id, miembro_id, plan_id, fecha_pago, fecha_vencimiento, monto_pagado
            FROM payments
            WHERE id = ?
        """
        return self.execute_query(query, (payment_id,), fetch_one=True)

    def get_latest_valid_membership(self, miembro_id, current_date_str):
        """
        Obtiene la fecha de vencimiento más lejana y aún válida (futura).
        
        Args:
            miembro_id: ID del miembro
            current_date_str: Fecha actual en formato YYYY-MM-DD
            
        Returns:
            str: Fecha de vencimiento más lejana o None
        """
        query = """
            SELECT MAX(fecha_vencimiento) 
            FROM payments 
            WHERE miembro_id = ? AND fecha_vencimiento >= ?
        """
        resultado = self.execute_query(
            query, 
            (miembro_id, current_date_str),
            fetch_one=True
        )
        return resultado[0] if resultado and resultado[0] else None
    
    def get_payments_by_member_id(self, miembro_id, desde=None, hasta=None):
        """
        Obtiene pagos de un miembro con filtro de fechas opcional.
        
        Args:
            miembro_id: ID del miembro
            desde: Fecha inicio (YYYY-MM-DD) opcional
            hasta: Fecha fin (YYYY-MM-DD) opcional
            
        Returns:
            list: Lista de tuplas (fecha_pago, nombre_plan, monto, fecha_vencimiento)
        """
        query = """
            SELECT p.fecha_pago, 
                   pl.nombre_plan, 
                   p.monto_pagado, 
                   p.fecha_vencimiento
            FROM payments p
            JOIN plans pl ON p.plan_id = pl.id
            WHERE p.miembro_id = ?
        """
        params = [miembro_id]

        if desde and hasta:
            query += " AND p.fecha_pago BETWEEN ? AND ?"
            params.extend([desde, hasta])

        query += " ORDER BY p.fecha_pago DESC, p.id DESC"

        return self.execute_query(query, tuple(params))

    def get_payments_by_codigo(self, codigo_membresia, desde=None, hasta=None):
        """
        Obtiene pagos usando el código de membresía en lugar del ID.
        
        Args:
            codigo_membresia: Código del miembro
            desde: Fecha inicio (YYYY-MM-DD) opcional
            hasta: Fecha fin (YYYY-MM-DD) opcional
            
        Returns:
            list: Lista de tuplas (fecha_pago, nombre_plan, monto, fecha_vencimiento)
        """
        query = """
            SELECT p.fecha_pago, 
                   pl.nombre_plan, 
                   p.monto_pagado, 
                   p.fecha_vencimiento
            FROM payments p
            JOIN plans pl ON p.plan_id = pl.id
            JOIN members m ON p.miembro_id = m.id
            WHERE m.codigo_membresia = ?
        """
        params = [codigo_membresia]

        if desde and hasta:
            query += " AND p.fecha_pago BETWEEN ? AND ?"
            params.extend([desde, hasta])

        query += " ORDER BY p.fecha_pago DESC, p.id DESC"

        return self.execute_query(query, tuple(params))

    def get_payment_id_by_fecha_plan_monto(self, codigo_membresia, fecha, plan, monto):
        """
        Busca el ID de un pago específico por sus características.
        Usado para extornar pagos.
        
        Args:
            codigo_membresia: Código del miembro
            fecha: Fecha del pago
            plan: Nombre del plan
            monto: Monto del pago
            
        Returns:
            int: ID del pago o None
        """
        query = """
            SELECT p.id
            FROM payments p
            JOIN plans pl ON p.plan_id = pl.id
            JOIN members m ON p.miembro_id = m.id
            WHERE m.codigo_membresia = ? 
              AND p.fecha_pago = ? 
              AND pl.nombre_plan = ? 
              AND p.monto_pagado = ?
            ORDER BY p.fecha_pago DESC, p.id DESC
            LIMIT 1
        """
        resultado = self.execute_query(
            query,
            (codigo_membresia, fecha, plan, monto),
            fetch_one=True
        )
        return resultado[0] if resultado else None

    def delete_payment_by_id(self, id_pago):
        """
        Elimina un pago por su ID (extornar pago).
        
        Args:
            id_pago: ID del pago a eliminar
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            deleted = self.delete('payments', {'id': id_pago})
            
            if deleted:
                self.logger.info(f"Pago ID={id_pago} eliminado (extornado)")
                return {
                    "success": True,
                    "message": "Pago eliminado correctamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontró el pago a eliminar"
                }
                
        except Exception as e:
            self.logger.error(f"Error al eliminar pago ID={id_pago}: {e}")
            return {
                "success": False,
                "message": f"Error al eliminar pago: {e}"
            }
