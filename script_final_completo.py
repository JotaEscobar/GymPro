#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT FINAL COMPLETO - GymManager PRO
- Ajustar KPIs del Historial
- Aplicar cambios Inventario y Proveedores
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

def ajustar_historial():
    """Ajusta KPIs del historial para mejor proporción y agrega Ticket Promedio"""
    print("\n📊 Ajustando Historial de Ventas...")
    
    filepath = 'ui/historial_ventas_dialog.py'
    backup(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # AJUSTE 1: Modificar estructura de KPIs para incluir 3 tarjetas
    old_kpi_setup = '''        # KPIs (Guardamos referencias directas a los Labels)
        kpi_layout = QHBoxLayout()
        self.card_total_frame, self.lbl_total_val = self._create_card("Ventas Periodo")
        self.card_count_frame, self.lbl_count_val = self._create_card("Transacciones")
        
        kpi_layout.addWidget(self.card_total_frame)
        kpi_layout.addWidget(self.card_count_frame)
        layout.addLayout(kpi_layout)'''
    
    new_kpi_setup = '''        # KPIs Mejorados (3 tarjetas con mejor proporción)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        self.card_total_frame, self.lbl_total_val = self._create_card("💰 Ventas Periodo", "#22c55e")
        self.card_count_frame, self.lbl_count_val = self._create_card("📊 Transacciones", "#3b82f6")
        self.card_ticket_frame, self.lbl_ticket_val = self._create_card("🎯 Ticket Promedio", "#f59e0b")
        
        kpi_layout.addWidget(self.card_total_frame)
        kpi_layout.addWidget(self.card_count_frame)
        kpi_layout.addWidget(self.card_ticket_frame)
        layout.addLayout(kpi_layout)'''
    
    content = content.replace(old_kpi_setup, new_kpi_setup)
    
    # AJUSTE 2: Mejorar función _create_card con mejor diseño
    old_create_card = '''    def _create_card(self, title):
        frame = QFrame()
        frame.setStyleSheet("background: #1e293b; border-radius: 8px; padding: 15px;")
        l = QVBoxLayout(frame)
        t = QLabel(title)
        t.setStyleSheet("color: #94a3b8; font-size: 14px;")
        v = QLabel("...")
        v.setStyleSheet("font-size: 24px; font-weight: bold; color: #22c55e;")
        l.addWidget(t)
        l.addWidget(v)
        return frame, v'''
    
    new_create_card = '''    def _create_card(self, title, color="#22c55e"):
        """Crea tarjeta KPI mejorada"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border-radius: 8px;
                border: 2px solid #334155;
            }
        """)
        frame.setMinimumHeight(120)
        
        l = QVBoxLayout(frame)
        l.setSpacing(8)
        l.setContentsMargins(20, 15, 20, 15)
        
        # Título
        t = QLabel(title)
        t.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: normal;")
        t.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Valor
        v = QLabel("...")
        v.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {color};
            padding: 5px 0;
        """)
        v.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        l.addWidget(t)
        l.addWidget(v)
        l.addStretch()
        
        return frame, v'''
    
    content = content.replace(old_create_card, new_create_card)
    
    # AJUSTE 3: Actualizar _load_data para calcular ticket promedio
    old_load_data_end = '''                cnt += 1
                
        self.lbl_total_val.setText(f"S/ {tot:.2f}")
        self.lbl_count_val.setText(str(cnt))'''
    
    new_load_data_end = '''                cnt += 1
        
        # Actualizar KPIs
        self.lbl_total_val.setText(f"S/ {tot:.2f}")
        self.lbl_count_val.setText(str(cnt))
        
        # Calcular ticket promedio
        if cnt > 0:
            promedio = tot / cnt
            self.lbl_ticket_val.setText(f"S/ {promedio:.2f}")
        else:
            self.lbl_ticket_val.setText("S/ 0.00")'''
    
    content = content.replace(old_load_data_end, new_load_data_end)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✓ 3 KPIs con mejor proporción")
    print("  ✓ Ticket Promedio agregado")
    print("  ✓ Tamaños ajustados")

def corregir_inventario():
    """Aplica todas las correcciones de inventario"""
    print("\n📦 Corrigiendo Inventario...")
    
    filepath = 'ui/inventario_dialog.py'
    backup(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Agregar columna Proveedor
    content = content.replace(
        'self.table.setColumnCount(7)',
        'self.table.setColumnCount(8)'
    )
    
    content = content.replace(
        '["Producto", "Categoría", "Costo", "Precio", "Stock", "Estado", "Acciones"]',
        '["Producto", "Categoría", "Costo", "Precio", "Stock", "Estado", "Proveedor", "Acciones"]'
    )
    
    # 2. Mostrar proveedor en tabla
    old_estado = '''            self.table.setItem(r, 5, QTableWidgetItem("Activo" if p[10] else "Inactivo"))
            
            # Botones Acciones'''
    
    new_estado = '''            self.table.setItem(r, 5, QTableWidgetItem("Activo" if p[10] else "Inactivo"))
            
            # Columna Proveedor
            prov_id = p[13] if len(p) > 13 else None
            prov_nombre = "Sin proveedor"
            if prov_id:
                try:
                    provs = self.prov_service.get_all()
                    for pv in provs:
                        if pv[0] == prov_id:
                            prov_nombre = pv[1]
                            break
                except:
                    pass
            self.table.setItem(r, 6, QTableWidgetItem(prov_nombre))
            
            # Botones Acciones'''
    
    content = content.replace(old_estado, new_estado)
    
    # Ajustar índice de botones
    content = content.replace('self.table.setCellWidget(r, 6, w)', 'self.table.setCellWidget(r, 7, w)')
    
    # 3. Reordenar formulario
    old_form = '''        # Orden Excel
        f.addRow("Nombre:", inp_nom)
        f.addRow("Categoría:", combo_cat)
        f.addRow("Precio Venta:", s_precio)
        f.addRow("Stock Inicial:", s_stock)
        f.addRow("Stock Mínimo:", s_min)
        f.addRow("Cód. Barras:", inp_bar)
        f.addRow("Costo Compra:", s_costo)
        f.addRow("Proveedor:", combo_prov)'''
    
    new_form = '''        # === FORMULARIO ORDENADO LÓGICAMENTE ===
        
        # 1. IDENTIFICACIÓN
        f.addRow("📝 Nombre:", inp_nom)
        f.addRow("🏷️ Código Barras:", inp_bar)
        
        # Separador
        sep1 = QLabel("─" * 50)
        sep1.setStyleSheet("color: #475569;")
        f.addRow("", sep1)
        
        # 2. CATEGORIZACIÓN
        f.addRow("📁 Categoría:", combo_cat)
        f.addRow("🚚 Proveedor:", combo_prov)
        
        # Separador
        sep2 = QLabel("─" * 50)
        sep2.setStyleSheet("color: #475569;")
        f.addRow("", sep2)
        
        # 3. PRECIOS (Compra → Venta)
        f.addRow("💵 Costo Compra:", s_costo)
        f.addRow("💰 Precio Venta:", s_precio)
        
        # Margen de ganancia (calculado automáticamente)
        lbl_margen = QLabel("---")
        lbl_margen.setStyleSheet("font-weight: bold; color: #22c55e; font-size: 14px;")
        f.addRow("📈 Margen:", lbl_margen)
        
        def calcular_margen():
            try:
                compra = s_costo.value()
                venta = s_precio.value()
                if compra > 0:
                    margen_pct = ((venta - compra) / compra) * 100
                    margen_sol = venta - compra
                    color = "#22c55e" if margen_pct >= 0 else "#ef4444"
                    lbl_margen.setText(f"{margen_pct:.1f}% (S/ {margen_sol:.2f})")
                    lbl_margen.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 14px;")
                else:
                    lbl_margen.setText("---")
                    lbl_margen.setStyleSheet("font-weight: bold; color: #64748b; font-size: 14px;")
            except:
                lbl_margen.setText("Error")
        
        s_costo.valueChanged.connect(calcular_margen)
        s_precio.valueChanged.connect(calcular_margen)
        calcular_margen()  # Calcular inicial
        
        # Separador
        sep3 = QLabel("─" * 50)
        sep3.setStyleSheet("color: #475569;")
        f.addRow("", sep3)
        
        # 4. INVENTARIO
        f.addRow("📦 Stock Inicial:", s_stock)
        f.addRow("⚠️ Stock Mínimo:", s_min)'''
    
    content = content.replace(old_form, new_form)
    
    print("  ✓ Columna Proveedor agregada")
    print("  ✓ Formulario reordenado")
    print("  ✓ Margen automático")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def corregir_proveedores():
    """Aplica todas las correcciones de proveedores"""
    print("\n🏭 Corrigiendo Proveedores...")
    
    filepath = 'ui/proveedores_dialog.py'
    backup(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Cambiar texto del botón
    content = content.replace(
        'btn_del = QPushButton("🗑️ Desactivar Seleccionado")',
        'btn_del = QPushButton("🗑️ Eliminar Seleccionado")'
    )
    
    # 2. Agregar checkbox en formulario
    old_form_fields = '''        inp_cat = QLineEdit(data[7] if data else "")
        
        form.addRow("Empresa *:", inp_empresa)'''
    
    new_form_fields = '''        inp_cat = QLineEdit(data[7] if data else "")
        
        # Checkbox Activo/Inactivo
        from PyQt6.QtWidgets import QCheckBox
        chk_activo = QCheckBox("Proveedor Activo")
        chk_activo.setChecked(data[8] if data and len(data) > 8 else True)
        chk_activo.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        
        form.addRow("Empresa *:", inp_empresa)'''
    
    content = content.replace(old_form_fields, new_form_fields)
    
    # Agregar checkbox antes del botón guardar
    old_form_end = '''        form.addRow("Categoría:", inp_cat)
        
        hbox = QHBoxLayout()'''
    
    new_form_end = '''        form.addRow("Categoría:", inp_cat)
        form.addRow("Estado:", chk_activo)
        
        hbox = QHBoxLayout()'''
    
    content = content.replace(old_form_end, new_form_end)
    
    # Incluir checkbox en datos a guardar
    old_save_data = '''            'email': inp_email.text(), 'direccion': inp_dir.text(), 'categoria': inp_cat.text()'''
    
    new_save_data = '''            'email': inp_email.text(), 'direccion': inp_dir.text(), 
            'categoria': inp_cat.text(), 'activo': chk_activo.isChecked()'''
    
    content = content.replace(old_save_data, new_save_data)
    
    # 3. Mejorar función de eliminación
    old_delete = '''    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0: return
        pid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)[0]
        
        if QMessageBox.question(self, "Confirmar", 
            "¿Desactivar proveedor?") == QMessageBox.StandardButton.Yes:
            self.service.eliminar_proveedor(pid)
            self._load_data()'''
    
    new_delete = '''    def _delete_selected(self):
        """Elimina proveedor con validación"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un proveedor")
            return
        
        data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        pid = data[0]
        empresa = data[1]
        
        # Verificar productos asociados
        from services.producto_service import ProductoService
        prod_service = ProductoService()
        try:
            productos = prod_service.get_all_productos()
            productos_asociados = [p for p in productos if len(p) > 13 and p[13] == pid]
            
            if productos_asociados:
                mensaje = (
                    f"⚠️ ADVERTENCIA\\n\\n"
                    f"El proveedor '{empresa}' tiene {len(productos_asociados)} producto(s) asociado(s).\\n\\n"
                    f"Si lo elimina, estos productos quedarán sin proveedor.\\n\\n"
                    f"¿Continuar?"
                )
                
                respuesta = QMessageBox.warning(
                    self, "Productos Asociados", mensaje,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if respuesta != QMessageBox.StandardButton.Yes:
                    return
        except:
            pass  # Si falla la validación, continuar
        
        # Confirmación final
        respuesta = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar '{empresa}'?\\n\\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.service.eliminar_proveedor(pid)
            QMessageBox.information(self, "Éxito", f"Proveedor eliminado")
            self._load_data()'''
    
    content = content.replace(old_delete, new_delete)
    
    print("  ✓ Botón cambiado a 'Eliminar'")
    print("  ✓ Checkbox Activo agregado")
    print("  ✓ Validación de productos")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🎯 SCRIPT FINAL COMPLETO - GymManager PRO          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    if not os.path.exists('main.py'):
        print("❌ Error: Ejecutar desde GymManager_Pro/")
        return
    
    print("\n📋 Correcciones a aplicar:\n")
    print("📊 HISTORIAL:")
    print("  - Ajustar tamaño de KPIs (mejor proporción)")
    print("  - Agregar KPI: Ticket Promedio")
    print("  - Mejorar diseño visual")
    
    print("\n📦 INVENTARIO:")
    print("  - Columna Proveedor en tabla")
    print("  - Formulario reordenado lógicamente")
    print("  - Margen de ganancia automático")
    
    print("\n🏭 PROVEEDORES:")
    print("  - Botón 'Eliminar' (no Desactivar)")
    print("  - Checkbox Activo/Inactivo")
    print("  - Validación antes de eliminar")
    
    respuesta = input("\n¿Aplicar todas las correcciones? (s/n): ")
    if respuesta.lower() != 's':
        print("❌ Cancelado")
        return
    
    try:
        ajustar_historial()
        corregir_inventario()
        corregir_proveedores()
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ TODO COMPLETADO                        ║
╚══════════════════════════════════════════════════════════════╝

Archivos corregidos:
  ✓ ui/historial_ventas_dialog.py
  ✓ ui/inventario_dialog.py
  ✓ ui/proveedores_dialog.py

Próximo paso:
  python main.py

Verifica:
  📊 Historial (F3):
     - 3 KPIs bien proporcionados
     - Ticket Promedio calculado
     
  📦 Inventario (F2):
     - Columna Proveedor visible
     - Formulario ordenado
     - Margen se calcula automático
     
  🏭 Proveedores:
     - Botón Eliminar
     - Checkbox Activo
     - Advertencia al eliminar

═══════════════════════════════════════════════════════════════

🎉 ¡TODAS LAS CORRECCIONES APLICADAS!
""")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
