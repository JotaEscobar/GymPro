# -*- coding: utf-8 -*-
"""Servicio de productos"""
import pandas as pd
from models.producto_model import ProductoModel
from core.validators import Validator
from core.response import Result

def validate_not_empty(value):
    """Helper: valida que un valor no esté vacío"""
    return value and str(value).strip()

def validate_positive_number(value):
    """Helper: valida que un valor sea número positivo"""
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False

class ProductoService:
    def __init__(self):
        self.model = ProductoModel()
    
    def get_all_productos(self, include_inactive=False):
        return self.model.get_all_productos(include_inactive)
    
    def get_producto(self, producto_id):
        return self.model.get_producto_by_id(producto_id)
    
    def search_productos(self, term):
        return self.model.search_productos(term)
    
    def get_bajo_stock(self):
        return self.model.get_productos_bajo_stock()
    
    def create_producto(self, nombre, categoria_id, precio, stock_inicial=0, 
                       stock_minimo=0, codigo_barras=None, precio_compra=0, proveedor_id=None):
        # Validar
        if not validate_not_empty(nombre):
            return Result.fail("Nombre requerido")
        if not validate_positive_number(precio):
            return Result.fail("Precio inválido")
        
        # Generar SKU
        sku = self.model.get_next_sku(categoria_id)
        if not sku:
            return Result.fail("Categoría inválida")
        
        # El modelo ya retorna un objeto Result, lo pasamos directamente
        return self.model.create_producto(
            sku, nombre, categoria_id, precio, stock_inicial, 
            stock_minimo, codigo_barras, None, precio_compra, proveedor_id
        )
    
    def update_producto(self, producto_id, nombre, categoria_id, precio, 
                       stock_minimo, codigo_barras=None, precio_compra=0, proveedor_id=None):
        if not validate_not_empty(nombre):
            return Result.fail("Nombre requerido")
        if not validate_positive_number(precio):
            return Result.fail("Precio inválido")
        
        return self.model.update_producto(
            producto_id, nombre, categoria_id, precio, stock_minimo, codigo_barras,
            None, precio_compra, proveedor_id
        )
    
    def update_stock(self, producto_id, nuevo_stock):
        return self.model.update_stock(producto_id, nuevo_stock)
    
    def toggle_active(self, producto_id):
        return self.model.toggle_active(producto_id)
    
    def get_categorias(self):
        return self.model.get_all_categorias()

    def importar_productos_masivo(self, file_path):
        """
        Importa productos desde Excel.
        Columnas esperadas: Nombre, Categoria, PrecioVenta, Stock, Minimo, Barras
        """
        try:
            df = pd.read_excel(file_path)
            
            # Obtener mapa de categorías (Nombre -> ID)
            cats_db = self.get_categorias()
            # cats_db es una lista de tuplas (id, nombre, prefijo...)
            # Creamos un diccionario { "NOMBRE_MAYUSCULAS": ID }
            cat_map = {str(c[1]).strip().upper(): c[0] for c in cats_db} 
            
            exitos = 0
            errores = []
            
            for index, row in df.iterrows():
                try:
                    nombre = str(row['Nombre']).strip()
                    cat_nombre = str(row['Categoria']).strip().upper()
                    precio = float(row['PrecioVenta'])
                    
                    if cat_nombre not in cat_map:
                        errores.append(f"Fila {index+2}: Categoría '{cat_nombre}' no existe en el sistema.")
                        continue
                        
                    cat_id = cat_map[cat_nombre]
                    
                    # Generar SKU
                    sku = self.model.get_next_sku(cat_id)
                    
                    # Crear
                    self.model.create_producto(
                        sku, nombre, cat_id, precio, 
                        int(row.get('Stock', 0)), 
                        int(row.get('Minimo', 0)),
                        str(row.get('Barras', ''))
                    )
                    exitos += 1
                except Exception as e:
                    errores.append(f"Fila {index+2}: Error al procesar - {str(e)}")
            
            summary = f"Importación finalizada. Éxitos: {exitos}. Errores: {len(errores)}."
            if errores:
                return Result.fail(summary + "\n\nDetalle de errores (primeros 5):\n" + "\n".join(errores[:5]))
            
            return Result.ok(summary)
            
        except Exception as e:
            return Result.fail(f"Error al leer el archivo Excel: {str(e)}")