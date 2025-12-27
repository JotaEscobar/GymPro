# -*- coding: utf-8 -*-
"""
Gestor de base de datos SQLite
Crea TODO automáticamente: Tablas CORE + FASE 1 + Datos iniciales
"""
import sqlite3
import json
from core.config import Config
from core.logger import logger


def get_connection():
    """Establece y devuelve la conexión a la BD con claves foráneas activadas."""
    try:
        conn = sqlite3.connect(Config.DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logger.error(f"No se pudo conectar a la base de datos: {e}")
        raise


def create_initial_tables():
    """
    Crea todas las tablas (CORE + FASE 1), índices y datos iniciales.
    Se ejecuta automáticamente al iniciar la app.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        logger.info("Inicializando base de datos...")
        
        # ==================== TABLAS CORE ====================
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                dni TEXT UNIQUE NOT NULL,
                contacto TEXT,
                email TEXT,
                direccion TEXT,
                fecha_registro DATE NOT NULL,
                codigo_membresia TEXT UNIQUE NOT NULL,
                foto_path TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miembro_id INTEGER NOT NULL,
                fecha_medicion DATE NOT NULL,
                peso REAL,
                talla REAL,
                grasa_corporal REAL,
                resistencia_fisica TEXT,
                pecho REAL,
                hombros REAL,
                cintura REAL,
                cadera REAL,
                biceps REAL,
                antebrazo REAL,
                muslo REAL,
                gemelos REAL,
                cuello REAL,
                comentarios TEXT,
                FOREIGN KEY(miembro_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_plan TEXT NOT NULL UNIQUE,
                precio REAL NOT NULL CHECK(precio > 0),
                duracion_dias INTEGER NOT NULL CHECK(duracion_dias > 0),
                cantidad_personas INTEGER NOT NULL DEFAULT 1 CHECK(cantidad_personas > 0),
                fecha_inicio_venta DATE,
                fecha_fin_venta DATE,
                descripcion TEXT,
                estado BOOLEAN NOT NULL DEFAULT 1,
                categoria_id INTEGER,
                FOREIGN KEY(categoria_id) REFERENCES membership_categories(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miembro_id INTEGER NOT NULL,
                plan_id INTEGER NOT NULL,
                monto_pagado REAL NOT NULL CHECK(monto_pagado > 0),
                fecha_pago DATE NOT NULL,
                fecha_vencimiento DATE NOT NULL,
                FOREIGN KEY(miembro_id) REFERENCES members(id) ON DELETE CASCADE,
                FOREIGN KEY(plan_id) REFERENCES plans(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miembro_id INTEGER NOT NULL,
                fecha_hora_entrada TEXT NOT NULL,
                FOREIGN KEY(miembro_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miembro_id INTEGER NOT NULL,
                fecha_hora TEXT NOT NULL,
                nota TEXT NOT NULL,
                FOREIGN KEY(miembro_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_producto TEXT NOT NULL UNIQUE,
                stock INTEGER NOT NULL CHECK(stock >= 0),
                precio_venta REAL NOT NULL CHECK(precio_venta >= 0),
                stock_minimo INTEGER NOT NULL CHECK(stock_minimo >= 0)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_clase TEXT NOT NULL,
                horario TEXT,
                entrenador_id INTEGER,
                FOREIGN KEY(entrenador_id) REFERENCES trainers(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miembro_id INTEGER NOT NULL,
                clase_id INTEGER NOT NULL,
                fecha_inscripcion TEXT NOT NULL,
                FOREIGN KEY(miembro_id) REFERENCES members(id) ON DELETE CASCADE,
                FOREIGN KEY(clase_id) REFERENCES classes(id) ON DELETE CASCADE,
                UNIQUE(miembro_id, clase_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members_eliminados (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                dni TEXT,
                contacto TEXT,
                email TEXT,
                direccion TEXT,
                fecha_registro DATE,
                codigo_membresia TEXT,
                foto_path TEXT,
                eliminado_en TEXT NOT NULL
            )
        """)

        # ==================== TABLAS FASE 1 ====================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS membership_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                color_hex TEXT DEFAULT '#3b82f6',
                orden INTEGER DEFAULT 0,
                descripcion TEXT,
                activo BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS benefit_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                codigo TEXT NOT NULL,
                tipo_valor TEXT NOT NULL CHECK(tipo_valor IN ('boolean', 'numeric', 'percentage')),
                descripcion TEXT,
                icono TEXT,
                activo BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_benefits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria_id INTEGER NOT NULL,
                benefit_type_id INTEGER NOT NULL,
                valor_configurado TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(categoria_id) REFERENCES membership_categories(id) ON DELETE CASCADE,
                FOREIGN KEY(benefit_type_id) REFERENCES benefit_types(id) ON DELETE CASCADE,
                UNIQUE(categoria_id, benefit_type_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id INTEGER NOT NULL,
                miembro_id INTEGER NOT NULL,
                es_titular BOOLEAN DEFAULT 0,
                fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(payment_id) REFERENCES payments(id) ON DELETE CASCADE,
                FOREIGN KEY(miembro_id) REFERENCES members(id) ON DELETE CASCADE,
                UNIQUE(payment_id, miembro_id)
            )
        """)

        # ==================== TABLAS FASE 2: MARKET & CAJA ====================
        
        # 1. Tabla Proveedores (NUEVA)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa TEXT NOT NULL,
                ruc TEXT,
                contacto_nombre TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                categoria_producto TEXT,
                activo BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Tabla Categorías de Producto
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias_producto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                prefijo TEXT NOT NULL UNIQUE,
                activo BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Tabla Productos (Con columnas nuevas preparadas para nuevas instalaciones)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                codigo_barras TEXT UNIQUE,
                nombre TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                proveedor_id INTEGER,
                precio_compra REAL DEFAULT 0,
                precio_base REAL NOT NULL CHECK(precio_base >= 0),
                stock_actual INTEGER NOT NULL DEFAULT 0 CHECK(stock_actual >= 0),
                stock_minimo INTEGER NOT NULL DEFAULT 0,
                foto_path TEXT,
                activo BOOLEAN DEFAULT 1,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(categoria_id) REFERENCES categorias_producto(id),
                FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)
            )
        """)

        # MIGRACIÓN AUTOMÁTICA: Agregar columnas nuevas a productos si ya existe la tabla
        try:
            cursor.execute("ALTER TABLE productos ADD COLUMN proveedor_id INTEGER REFERENCES proveedores(id)")
            logger.info("Migración: Columna proveedor_id agregada a productos")
        except sqlite3.OperationalError:
            pass # Ya existe o error irrelevante

        try:
            cursor.execute("ALTER TABLE productos ADD COLUMN precio_compra REAL DEFAULT 0")
            logger.info("Migración: Columna precio_compra agregada a productos")
        except sqlite3.OperationalError:
            pass # Ya existe o error irrelevante
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario_movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                tipo_movimiento TEXT NOT NULL CHECK(tipo_movimiento IN ('entrada', 'salida', 'ajuste', 'venta')),
                cantidad INTEGER NOT NULL,
                stock_anterior INTEGER NOT NULL,
                stock_nuevo INTEGER NOT NULL,
                motivo TEXT,
                usuario_id INTEGER,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                referencia_tipo TEXT,
                referencia_id INTEGER,
                FOREIGN KEY(producto_id) REFERENCES productos(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                cliente_tipo TEXT NOT NULL CHECK(cliente_tipo IN ('miembro', 'visitante')),
                cliente_id INTEGER,
                total REAL NOT NULL CHECK(total >= 0),
                metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('efectivo', 'yape', 'plin', 'pos_banco')),
                usuario_id INTEGER,
                estado TEXT DEFAULT 'completada' CHECK(estado IN ('completada', 'cancelada'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas_detalle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL CHECK(cantidad > 0),
                precio_unitario REAL NOT NULL CHECK(precio_unitario >= 0),
                descuento_porcentaje REAL DEFAULT 0 CHECK(descuento_porcentaje >= 0 AND descuento_porcentaje <= 100),
                subtotal REAL NOT NULL CHECK(subtotal >= 0),
                FOREIGN KEY(venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                FOREIGN KEY(producto_id) REFERENCES productos(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caja_sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_apertura DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_cierre DATETIME,
                usuario_apertura_id INTEGER,
                usuario_cierre_id INTEGER,
                efectivo_inicial REAL DEFAULT 0,
                yape_inicial REAL DEFAULT 0,
                plin_inicial REAL DEFAULT 0,
                pos_banco_inicial REAL DEFAULT 0,
                efectivo_cierre REAL,
                yape_cierre REAL,
                plin_cierre REAL,
                pos_banco_cierre REAL,
                total_ingresos_sistema REAL,
                total_egresos_sistema REAL,
                diferencia_efectivo REAL,
                diferencia_yape REAL,
                diferencia_plin REAL,
                diferencia_pos_banco REAL,
                observaciones TEXT,
                estado TEXT DEFAULT 'abierta' CHECK(estado IN ('abierta', 'cerrada', 'con_diferencias'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cash_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_movimiento TEXT NOT NULL CHECK(tipo_movimiento IN ('ingreso', 'egreso')),
                categoria TEXT NOT NULL CHECK(categoria IN ('membresia', 'clase', 'market', 'gasto', 'ajuste', 'remesa')),
                metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('efectivo', 'yape', 'plin', 'pos_banco')),
                monto REAL NOT NULL CHECK(monto > 0),
                referencia_tipo TEXT,
                referencia_id INTEGER,
                descripcion TEXT,
                glosa TEXT,
                usuario_id INTEGER,
                caja_sesion_id INTEGER,
                estado TEXT DEFAULT 'activo' CHECK(estado IN ('activo', 'extornado')),
                FOREIGN KEY(caja_sesion_id) REFERENCES caja_sesiones(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_gasto TEXT NOT NULL CHECK(tipo_gasto IN ('servicio', 'compra', 'sueldo', 'alquiler', 'tributo', 'mantenimiento', 'otro')),
                monto REAL NOT NULL CHECK(monto > 0),
                metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('efectivo', 'yape', 'plin', 'pos_banco')),
                proveedor_id INTEGER,
                personal_id INTEGER,
                descripcion TEXT NOT NULL,
                glosa TEXT,
                usuario_id INTEGER,
                estado TEXT DEFAULT 'activo' CHECK(estado IN ('activo', 'anulado'))
            )
        """)

        # ==================== ÍNDICES ====================
        
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_members_dni ON members(dni)",
            "CREATE INDEX IF NOT EXISTS idx_members_codigo ON members(codigo_membresia)",
            "CREATE INDEX IF NOT EXISTS idx_payments_miembro ON payments(miembro_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_vencimiento ON payments(fecha_vencimiento)",
            "CREATE INDEX IF NOT EXISTS idx_payments_miembro_venc ON payments(miembro_id, fecha_vencimiento)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_miembro ON attendance(miembro_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_fecha ON attendance(fecha_hora_entrada)",
            "CREATE INDEX IF NOT EXISTS idx_measurements_miembro ON measurements(miembro_id)",
            "CREATE INDEX IF NOT EXISTS idx_notes_miembro ON notes(miembro_id)",
            "CREATE INDEX IF NOT EXISTS idx_category_benefits_categoria ON category_benefits(categoria_id)",
            "CREATE INDEX IF NOT EXISTS idx_category_benefits_benefit ON category_benefits(benefit_type_id)",
            "CREATE INDEX IF NOT EXISTS idx_payment_members_payment ON payment_members(payment_id)",
            "CREATE INDEX IF NOT EXISTS idx_payment_members_miembro ON payment_members(miembro_id)",
            "CREATE INDEX IF NOT EXISTS idx_plans_categoria ON plans(categoria_id)",
            # FASE 2 indices
            "CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id)",
            "CREATE INDEX IF NOT EXISTS idx_productos_sku ON productos(sku)",
            "CREATE INDEX IF NOT EXISTS idx_productos_barcode ON productos(codigo_barras)",
            "CREATE INDEX IF NOT EXISTS idx_inventario_producto ON inventario_movimientos(producto_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventario_fecha ON inventario_movimientos(fecha_hora)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_hora)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente_id)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_detalle_venta ON ventas_detalle(venta_id)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_detalle_producto ON ventas_detalle(producto_id)",
            "CREATE INDEX IF NOT EXISTS idx_caja_sesiones_estado ON caja_sesiones(estado)",
            "CREATE INDEX IF NOT EXISTS idx_cash_movements_sesion ON cash_movements(caja_sesion_id)",
            "CREATE INDEX IF NOT EXISTS idx_cash_movements_fecha ON cash_movements(fecha_hora)",
            "CREATE INDEX IF NOT EXISTS idx_cash_movements_categoria ON cash_movements(categoria)",
            "CREATE INDEX IF NOT EXISTS idx_cash_movements_metodo ON cash_movements(metodo_pago)",
            "CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos(fecha_hora)",
            "CREATE INDEX IF NOT EXISTS idx_gastos_tipo ON gastos(tipo_gasto)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)

        # ==================== DATOS INICIALES ====================
        
        # Planes por defecto
        for plan_data in Config.DEFAULT_PLANS:
            try:
                cursor.execute(
                    "INSERT INTO plans (nombre_plan, precio, duracion_dias, cantidad_personas) VALUES (?, ?, ?, ?)",
                    plan_data
                )
            except sqlite3.IntegrityError:
                pass

        # Categorías de membresía
        categorias = [
            ("Básico", "#22c55e", 1, "Categoría básica con acceso estándar"),
            ("Pro", "#3b82f6", 2, "Categoría intermedia con beneficios adicionales"),
            ("Premium", "#f59e0b", 3, "Categoría premium con todos los beneficios")
        ]
        
        for nombre, color, orden, desc in categorias:
            try:
                cursor.execute(
                    "INSERT INTO membership_categories (nombre, color_hex, orden, descripcion, activo) VALUES (?, ?, ?, ?, 1)",
                    (nombre, color, orden, desc)
                )
            except sqlite3.IntegrityError:
                pass

        # Tipos de beneficios (código AUTO-GENERADO)
        cursor.execute("SELECT MAX(CAST(SUBSTR(codigo, 4) AS INTEGER)) FROM benefit_types WHERE codigo LIKE 'BEN%'")
        max_code = cursor.fetchone()[0] or 0
        
        beneficios = [
            ("Sesión de Entrenamiento", "boolean", "Acceso a sesiones de entrenamiento con máquinas y pesas", "🏋️"),
            ("Clases Grupales", "percentage", "Descuento en clases grupales (yoga, spinning, zumba, etc)", "🧘"),
            ("Invitados Permitidos", "numeric", "Cantidad de invitados que puede traer el miembro al gimnasio", "👥"),
            ("Servicios Personalizados", "boolean", "Acceso a dietas personalizadas, rutinas y asesorías nutricionales", "⭐")
        ]
        
        for idx, (nombre, tipo, desc, icono) in enumerate(beneficios, start=1):
            codigo_auto = f"BEN{str(max_code + idx).zfill(3)}"
            try:
                cursor.execute(
                    "INSERT INTO benefit_types (nombre, codigo, tipo_valor, descripcion, icono, activo) VALUES (?, ?, ?, ?, ?, 1)",
                    (nombre, codigo_auto, tipo, desc, icono)
                )
            except sqlite3.IntegrityError:
                pass

        # Configuración de beneficios por categoría
        cursor.execute("SELECT id, nombre FROM membership_categories ORDER BY orden")
        categorias_db = cursor.fetchall()
        categorias_map = {nombre: id for id, nombre in categorias_db}
        
        cursor.execute("SELECT id, nombre FROM benefit_types")
        beneficios_db = cursor.fetchall()
        beneficios_map = {nombre: id for id, nombre in beneficios_db}
        
        configs = {
            "Básico": {
                "Sesión de Entrenamiento": {"enabled": True},
                "Clases Grupales": {"enabled": False, "descuento_porcentaje": 0},
                "Invitados Permitidos": {"enabled": False, "cantidad": 0},
                "Servicios Personalizados": {"enabled": False}
            },
            "Pro": {
                "Sesión de Entrenamiento": {"enabled": True},
                "Clases Grupales": {"enabled": True, "descuento_porcentaje": 50},
                "Invitados Permitidos": {"enabled": True, "cantidad": 2},
                "Servicios Personalizados": {"enabled": False}
            },
            "Premium": {
                "Sesión de Entrenamiento": {"enabled": True},
                "Clases Grupales": {"enabled": True, "descuento_porcentaje": 100},
                "Invitados Permitidos": {"enabled": True, "cantidad": 4},
                "Servicios Personalizados": {"enabled": True}
            }
        }
        
        for categoria_nombre, beneficios_config in configs.items():
            if categoria_nombre not in categorias_map:
                continue
            
            categoria_id = categorias_map[categoria_nombre]
            
            for beneficio_nombre, config in beneficios_config.items():
                if beneficio_nombre not in beneficios_map:
                    continue
                
                beneficio_id = beneficios_map[beneficio_nombre]
                valor_json = json.dumps(config)
                
                try:
                    cursor.execute(
                        "INSERT INTO category_benefits (categoria_id, benefit_type_id, valor_configurado) VALUES (?, ?, ?)",
                        (categoria_id, beneficio_id, valor_json)
                    )
                except sqlite3.IntegrityError:
                    pass

        # ==================== DATOS INICIALES FASE 2 ====================
        
        # Categorías de productos
        categorias_productos = [
            ("Nutrición", "NUT"),
            ("Ropa", "ROP"),
            ("Bebidas", "BEB"),
            ("Otros", "OTR")
        ]
        
        for nombre, prefijo in categorias_productos:
            try:
                cursor.execute(
                    "INSERT INTO categorias_producto (nombre, prefijo, activo) VALUES (?, ?, 1)",
                    (nombre, prefijo)
                )
            except sqlite3.IntegrityError:
                pass
        
        # Agregar beneficio de descuento Market a benefit_types si no existe
        try:
            cursor.execute(
                "SELECT MAX(CAST(SUBSTR(codigo, 4) AS INTEGER)) FROM benefit_types WHERE codigo LIKE 'BEN%'"
            )
            max_code = cursor.fetchone()[0] or 4  # Ya hay 4 beneficios base
            
            codigo_market = f"BEN{str(max_code + 1).zfill(3)}"
            
            cursor.execute(
                "INSERT INTO benefit_types (nombre, codigo, tipo_valor, descripcion, icono, activo) VALUES (?, ?, ?, ?, ?, 1)",
                ("Descuento Market", codigo_market, "percentage", "Descuento porcentual en compras del Market", "🛒")
            )
            
            benefit_market_id = cursor.lastrowid
            
            # Configurar descuentos por categoría
            cursor.execute("SELECT id, nombre FROM membership_categories")
            categorias_db = cursor.fetchall()
            
            descuentos_market = {
                "Básico": 0,    # Sin descuento
                "Pro": 10,      # 10% descuento
                "Premium": 20   # 20% descuento
            }
            
            for cat_id, cat_nombre in categorias_db:
                if cat_nombre in descuentos_market:
                    config_market = {
                        "enabled": True,
                        "descuento_porcentaje": descuentos_market[cat_nombre]
                    }
                    
                    try:
                        cursor.execute(
                            "INSERT INTO category_benefits (categoria_id, benefit_type_id, valor_configurado) VALUES (?, ?, ?)",
                            (cat_id, benefit_market_id, json.dumps(config_market))
                        )
                    except sqlite3.IntegrityError:
                        pass
        
        except sqlite3.IntegrityError:
            # El beneficio ya existe
            pass

        conn.commit()
        logger.info("✅ Base de datos inicializada: 23 tablas + 30 índices + datos iniciales FASE 1 + FASE 2")
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Error al crear tablas: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    create_initial_tables()
    print("✅ Base de datos creada correctamente")