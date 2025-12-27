# -*- coding: utf-8 -*-
"""
Modelo para gestión de caja y movimientos de efectivo
"""
from core.base_model import BaseModel
from core.response import Result


class CajaModel(BaseModel):
    """Modelo para operaciones de caja y cash movements"""

    def __init__(self):
        super().__init__()

    # ==================== SESIONES DE CAJA ====================

    def get_sesion_abierta(self):
        """
        Obtiene la sesión de caja actualmente abierta
        
        Returns:
            tuple: Datos de la sesión abierta o None
        """
        query = """
            SELECT 
                id, fecha_apertura, usuario_apertura_id,
                efectivo_inicial, yape_inicial, plin_inicial, pos_banco_inicial,
                estado
            FROM caja_sesiones
            WHERE estado = 'abierta'
            ORDER BY fecha_apertura DESC
            LIMIT 1
        """
        return self.execute_query(query, fetch_one=True)

    def abrir_caja(self, efectivo_inicial=0, yape_inicial=0, plin_inicial=0, 
                   pos_banco_inicial=0, usuario_id=None):
        """
        Abre una nueva sesión de caja
        
        Args:
            efectivo_inicial: Monto inicial en efectivo
            yape_inicial: Monto inicial en Yape
            plin_inicial: Monto inicial en Plin
            pos_banco_inicial: Monto inicial en POS/Banco
            usuario_id: ID del usuario que abre (opcional)
            
        Returns:
            Result: Resultado con caja_sesion_id
        """
        # Verificar que no haya caja abierta
        caja_abierta = self.get_sesion_abierta()
        if caja_abierta:
            return Result.fail("Ya existe una caja abierta")
        
        query = """
            INSERT INTO caja_sesiones (
                usuario_apertura_id,
                efectivo_inicial, yape_inicial, plin_inicial, pos_banco_inicial,
                estado
            ) VALUES (?, ?, ?, ?, ?, 'abierta')
        """
        
        try:
            caja_sesion_id = self.execute_query(
                query,
                (usuario_id, efectivo_inicial, yape_inicial, plin_inicial, pos_banco_inicial), commit=True)
            return Result.ok("Caja abierta exitosamente", {"caja_sesion_id": caja_sesion_id})
        except Exception as e:
            return Result.fail(f"Error al abrir caja: {str(e)}")

    def cerrar_caja(self, caja_sesion_id, efectivo_cierre, yape_cierre, plin_cierre,
                    pos_banco_cierre, usuario_cierre_id=None, observaciones=None):
        """
        Cierra una sesión de caja
        
        Args:
            caja_sesion_id: ID de la sesión a cerrar
            efectivo_cierre: Monto contado en efectivo
            yape_cierre: Monto contado en Yape
            plin_cierre: Monto contado en Plin
            pos_banco_cierre: Monto contado en POS/Banco
            usuario_cierre_id: ID del usuario que cierra
            observaciones: Observaciones del cierre
            
        Returns:
            Result: Resultado de la operación
        """
        # Calcular totales del sistema
        totales = self.get_totales_sesion(caja_sesion_id)
        
        if not totales:
            return Result.fail("No se encontró la sesión de caja")
        
        # Calcular diferencias
        diferencia_efectivo = efectivo_cierre - totales['efectivo_esperado']
        diferencia_yape = yape_cierre - totales['yape_esperado']
        diferencia_plin = plin_cierre - totales['plin_esperado']
        diferencia_pos_banco = pos_banco_cierre - totales['pos_banco_esperado']
        
        # Determinar estado
        tiene_diferencias = any([
            abs(diferencia_efectivo) > 0.01,
            abs(diferencia_yape) > 0.01,
            abs(diferencia_plin) > 0.01,
            abs(diferencia_pos_banco) > 0.01
        ])
        
        estado = 'con_diferencias' if tiene_diferencias else 'cerrada'
        
        query = """
            UPDATE caja_sesiones
            SET fecha_cierre = datetime('now', 'localtime'),
                usuario_cierre_id = ?,
                efectivo_cierre = ?,
                yape_cierre = ?,
                plin_cierre = ?,
                pos_banco_cierre = ?,
                total_ingresos_sistema = ?,
                total_egresos_sistema = ?,
                diferencia_efectivo = ?,
                diferencia_yape = ?,
                diferencia_plin = ?,
                diferencia_pos_banco = ?,
                observaciones = ?,
                estado = ?
            WHERE id = ?
        """
        
        try:
            self.execute_query(
                query,
                (usuario_cierre_id, efectivo_cierre, yape_cierre, plin_cierre, pos_banco_cierre,
                 totales['total_ingresos'], totales['total_egresos'],
                 diferencia_efectivo, diferencia_yape, diferencia_plin, diferencia_pos_banco,
                 observaciones, estado, caja_sesion_id), commit=True)
            
            # Vincular movimientos a esta sesión
            self.execute_query(
                "UPDATE cash_movements SET caja_sesion_id = ? WHERE caja_sesion_id IS NULL",
                (caja_sesion_id,), commit=True)
            
            return Result.ok(
                f"Caja cerrada ({estado})",
                {
                    "diferencias": {
                        "efectivo": diferencia_efectivo,
                        "yape": diferencia_yape,
                        "plin": diferencia_plin,
                        "pos_banco": diferencia_pos_banco
                    }
                }
            )
        except Exception as e:
            return Result.fail(f"Error al cerrar caja: {str(e)}")

    def get_totales_sesion(self, caja_sesion_id):
        """
        Calcula los totales de una sesión de caja
        
        Args:
            caja_sesion_id: ID de la sesión
            
        Returns:
            dict: Totales calculados por método de pago
        """
        # Obtener montos iniciales
        sesion = self.execute_query("""SELECT efectivo_inicial, yape_inicial, plin_inicial, pos_banco_inicial
               FROM caja_sesiones WHERE id = ?""",
            (caja_sesion_id,), fetch_one=True)
        
        if not sesion or sesion == True:
            return None
        
        efectivo_ini, yape_ini, plin_ini, pos_banco_ini = sesion
        
        # Calcular ingresos y egresos por método
        query = """
            SELECT 
                metodo_pago,
                tipo_movimiento,
                SUM(monto) as total
            FROM cash_movements
            WHERE (caja_sesion_id = ? OR caja_sesion_id IS NULL)
            AND estado = 'activo'
            GROUP BY metodo_pago, tipo_movimiento
        """
        
        movimientos = self.execute_query(query, (caja_sesion_id,), fetch_all=True)
        
        # Inicializar totales
        totales = {
            'efectivo_ingresos': 0,
            'efectivo_egresos': 0,
            'yape_ingresos': 0,
            'yape_egresos': 0,
            'plin_ingresos': 0,
            'plin_egresos': 0,
            'pos_banco_ingresos': 0,
            'pos_banco_egresos': 0
        }
        
        # Sumar movimientos
        for metodo, tipo, total in movimientos:
            key = f"{metodo}_{tipo}s"  # ej: 'efectivo_ingresos'
            if key in totales:
                totales[key] = total
        
        # Calcular esperados
        return {
            'efectivo_esperado': efectivo_ini + totales['efectivo_ingresos'] - totales['efectivo_egresos'],
            'yape_esperado': yape_ini + totales['yape_ingresos'] - totales['yape_egresos'],
            'plin_esperado': plin_ini + totales['plin_ingresos'] - totales['plin_egresos'],
            'pos_banco_esperado': pos_banco_ini + totales['pos_banco_ingresos'] - totales['pos_banco_egresos'],
            'total_ingresos': sum([totales['efectivo_ingresos'], totales['yape_ingresos'], 
                                  totales['plin_ingresos'], totales['pos_banco_ingresos']]),
            'total_egresos': sum([totales['efectivo_egresos'], totales['yape_egresos'], 
                                 totales['plin_egresos'], totales['pos_banco_egresos']])
        }

    # ==================== MOVIMIENTOS DE EFECTIVO ====================

    def registrar_movimiento(self, tipo_movimiento, categoria, metodo_pago, monto,
                            referencia_tipo=None, referencia_id=None, descripcion=None,
                            glosa=None, usuario_id=None, connection=None):
        """
        Registra un movimiento de efectivo.
        🔥 ACTUALIZADO: Soporta transacción externa mediante 'connection'.
        
        Args:
            tipo_movimiento: 'ingreso' o 'egreso'
            categoria: 'membresia', 'clase', 'market', 'gasto', 'ajuste', 'remesa'
            metodo_pago: 'efectivo', 'yape', 'plin', 'pos_banco'
            monto: Monto del movimiento
            referencia_tipo: Tipo de referencia (opcional)
            referencia_id: ID de referencia (opcional)
            descripcion: Descripción del movimiento
            glosa: Glosa adicional (opcional)
            usuario_id: ID del usuario que registra
            connection: Objeto sqlite3.Connection opcional para transacciones atómicas
            
        Returns:
            Result: Resultado con movement_id
        """
        query = """
            INSERT INTO cash_movements (
                tipo_movimiento, categoria, metodo_pago, monto,
                referencia_tipo, referencia_id, descripcion, glosa, usuario_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            # 🔥 Si hay connection, NO hacemos commit aquí (lo hace el servicio padre)
            do_commit = (connection is None)
            
            movement_id = self.execute_query(
                query,
                (tipo_movimiento, categoria, metodo_pago, monto,
                 referencia_tipo, referencia_id, descripcion, glosa, usuario_id),
                commit=do_commit,
                connection=connection  # Pasamos la conexión al BaseModel
            )
            return Result.ok("Movimiento registrado exitosamente", {"movement_id": movement_id})
        except Exception as e:
            return Result.fail(f"Error al registrar movimiento: {str(e)}")

    def get_movimientos_hoy(self):
        """
        Obtiene todos los movimientos del día actual
        
        Returns:
            list: Movimientos de hoy
        """
        query = """
            SELECT 
                id, fecha_hora, tipo_movimiento, categoria, metodo_pago,
                monto, descripcion, estado
            FROM cash_movements
            WHERE DATE(fecha_hora) = DATE('now', 'localtime')
            AND estado = 'activo'
            ORDER BY fecha_hora DESC
        """
        return self.execute_query(query, fetch_all=True)

    def get_movimientos_periodo(self, fecha_inicio, fecha_fin, categoria=None):
        """
        Obtiene movimientos en un período
        
        Args:
            fecha_inicio: Fecha inicio
            fecha_fin: Fecha fin
            categoria: Filtrar por categoría (opcional)
            
        Returns:
            list: Movimientos del período
        """
        query = """
            SELECT 
                id, fecha_hora, tipo_movimiento, categoria, metodo_pago,
                monto, descripcion, estado
            FROM cash_movements
            WHERE DATE(fecha_hora) BETWEEN ? AND ?
            AND estado = 'activo'
        """
        
        params = [fecha_inicio, fecha_fin]
        
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        
        query += " ORDER BY fecha_hora DESC"
        
        return self.execute_query(query, tuple(params), fetch_all=True)

    def extornar_movimiento(self, movement_id):
        """
        Extorna (anula) un movimiento
        
        Args:
            movement_id: ID del movimiento
            
        Returns:
            Result: Resultado de la operación
        """
        query = "UPDATE cash_movements SET estado = 'extornado' WHERE id = ?"
        try:
            self.execute_query(query, (movement_id,), commit=True)
            return Result.ok("Movimiento eliminado exitosamente")
        except Exception as e:
            return Result.fail(f"Error al eliminar movimiento: {str(e)}")

    def get_saldos_actuales(self):
        """
        Calcula los saldos actuales de la caja abierta
        
        Returns:
            dict: Saldos por método de pago
        """
        sesion = self.get_sesion_abierta()
        
        if not sesion:
            return None
        
        return self.get_totales_sesion(sesion[0])

    def registrar_remesa(self, monto, descripcion="Remesa de efectivo", usuario_id=None):
        """
        Registra una remesa (traslado de efectivo a banco)
        
        Args:
            monto: Monto a remesar
            descripcion: Descripción de la remesa
            usuario_id: ID del usuario que registra
            
        Returns:
            Result: Resultado de la operación
        """
        # Registrar egreso de efectivo
        egreso = self.registrar_movimiento(
            'egreso', 'remesa', 'efectivo', monto,
            descripcion=f"{descripcion} (salida)", usuario_id=usuario_id
        )
        
        if not egreso.success:
            return egreso
        
        # Registrar ingreso en banco
        ingreso = self.registrar_movimiento(
            'ingreso', 'remesa', 'pos_banco', monto,
            descripcion=f"{descripcion} (ingreso)", usuario_id=usuario_id
        )
        
        if ingreso.success:
            return Result.ok("Remesa registrada exitosamente")
        return ingreso