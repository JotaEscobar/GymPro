#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parche de Ajustes Finos - Market View
- Botón eliminar: volver a "-"
- Agregar botones +/- para cantidad
- Confirmación antes de cobrar
"""

import os
import shutil
from datetime import datetime

def backup(filepath):
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"✓ Backup: {os.path.basename(backup_path)}")
    return None

def aplicar_ajustes():
    print("\n🔧 Aplicando ajustes finos a Market View...\n")
    
    filepath = 'ui/market_view.py'
    backup(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # AJUSTE 1: Cambiar estructura de tabla del carrito
    # Buscar donde se define setColumnCount
    old_cart_setup = '''        self.table_cart.setColumnCount(4)
        self.table_cart.setHorizontalHeaderLabels(["Prod", "Cant", "Total", ""])'''
    
    new_cart_setup = '''        self.table_cart.setColumnCount(5)
        self.table_cart.setHorizontalHeaderLabels(["Prod", "Cant", "+/-", "Total", ""])'''
    
    if old_cart_setup in content:
        content = content.replace(old_cart_setup, new_cart_setup)
        print("✓ Tabla del carrito: columna +/- agregada")
    
    # Ajustar anchos de columnas
    old_widths = '''        self.table_cart.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_cart.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table_cart.setColumnWidth(3, 30)'''
    
    new_widths = '''        self.table_cart.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_cart.setColumnWidth(1, 50)   # Cantidad
        self.table_cart.setColumnWidth(2, 70)   # Botones +/-
        self.table_cart.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table_cart.setColumnWidth(4, 40)   # Botón eliminar'''
    
    if old_widths in content:
        content = content.replace(old_widths, new_widths)
        print("✓ Anchos de columnas ajustados")
    
    # AJUSTE 2: Reemplazar función _render_cart completa
    # Encontrar inicio de la función
    start_marker = '    def _render_cart(self):'
    end_marker = '    def _on_quantity_changed(self, row, col):'
    
    if start_marker in content and end_marker in content:
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        new_render_cart = '''    def _render_cart(self):
        """Renderiza el carrito con controles mejorados"""
        self.table_cart.setRowCount(0)
        
        # Desconectar señal para evitar loops
        try:
            self.table_cart.cellChanged.disconnect()
        except:
            pass
        
        tot = 0
        for r, item in enumerate(self.carrito):
            self.table_cart.insertRow(r)
            self.table_cart.setRowHeight(r, 50)  # Altura aumentada
            
            p = item['data']
            cant = item['cant']
            price = p[6] * (1 - self.descuento_global/100)
            sub = price * cant
            tot += sub
            
            # Col 0: Nombre del producto (no editable)
            nombre_item = QTableWidgetItem(p[3])
            nombre_item.setFlags(nombre_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_cart.setItem(r, 0, nombre_item)
            
            # Col 1: Cantidad (EDITABLE)
            cant_item = QTableWidgetItem(str(cant))
            cant_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cant_item.setForeground(QColor("#3b82f6"))
            font = cant_item.font()
            font.setBold(True)
            font.setPointSize(12)
            cant_item.setFont(font)
            self.table_cart.setItem(r, 1, cant_item)
            
            # Col 2: Botones +/- para ajustar cantidad
            widget_botones = QWidget()
            layout_botones = QHBoxLayout(widget_botones)
            layout_botones.setContentsMargins(2, 2, 2, 2)
            layout_botones.setSpacing(2)
            
            # Botón -
            btn_menos = QPushButton("−")
            btn_menos.setStyleSheet("""
                QPushButton {
                    background: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background: #dc2626;
                }
            """)
            btn_menos.clicked.connect(lambda checked, idx=r: self._decrementar_cantidad(idx))
            
            # Botón +
            btn_mas = QPushButton("+")
            btn_mas.setStyleSheet("""
                QPushButton {
                    background: #22c55e;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background: #16a34a;
                }
            """)
            btn_mas.clicked.connect(lambda checked, idx=r: self._incrementar_cantidad(idx))
            
            layout_botones.addWidget(btn_menos)
            layout_botones.addWidget(btn_mas)
            self.table_cart.setCellWidget(r, 2, widget_botones)
            
            # Col 3: Total (no editable)
            total_item = QTableWidgetItem(f"S/ {sub:.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setForeground(QColor("#22c55e"))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font_total = total_item.font()
            font_total.setBold(True)
            total_item.setFont(font_total)
            self.table_cart.setItem(r, 3, total_item)
            
            # Col 4: Botón eliminar (emoji -)
            btn_del = QPushButton("−")
            btn_del.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #ef4444;
                    border: 1px solid #ef4444;
                    border-radius: 4px;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 6px;
                }
                QPushButton:hover {
                    background: #ef4444;
                    color: white;
                }
            """)
            btn_del.clicked.connect(lambda checked, idx=r: self._remove_from_cart(idx))
            self.table_cart.setCellWidget(r, 4, btn_del)
        
        # Conectar evento de cambio de cantidad
        self.table_cart.cellChanged.connect(self._on_quantity_changed)
        
        # Actualizar total
        self.lbl_total.setText(f"S/ {tot:.2f}")
    
    def _incrementar_cantidad(self, idx):
        """Incrementa la cantidad de un producto en el carrito"""
        if 0 <= idx < len(self.carrito):
            producto = self.carrito[idx]['data']
            cantidad_actual = self.carrito[idx]['cant']
            
            # Validar stock
            if cantidad_actual + 1 > producto[7]:
                QMessageBox.warning(self, "Stock Insuficiente",
                    f"Solo hay {producto[7]} unidades disponibles")
                return
            
            self.carrito[idx]['cant'] += 1
            self.table_cart.cellChanged.disconnect()
            self._render_cart()
    
    def _decrementar_cantidad(self, idx):
        """Decrementa la cantidad de un producto en el carrito"""
        if 0 <= idx < len(self.carrito):
            cantidad_actual = self.carrito[idx]['cant']
            
            if cantidad_actual > 1:
                self.carrito[idx]['cant'] -= 1
                self.table_cart.cellChanged.disconnect()
                self._render_cart()
            else:
                # Si es 1, eliminar el producto
                self._remove_from_cart(idx)
    
