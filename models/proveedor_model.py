# -*- coding: utf-8 -*-
from core.base_model import BaseModel
from core.response import Result

class ProveedorModel(BaseModel):
    def __init__(self):
        super().__init__()

    def create(self, empresa, ruc, contacto, telefono, email, direccion, categoria):
        query = """
            INSERT INTO proveedores (
                empresa, ruc, contacto_nombre, telefono, email, 
                direccion, categoria_producto, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """
        try:
            id = self.execute_query(
                query, 
                (empresa, ruc, contacto, telefono, email, direccion, categoria), 
                commit=True
            )
            return Result.ok("Proveedor registrado", {"id": id})
        except Exception as e:
            return Result.fail(f"Error al crear: {e}")

    def update(self, id, empresa, ruc, contacto, telefono, email, direccion, categoria):
        query = """
            UPDATE proveedores SET 
                empresa=?, ruc=?, contacto_nombre=?, telefono=?, 
                email=?, direccion=?, categoria_producto=?
            WHERE id=?
        """
        try:
            self.execute_query(
                query, 
                (empresa, ruc, contacto, telefono, email, direccion, categoria, id), 
                commit=True
            )
            return Result.ok("Proveedor actualizado")
        except Exception as e:
            return Result.fail(f"Error al actualizar: {e}")

    def delete(self, id):
        # Soft delete (marcar como inactivo)
        query = "UPDATE proveedores SET activo=0 WHERE id=?"
        try:
            self.execute_query(query, (id,), commit=True)
            return Result.ok("Proveedor eliminado")
        except Exception as e:
            return Result.fail(f"Error al eliminar: {e}")

    def get_all(self):
        query = """
            SELECT id, empresa, ruc, contacto_nombre, telefono, 
                   email, direccion, categoria_producto 
            FROM proveedores WHERE activo=1 ORDER BY empresa
        """
        return self.execute_query(query, fetch_all=True)