# -*- coding: utf-8 -*-
"""Servicio de caja"""
from models.caja_model import CajaModel

class CajaService:
    def __init__(self):
        self.model = CajaModel()
    
    def get_sesion_abierta(self):
        return self.model.get_sesion_abierta()
    
    def abrir_caja(self, efectivo=0, yape=0, plin=0, pos_banco=0, usuario_id=None):
        result = self.model.abrir_caja(efectivo, yape, plin, pos_banco, usuario_id)
        return {"success": result.success, "message": result.message, "data": result.data}
    
    def cerrar_caja(self, caja_id, efectivo, yape, plin, pos_banco, 
                    usuario_id=None, observaciones=None):
        result = self.model.cerrar_caja(
            caja_id, efectivo, yape, plin, pos_banco, usuario_id, observaciones
        )
        return {"success": result.success, "message": result.message, "data": result.data}
    
    def get_totales_sesion(self, caja_id):
        return self.model.get_totales_sesion(caja_id)
    
    def get_saldos_actuales(self):
        return self.model.get_saldos_actuales()
    
    def get_movimientos_hoy(self):
        return self.model.get_movimientos_hoy()
    
    def get_movimientos(self, fecha_inicio, fecha_fin, categoria=None):
        return self.model.get_movimientos_periodo(fecha_inicio, fecha_fin, categoria)
    
    def registrar_movimiento(self, tipo, categoria, metodo, monto, 
                            ref_tipo=None, ref_id=None, desc=None, glosa=None, usuario_id=None):
        result = self.model.registrar_movimiento(
            tipo, categoria, metodo, monto, ref_tipo, ref_id, desc, glosa, usuario_id
        )
        return {"success": result.success, "message": result.message}
    
    def registrar_remesa(self, monto, desc="Remesa", usuario_id=None):
        result = self.model.registrar_remesa(monto, desc, usuario_id)
        return {"success": result.success, "message": result.message}
