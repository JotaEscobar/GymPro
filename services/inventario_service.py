# -*- coding: utf-8 -*-
"""Servicio de movimientos de inventario"""
from core.base_model import BaseModel
from core.response import Result
from models.producto_model import ProductoModel

class InventarioService:
    def __init__(self):
        self.base = BaseModel()
        self.producto_model = ProductoModel()
    
    def registrar_movimiento(self, producto_id, tipo, cantidad, motivo, 
                            referencia_tipo=None, referencia_id=None, usuario_id=None, connection=None):
        """Registra movimiento y actualiza stock. Soporta transacción externa."""
        
        # Obtener stock actual
        # Nota: Usamos lectura normal aunque haya transacción, para simplificar.
        producto = self.producto_model.get_producto_by_id(producto_id)
        if not producto:
            return Result.fail("Producto no encontrado")
        
        stock_actual = producto[7]
        
        # Calcular nuevo stock
        if tipo in ['entrada', 'ajuste']:
            stock_nuevo = stock_actual + cantidad
        elif tipo in ['salida', 'venta']:
            stock_nuevo = stock_actual - cantidad
            if stock_nuevo < 0:
                return Result.fail(f"Stock insuficiente para {producto[3]}")
        else:
            return Result.fail("Tipo de movimiento inválido")
        
        # Registrar movimiento
        query = """
            INSERT INTO inventario_movimientos (
                producto_id, tipo_movimiento, cantidad, stock_anterior,
                stock_nuevo, motivo, usuario_id, referencia_tipo, referencia_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            movement_id = self.base.execute_query(
                query,
                (producto_id, tipo, cantidad, stock_actual, stock_nuevo,
                 motivo, usuario_id, referencia_tipo, referencia_id),
                commit=(connection is None),
                connection=connection
            )
            
            # Actualizar stock en producto (Usando update genérico de base que acepta connection)
            self.base.update(
                'productos', 
                {'stock_actual': stock_nuevo}, 
                {'id': producto_id},
                connection=connection
            )
            
            return Result.ok(
                "Movimiento registrado", 
                {"movement_id": movement_id, "stock_nuevo": stock_nuevo}
            )
        except Exception as e:
            return Result.fail(f"Error al registrar movimiento: {str(e)}")
    
    def get_movimientos_producto(self, producto_id, limit=50):
        query = """
            SELECT fecha_hora, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, motivo
            FROM inventario_movimientos WHERE producto_id = ? ORDER BY fecha_hora DESC LIMIT ?
        """
        return self.base.execute_query(query, (producto_id, limit), fetch_all=True)