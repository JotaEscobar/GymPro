# -*- coding: utf-8 -*-
import sqlite3
from typing import Any, List, Optional, Tuple
from contextlib import contextmanager
from core.database_manager import get_connection
from core.logger import logger

class BaseModel:
    # Whitelist de tablas permitidas
    ALLOWED_TABLES = {
        'members', 'measurements', 'plans', 'payments', 'attendance',
        'notes', 'inventory', 'trainers', 'classes', 'registrations',
        'members_eliminados', 'membership_categories', 'benefit_types',
        'category_benefits', 'payment_members',
        'categorias_producto', 'productos', 'inventario_movimientos',
        'ventas', 'ventas_detalle', 'caja_sesiones', 
        'cash_movements', 'gastos', 'proveedores'
    }
    
    def __init__(self):
        self.logger = logger
    
    @contextmanager
    def get_db_connection(self):
        conn = get_connection()
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error en transacción BD: {e}")
            raise
        finally:
            conn.close()
    
    def _validate_table(self, table: str) -> None:
        if table not in self.ALLOWED_TABLES:
            raise ValueError(f"Tabla no permitida: {table}")
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True,
        commit: bool = False,
        connection: sqlite3.Connection = None
    ) -> Any:
        # Modo Transacción Externa
        if connection:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return cursor.lastrowid if cursor.lastrowid else True

        # Modo Autoconsumo
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if commit:
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else True
            
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            
            return cursor
    
    def insert(self, table: str, data: dict, connection: sqlite3.Connection = None) -> int:
        self._validate_table(table)
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            return self.execute_query(
                query, 
                tuple(data.values()),
                commit=(connection is None),
                connection=connection
            )
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Error de integridad al insertar en {table}: {e}")
            raise ValueError(f"Error de integridad: {e}")
    
    def update(self, table: str, data: dict, where: dict, connection: sqlite3.Connection = None) -> bool:
        self._validate_table(table)
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        params = tuple(data.values()) + tuple(where.values())
        
        if connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete(self, table: str, where: dict, connection: sqlite3.Connection = None) -> bool:
        self._validate_table(table)
        
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        if connection:
            cursor = connection.cursor()
            cursor.execute(query, tuple(where.values()))
            return cursor.rowcount > 0

        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(where.values()))
            conn.commit()
            return cursor.rowcount > 0

    def bulk_insert(self, table: str, records: List[dict], connection: sqlite3.Connection = None) -> List[int]:
        if not records:
            raise ValueError("La lista de registros no puede estar vacía")
        
        self._validate_table(table)
        
        columns = list(records[0].keys())
        placeholders = ', '.join(['?'] * len(columns))
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        inserted_ids = []
        
        # Lógica unificada para transacción externa o interna
        if connection:
            cursor = connection.cursor()
            for record in records:
                values = tuple(record[col] for col in columns)
                cursor.execute(query, values)
                inserted_ids.append(cursor.lastrowid)
        else:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                for record in records:
                    values = tuple(record[col] for col in columns)
                    cursor.execute(query, values)
                    inserted_ids.append(cursor.lastrowid)
                conn.commit()
        
        self.logger.info(f"Bulk insert: {len(inserted_ids)} registros en {table}")
        return inserted_ids