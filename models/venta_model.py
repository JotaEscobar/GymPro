# -*- coding: utf-8 -*-
from core.base_model import BaseModel
from core.response import Result

class VentaModel(BaseModel):
    def __init__(self):
        super().__init__()

    def create_venta(self, cliente_tipo, cliente_id, total, metodo_pago, 
                     usuario_id=None, detalle_items=None, connection=None):
        # Insertar venta principal
        venta_query = """
            INSERT INTO ventas (
                cliente_tipo, cliente_id, total, metodo_pago, usuario_id, estado
            ) VALUES (?, ?, ?, ?, ?, 'completada')
        """
        
        try:
            venta_id = self.execute_query(
                venta_query,
                (cliente_tipo, cliente_id, total, metodo_pago, usuario_id), 
                commit=(connection is None),
                connection=connection
            )
            
            # Insertar detalle de venta
            if detalle_items:
                # CORRECCIÓN: 'precio_unit' -> 'precio_unitario'
                detalle_query = """
                    INSERT INTO ventas_detalle (
                        venta_id, producto_id, cantidad, precio_unitario,
                        descuento_porcentaje, subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """
                
                for item in detalle_items:
                    self.execute_query(
                        detalle_query,
                        (venta_id, item['producto_id'], item['cantidad'],
                         item['precio_unit'], item.get('descuento_porcentaje', 0),
                         item['subtotal']),
                        commit=(connection is None),
                        connection=connection
                    )
            
            return Result.ok("Venta registrada exitosamente", {"venta_id": venta_id})
        except Exception as e:
            return Result.fail(f"Error al crear venta: {str(e)}")

    def get_venta_by_id(self, venta_id):
        # Obtener venta principal
        venta_query = """
            SELECT v.id, v.fecha_hora, v.cliente_tipo, v.cliente_id,
                CASE WHEN v.cliente_tipo = 'miembro' THEN m.nombre ELSE 'Visitante' END as cliente_nombre,
                v.total, v.metodo_pago, v.usuario_id, v.estado
            FROM ventas v
            LEFT JOIN members m ON v.cliente_id = m.id
            WHERE v.id = ?
        """
        venta = self.execute_query(venta_query, (venta_id,), fetch_one=True)
        if not venta: return None
        
        # Obtener detalle (CORRECCIÓN: precio_unitario)
        detalle_query = """
            SELECT vd.id, vd.producto_id, p.nombre, p.sku,
                vd.cantidad, vd.precio_unitario, vd.descuento_porcentaje, vd.subtotal
            FROM ventas_detalle vd
            INNER JOIN productos p ON vd.producto_id = p.id
            WHERE vd.venta_id = ?
        """
        detalle = self.execute_query(detalle_query, (venta_id,), fetch_all=True)
        return {'venta': venta, 'detalle': detalle}

    def get_ventas(self, fecha_inicio=None, fecha_fin=None, cliente_id=None, estado='completada', limit=100):
        query = """
            SELECT v.id, v.fecha_hora, v.cliente_tipo,
                CASE WHEN v.cliente_tipo = 'miembro' THEN m.nombre ELSE 'Visitante' END as cliente_nombre,
                v.total, v.metodo_pago, v.estado
            FROM ventas v
            LEFT JOIN members m ON v.cliente_id = m.id
            WHERE v.estado = ?
        """
        params = [estado]
        if fecha_inicio:
            query += " AND DATE(v.fecha_hora) >= ?"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND DATE(v.fecha_hora) <= ?"
            params.append(fecha_fin)
        if cliente_id:
            query += " AND v.cliente_id = ?"
            params.append(cliente_id)
        query += " ORDER BY v.fecha_hora DESC LIMIT ?"
        params.append(limit)
        return self.execute_query(query, tuple(params), fetch_all=True)

    def get_ventas_hoy(self):
        query = """
            SELECT v.id, v.fecha_hora, v.cliente_tipo,
                CASE WHEN v.cliente_tipo = 'miembro' THEN m.nombre ELSE 'Visitante' END as cliente_nombre,
                v.total, v.metodo_pago, v.estado
            FROM ventas v
            LEFT JOIN members m ON v.cliente_id = m.id
            WHERE DATE(v.fecha_hora) = DATE('now', 'localtime') AND v.estado = 'completada'
            ORDER BY v.fecha_hora DESC
        """
        return self.execute_query(query, fetch_all=True)

    def get_total_ventas_periodo(self, fecha_inicio, fecha_fin):
        query = "SELECT COALESCE(SUM(total), 0) FROM ventas WHERE DATE(fecha_hora) BETWEEN ? AND ? AND estado = 'completada'"
        result = self.execute_query(query, (fecha_inicio, fecha_fin), fetch_one=True)
        return result[0] if result else 0

    def get_productos_mas_vendidos(self, limit=10, fecha_inicio=None, fecha_fin=None):
        query = """
            SELECT p.id, p.nombre, p.sku, SUM(vd.cantidad) as cantidad_total, SUM(vd.subtotal) as venta_total
            FROM ventas_detalle vd
            INNER JOIN productos p ON vd.producto_id = p.id
            INNER JOIN ventas v ON vd.venta_id = v.id
            WHERE v.estado = 'completada'
        """
        params = []
        if fecha_inicio and fecha_fin:
            query += " AND DATE(v.fecha_hora) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        query += " GROUP BY p.id, p.nombre, p.sku ORDER BY cantidad_total DESC LIMIT ?"
        params.append(limit)
        return self.execute_query(query, tuple(params), fetch_all=True)

    def cancel_venta(self, venta_id):
        query = "UPDATE ventas SET estado = 'cancelada' WHERE id = ?"
        try:
            self.execute_query(query, (venta_id,), commit=True)
            return Result.ok("Venta cancelada exitosamente")
        except Exception as e:
            return Result.fail(f"Error: {str(e)}")

    def get_ventas_by_metodo_pago(self, fecha_inicio, fecha_fin):
        query = """
            SELECT metodo_pago, COUNT(*) as cantidad_ventas, SUM(total) as total_monto
            FROM ventas WHERE DATE(fecha_hora) BETWEEN ? AND ? AND estado = 'completada'
            GROUP BY metodo_pago ORDER BY total_monto DESC
        """
        return self.execute_query(query, (fecha_inicio, fecha_fin), fetch_all=True)