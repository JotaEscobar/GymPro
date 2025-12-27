# -*- coding: utf-8 -*-
"""
Modelo para gestión de gastos
"""
from core.base_model import BaseModel
from core.response import Result


class GastoModel(BaseModel):
    """Modelo para operaciones CRUD de gastos"""

    def __init__(self):
        super().__init__()

    def create_gasto(self, tipo_gasto, monto, metodo_pago, descripcion,
                     proveedor_id=None, personal_id=None, glosa=None, usuario_id=None):
        """
        Registra un nuevo gasto
        
        Args:
            tipo_gasto: 'servicio', 'compra', 'sueldo', 'alquiler', 'tributo', 'mantenimiento', 'otro'
            monto: Monto del gasto
            metodo_pago: Método de pago utilizado
            descripcion: Descripción del gasto
            proveedor_id: ID del proveedor (opcional)
            personal_id: ID del personal (opcional, para sueldos)
            glosa: Glosa adicional (opcional)
            usuario_id: ID del usuario que registra
            
        Returns:
            Result: Resultado con gasto_id
        """
        query = """
            INSERT INTO gastos (
                tipo_gasto, monto, metodo_pago, proveedor_id, personal_id,
                descripcion, glosa, usuario_id, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'activo')
        """
        
        try:
            gasto_id = self.execute_query(
                query,
                (tipo_gasto, monto, metodo_pago, proveedor_id, personal_id,
                 descripcion, glosa, usuario_id), commit=True)
            return Result.ok("Gasto registrado exitosamente", {"gasto_id": gasto_id})
        except Exception as e:
            return Result.fail(f"Error al registrar gasto: {str(e)}")

    def get_gasto_by_id(self, gasto_id):
        """
        Obtiene un gasto por ID
        
        Args:
            gasto_id: ID del gasto
            
        Returns:
            tuple: Datos del gasto
        """
        query = """
            SELECT 
                id, fecha_hora, tipo_gasto, monto, metodo_pago,
                proveedor_id, personal_id, descripcion, glosa,
                usuario_id, estado
            FROM gastos
            WHERE id = ?
        """
        return self.execute_query(query, (gasto_id,), fetch_one=True)

    def get_gastos(self, fecha_inicio=None, fecha_fin=None, tipo_gasto=None, 
                   estado='activo', limit=100):
        """
        Obtiene gastos con filtros
        
        Args:
            fecha_inicio: Fecha inicio (opcional)
            fecha_fin: Fecha fin (opcional)
            tipo_gasto: Tipo de gasto (opcional)
            estado: Estado del gasto (default 'activo')
            limit: Límite de resultados
            
        Returns:
            list: Lista de gastos
        """
        query = """
            SELECT 
                id, fecha_hora, tipo_gasto, monto, metodo_pago,
                descripcion, estado
            FROM gastos
            WHERE estado = ?
        """
        
        params = [estado]
        
        if fecha_inicio:
            query += " AND DATE(fecha_hora) >= ?"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND DATE(fecha_hora) <= ?"
            params.append(fecha_fin)
        
        if tipo_gasto:
            query += " AND tipo_gasto = ?"
            params.append(tipo_gasto)
        
        query += " ORDER BY fecha_hora DESC LIMIT ?"
        params.append(limit)
        
        return self.execute_query(query, tuple(params), fetch_all=True)

    def get_gastos_hoy(self):
        """
        Obtiene todos los gastos del día actual
        
        Returns:
            list: Gastos de hoy
        """
        query = """
            SELECT 
                id, fecha_hora, tipo_gasto, monto, metodo_pago,
                descripcion, estado
            FROM gastos
            WHERE DATE(fecha_hora) = DATE('now', 'localtime')
            AND estado = 'activo'
            ORDER BY fecha_hora DESC
        """
        return self.execute_query(query, fetch_all=True)

    def get_total_gastos_periodo(self, fecha_inicio, fecha_fin, tipo_gasto=None):
        """
        Obtiene el total de gastos en un período
        
        Args:
            fecha_inicio: Fecha inicio
            fecha_fin: Fecha fin
            tipo_gasto: Tipo de gasto (opcional)
            
        Returns:
            float: Total de gastos
        """
        query = """
            SELECT COALESCE(SUM(monto), 0)
            FROM gastos
            WHERE DATE(fecha_hora) BETWEEN ? AND ?
            AND estado = 'activo'
        """
        
        params = [fecha_inicio, fecha_fin]
        
        if tipo_gasto:
            query += " AND tipo_gasto = ?"
            params.append(tipo_gasto)
        
        result = self.execute_query(query, tuple(params), fetch_one=True)
        return result[0] if result else 0

    def get_gastos_by_tipo(self, fecha_inicio, fecha_fin):
        """
        Obtiene gastos agrupados por tipo
        
        Args:
            fecha_inicio: Fecha inicio
            fecha_fin: Fecha fin
            
        Returns:
            list: Lista con totales por tipo de gasto
        """
        query = """
            SELECT 
                tipo_gasto,
                COUNT(*) as cantidad,
                SUM(monto) as total_monto
            FROM gastos
            WHERE DATE(fecha_hora) BETWEEN ? AND ?
            AND estado = 'activo'
            GROUP BY tipo_gasto
            ORDER BY total_monto DESC
        """
        return self.execute_query(query, (fecha_inicio, fecha_fin), fetch_all=True)

    def get_gastos_by_metodo_pago(self, fecha_inicio, fecha_fin):
        """
        Obtiene gastos agrupados por método de pago
        
        Args:
            fecha_inicio: Fecha inicio
            fecha_fin: Fecha fin
            
        Returns:
            list: Lista con totales por método de pago
        """
        query = """
            SELECT 
                metodo_pago,
                COUNT(*) as cantidad,
                SUM(monto) as total_monto
            FROM gastos
            WHERE DATE(fecha_hora) BETWEEN ? AND ?
            AND estado = 'activo'
            GROUP BY metodo_pago
            ORDER BY total_monto DESC
        """
        return self.execute_query(query, (fecha_inicio, fecha_fin), fetch_all=True)

    def anular_gasto(self, gasto_id, motivo="Anulación manual"):
        """
        Anula un gasto
        
        Args:
            gasto_id: ID del gasto
            motivo: Motivo de anulación
            
        Returns:
            Result: Resultado de la operación
        """
        query = "UPDATE gastos SET estado = 'anulado' WHERE id = ?"
        try:
            self.execute_query(query, (gasto_id,), commit=True)
            return Result.ok("Gasto eliminado exitosamente")
        except Exception as e:
            return Result.fail(f"Error al eliminar gasto: {str(e)}")

    def update_gasto(self, gasto_id, tipo_gasto, monto, metodo_pago, descripcion,
                     proveedor_id=None, personal_id=None, glosa=None):
        """
        Actualiza un gasto existente
        
        Args:
            gasto_id: ID del gasto
            tipo_gasto: Tipo de gasto
            monto: Monto
            metodo_pago: Método de pago
            descripcion: Descripción
            proveedor_id: ID del proveedor (opcional)
            personal_id: ID del personal (opcional)
            glosa: Glosa adicional (opcional)
            
        Returns:
            Result: Resultado de la operación
        """
        query = """
            UPDATE gastos
            SET tipo_gasto = ?,
                monto = ?,
                metodo_pago = ?,
                proveedor_id = ?,
                personal_id = ?,
                descripcion = ?,
                glosa = ?
            WHERE id = ? AND estado = 'activo'
        """
        
        try:
            self.execute_query(
                query,
                (tipo_gasto, monto, metodo_pago, proveedor_id, personal_id,
                 descripcion, glosa, gasto_id), commit=True)
            return Result.ok("Gasto actualizado exitosamente")
        except Exception as e:
            return Result.fail(f"Error al actualizar gasto: {str(e)}")

    def get_tipos_gasto(self):
        """
        Obtiene la lista de tipos de gasto disponibles
        
        Returns:
            list: Lista de tipos de gasto
        """
        return [
            'servicio',
            'compra',
            'sueldo',
            'alquiler',
            'tributo',
            'mantenimiento',
            'otro'
        ]
