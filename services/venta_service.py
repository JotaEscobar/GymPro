# -*- coding: utf-8 -*-
from core.response import Result
from core.database_manager import get_connection
from models.venta_model import VentaModel
from models.caja_model import CajaModel
from services.inventario_service import InventarioService

class VentaService:
    def __init__(self):
        self.venta_model = VentaModel()
        self.caja_model = CajaModel()
        self.inventario = InventarioService()
    
    def procesar_venta(self, cliente_tipo, cliente_id, total, metodo_pago,
                       items, usuario_id=None):
        conn = get_connection()
        try:
            # === BLINDAJE DE DATOS (Evita error 'list is not supported') ===
            # Aseguramos que sean tipos simples, no listas ni objetos
            c_id = int(cliente_id) if cliente_id is not None else None
            tot = float(total)
            u_id = int(usuario_id) if usuario_id is not None else None
            m_pago = str(metodo_pago)
            c_tipo = str(cliente_tipo)
            
            # 1. Crear venta
            result = self.venta_model.create_venta(
                c_tipo, c_id, tot, m_pago, u_id, items,
                connection=conn
            )
            if not result.success:
                raise Exception(result.message)
            
            venta_id = result.data['venta_id']
            
            # 2. Descontar stock
            for item in items:
                p_id = int(item['producto_id'])
                cant = int(item['cantidad'])
                
                inv_result = self.inventario.registrar_movimiento(
                    p_id, 'venta', cant,
                    f"Venta #{venta_id}", 'venta', venta_id, u_id,
                    connection=conn
                )
                if not inv_result.success:
                    raise Exception(f"Stock error prod {p_id}: {inv_result.message}")
            
            # 3. Caja
            cash_result = self.caja_model.registrar_movimiento(
                'ingreso', 'market', m_pago, tot,
                'venta', venta_id,
                f"Venta #{venta_id}",
                glosa=None, usuario_id=u_id,
                connection=conn
            )
            
            if not cash_result.success:
                raise Exception(cash_result.message)
            
            conn.commit()
            return Result.ok("Venta procesada", {"venta_id": venta_id})
            
        except Exception as e:
            conn.rollback()
            return Result.fail(f"Error transacción: {str(e)}")
        finally:
            conn.close()
    
    def extornar_venta(self, venta_id, usuario_id=None):
        conn = get_connection()
        try:
            detalle = self.venta_model.get_venta_by_id(venta_id)
            if not detalle or detalle['venta'][8] == 'cancelada':
                raise Exception("Venta no encontrada o ya anulada")
            
            # Cancelar venta
            self.venta_model.execute_query(
                "UPDATE ventas SET estado='cancelada' WHERE id=?", 
                (venta_id,), connection=conn
            )
            
            # Devolver stock
            items = detalle['detalle']
            for item in items:
                # item: id, prod_id, nombre, sku, cant...
                prod_id = item[1]
                cantidad = item[4]
                self.inventario.registrar_movimiento(
                    prod_id, 'entrada', cantidad,
                    f"Anulación Venta #{venta_id}", 'venta_anulada', venta_id, usuario_id,
                    connection=conn
                )

            # Extornar caja
            self.caja_model.execute_query(
                "UPDATE cash_movements SET estado='extornado' WHERE referencia_tipo='venta' AND referencia_id=?",
                (venta_id,), connection=conn
            )
            
            conn.commit()
            return Result.ok("Venta anulada correctamente")
            
        except Exception as e:
            conn.rollback()
            return Result.fail(f"Error al extornar: {str(e)}")
        finally:
            conn.close()

    def get_ventas(self, fecha_inicio=None, fecha_fin=None, limit=100):
        return self.venta_model.get_ventas(fecha_inicio, fecha_fin, limit=limit)
    
    def get_venta_detalle(self, venta_id):
        return self.venta_model.get_venta_by_id(venta_id)
    
    def get_productos_mas_vendidos(self, limit=10, fecha_inicio=None, fecha_fin=None):
        return self.venta_model.get_productos_mas_vendidos(limit, fecha_inicio, fecha_fin)

    def get_total_ventas_periodo(self, fecha_inicio, fecha_fin):
        return self.venta_model.get_total_ventas_periodo(fecha_inicio, fecha_fin)