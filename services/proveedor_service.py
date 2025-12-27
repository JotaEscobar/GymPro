# -*- coding: utf-8 -*-
from models.proveedor_model import ProveedorModel
from core.response import Result

class ProveedorService:
    def __init__(self):
        self.model = ProveedorModel()

    def get_all(self):
        return self.model.get_all()

    def guardar_proveedor(self, id_prov, data):
        # Validaciones básicas
        if not data.get('empresa'):
            return Result.fail("El nombre de la empresa es obligatorio")
        
        if id_prov:
            return self.model.update(
                id_prov, data['empresa'], data.get('ruc'), data.get('contacto'),
                data.get('telefono'), data.get('email'), data.get('direccion'),
                data.get('categoria')
            )
        else:
            return self.model.create(
                data['empresa'], data.get('ruc'), data.get('contacto'),
                data.get('telefono'), data.get('email'), data.get('direccion'),
                data.get('categoria')
            )

    def eliminar_proveedor(self, id_prov):
        return self.model.delete(id_prov)