'''
        
        # Reemplazar
        content = content[:start_idx] + new_render_cart + content[end_idx:]
        print("✓ Función _render_cart actualizada")
        print("  - Botón eliminar: '-' (emoji)")
        print("  - Botones +/- agregados")
    
    # AJUSTE 3: Agregar confirmación antes de cobrar
    old_cobrar = '''    def _cobrar(self):
        if not self.carrito: return
        if not self.caja_service.get_sesion_abierta():
            QMessageBox.warning(self, "Caja Cerrada", "No se puede vender.")
            return'''
    
    new_cobrar = '''    def _cobrar(self):
        if not self.carrito: return
        if not self.caja_service.get_sesion_abierta():
            QMessageBox.warning(self, "Caja Cerrada", "No se puede vender.")
            return
        
        # CONFIRMACIÓN ANTES DE PROCESAR
        total_items = sum(item['cant'] for item in self.carrito)
        total_productos = len(self.carrito)
        
        mensaje = f"¿Confirmar venta?\\n\\n"
        mensaje += f"Productos: {total_productos}\\n"
        mensaje += f"Unidades: {total_items}\\n"
        mensaje += f"Total: {self.lbl_total.text()}\\n"
        mensaje += f"Método: {self.combo_metodo.currentText()}"
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar Venta",
            mensaje,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return'''
    
    if old_cobrar in content:
        content = content.replace(old_cobrar, new_cobrar)
        print("✓ Confirmación agregada antes de cobrar")
    
    # Guardar cambios
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Ajustes aplicados exitosamente\n")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🎨 AJUSTES FINOS - Market View                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    if not os.path.exists('main.py'):
        print("❌ Error: Ejecutar desde GymManager_Pro/")
        return
    
    respuesta = input("¿Aplicar ajustes? (s/n): ")
    if respuesta.lower() != 's':
        print("Cancelado")
        return
    
    try:
        aplicar_ajustes()
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║                       ✅ COMPLETADO                          ║
╚══════════════════════════════════════════════════════════════╝

Cambios aplicados:
  ✓ Botón eliminar: "-" (minimalista)
  ✓ Botones +/- para ajustar cantidad
  ✓ Confirmación antes de procesar venta

Próximo paso:
  python main.py

Prueba:
  1. Agrega productos al carrito
  2. Usa los botones +/- para ajustar cantidad
  3. Al cobrar, verás confirmación
""")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
