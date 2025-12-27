# -*- coding: utf-8 -*-
"""Servicio de gastos"""
from models.gasto_model import GastoModel
from models.caja_model import CajaModel

class GastoService:
    def __init__(self):
        self.model = GastoModel()
        self.caja_model = CajaModel()
    
    def registrar_gasto(self, tipo_gasto, monto, metodo_pago, descripcion,
                       proveedor_id=None, personal_id=None, glosa=None, usuario_id=None):
        """Registra gasto y movimiento de caja"""
        # 1. Crear gasto
        result = self.model.create_gasto(
            tipo_gasto, monto, metodo_pago, descripcion,
            proveedor_id, personal_id, glosa, usuario_id
        )
        
        if not result.success:
            return {"success": False, "message": result.message}
        
        gasto_id = result.data['gasto_id']
        
        # 2. Registrar egreso en cash_movements
        cash_result = self.caja_model.registrar_movimiento(
            'egreso', 'gasto', metodo_pago, monto,
            'gasto', gasto_id, f"{tipo_gasto}: {descripcion}",
            glosa, usuario_id
        )
        
        if not cash_result.success:
            return {"success": False, 
                   "message": f"Gasto registrado pero error en caja: {cash_result.message}"}
        
        return {"success": True, "message": "Gasto registrado exitosamente",
               "data": {"gasto_id": gasto_id}}
    
    def get_gastos(self, fecha_inicio=None, fecha_fin=None, tipo=None):
        return self.model.get_gastos(fecha_inicio, fecha_fin, tipo)
    
    def get_gastos_hoy(self):
        return self.model.get_gastos_hoy()
    
    def get_total_periodo(self, fecha_inicio, fecha_fin, tipo=None):
        return self.model.get_total_gastos_periodo(fecha_inicio, fecha_fin, tipo)
    
    def anular_gasto(self, gasto_id, motivo="Anulación"):
        result = self.model.anular_gasto(gasto_id, motivo)
        return {"success": result.success, "message": result.message}
    
    def get_tipos_gasto(self):
        return self.model.get_tipos_gasto()
