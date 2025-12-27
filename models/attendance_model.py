# -*- coding: utf-8 -*-
"""
Modelo para gestión de asistencias
"""
import sqlite3
from datetime import datetime
from core.base_model import BaseModel
from core.config import Config

class AttendanceModel(BaseModel):
    """Modelo para operaciones CRUD de asistencias"""

    def insert_check_in(self, miembro_id, fecha_hora_entrada):
        """
        Registra una asistencia de entrada.
        Valida que no exista ya una entrada el mismo día.
        
        Args:
            miembro_id: ID del miembro
            fecha_hora_entrada: Fecha y hora de entrada
            
        Raises:
            ValueError: Si ya registró asistencia hoy
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya registró hoy
            fecha_hoy = datetime.now().strftime(Config.DATE_FORMAT)
            cursor.execute("""
                SELECT 1
                FROM attendance
                WHERE miembro_id = ? AND DATE(fecha_hora_entrada) = ?
                LIMIT 1
            """, (miembro_id, fecha_hoy))
            
            existe = cursor.fetchone()
            
            if existe:
                raise ValueError("Ya registró asistencia hoy")
            
            # Insertar nueva asistencia
            cursor.execute("""
                INSERT INTO attendance (miembro_id, fecha_hora_entrada)
                VALUES (?, ?)
            """, (miembro_id, fecha_hora_entrada))
            
            conn.commit()
            
            self.logger.info(
                f"Asistencia registrada: Miembro={miembro_id}, Fecha={fecha_hora_entrada}"
            )

    def delete_last_check_in(self, miembro_id):
        """
        Elimina la última entrada registrada de un miembro.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            bool: True si se eliminó, False si no había entradas
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Buscar última entrada
            cursor.execute("""
                SELECT id FROM attendance
                WHERE miembro_id = ?
                ORDER BY fecha_hora_entrada DESC
                LIMIT 1
            """, (miembro_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return False
            
            last_id = row[0]
            
            # Eliminar
            cursor.execute("DELETE FROM attendance WHERE id = ?", (last_id,))
            conn.commit()
            
            self.logger.info(f"Asistencia eliminada: ID={last_id}, Miembro={miembro_id}")
            
            return True

    def get_todays_log(self):
        """
        Devuelve una lista de asistencias registradas hoy con información del miembro.
        
        Returns:
            list: Lista de tuplas (codigo, nombre, plan, vencimiento, hora_entrada)
        """
        fecha_hoy = datetime.now().strftime(Config.DATE_FORMAT)
        
        # Query optimizada con subconsulta para obtener solo el plan vigente
        query = """
            SELECT 
                m.codigo_membresia,
                m.nombre,
                COALESCE(p.nombre_plan, 'Sin plan') AS nombre_plan,
                pay.fecha_vencimiento,
                a.fecha_hora_entrada
            FROM attendance a
            JOIN members m ON a.miembro_id = m.id
            LEFT JOIN (
                SELECT 
                    miembro_id, 
                    MAX(fecha_vencimiento) AS fecha_vencimiento, 
                    plan_id
                FROM payments
                GROUP BY miembro_id
            ) pay ON pay.miembro_id = m.id
            LEFT JOIN plans p ON pay.plan_id = p.id
            WHERE DATE(a.fecha_hora_entrada) = ?
            ORDER BY a.fecha_hora_entrada DESC
        """
        
        return self.execute_query(query, (fecha_hoy,))

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
        # Query optimizada para obtener plan vigente en cada fecha
        query = """
            SELECT 
                a.fecha_hora_entrada,
                COALESCE(p.nombre_plan, 'Sin plan') AS nombre_plan
            FROM attendance a
            LEFT JOIN (
                SELECT 
                    pay.miembro_id,
                    pay.plan_id,
                    pay.fecha_pago,
                    pay.fecha_vencimiento
                FROM payments pay
                WHERE pay.miembro_id = ?
            ) pay ON a.miembro_id = pay.miembro_id
                AND DATE(a.fecha_hora_entrada) BETWEEN pay.fecha_pago AND pay.fecha_vencimiento
            LEFT JOIN plans p ON pay.plan_id = p.id
            WHERE a.miembro_id = ?
              AND DATE(a.fecha_hora_entrada) BETWEEN ? AND ?
            ORDER BY a.fecha_hora_entrada DESC
        """
        
        return self.execute_query(query, (miembro_id, miembro_id, desde, hasta))
