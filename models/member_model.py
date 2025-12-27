# -*- coding: utf-8 -*-
"""
Modelo para gestión de miembros
"""
import sqlite3
from datetime import datetime
from core.base_model import BaseModel
from core.config import Config

class MemberModel(BaseModel):
    """Modelo para operaciones CRUD de miembros"""
    
    def insert_member(self, nombre, dni, contacto, email, direccion, codigo_membresia, foto_path=None):
        """
        Inserta un nuevo miembro en la base de datos.
        
        Args:
            nombre: Nombre completo del miembro
            dni: DNI del miembro
            contacto: Teléfono de contacto
            email: Correo electrónico
            direccion: Dirección
            codigo_membresia: Código único de membresía
            foto_path: Ruta a la foto del miembro (opcional)
            
        Returns:
            int: ID del miembro insertado
            
        Raises:
            ValueError: Si hay error de integridad (DNI o código duplicado)
        """
        try:
            fecha_registro = datetime.now().strftime(Config.DATE_FORMAT)
            
            data = {
                'nombre': nombre,
                'dni': dni,
                'contacto': contacto,
                'email': email,
                'direccion': direccion,
                'fecha_registro': fecha_registro,
                'codigo_membresia': codigo_membresia,
                'foto_path': foto_path
            }
            
            return self.insert('members', data)
            
        except ValueError as e:
            if "UNIQUE constraint failed: members.dni" in str(e):
                raise ValueError("El DNI ya está registrado")
            elif "UNIQUE constraint failed: members.codigo_membresia" in str(e):
                raise ValueError("El código de membresía ya existe")
            raise

    def get_all_members(self):
        """
        Obtiene todos los miembros ordenados por nombre.
        
        Returns:
            list: Lista de tuplas (id, nombre, dni, contacto, codigo_membresia)
        """
        query = """
            SELECT id, nombre, dni, contacto, codigo_membresia
            FROM members
            ORDER BY nombre ASC
        """
        return self.execute_query(query)

    def get_member_registration_date(self, miembro_id):
        """
        Obtiene la fecha de registro de un miembro.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            str: Fecha de registro en formato YYYY-MM-DD o None
        """
        query = """
            SELECT fecha_registro
            FROM members
            WHERE id = ?
        """
        resultado = self.execute_query(query, (miembro_id,), fetch_one=True)
        return resultado[0] if resultado else None

    def find_member_by_identifier(self, identifier):
        """
        Busca un miembro por DNI o código de membresía (case-insensitive).
        
        Args:
            identifier: DNI o código de membresía
            
        Returns:
            tuple: (id, nombre, dni, contacto, email, direccion, codigo_membresia, foto_path)
                   o None si no se encuentra
        """
        identifier = identifier.strip()
        
        query = """
            SELECT id, nombre, dni, contacto, email, direccion, codigo_membresia, foto_path
            FROM members
            WHERE dni = ? OR UPPER(codigo_membresia) = UPPER(?)
            LIMIT 1
        """
        return self.execute_query(query, (identifier, identifier), fetch_one=True)

    def codigo_exists(self, codigo):
        """
        Verifica si un código de membresía ya existe.
        
        Args:
            codigo: Código a verificar
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        query = "SELECT 1 FROM members WHERE codigo_membresia = ? LIMIT 1"
        resultado = self.execute_query(query, (codigo,), fetch_one=True)
        return resultado is not None

    def update_foto_path(self, codigo_membresia, foto_path):
        """
        Actualiza la ruta de la foto de un miembro.
        
        Args:
            codigo_membresia: Código del miembro
            foto_path: Nueva ruta de la foto (None para eliminar)
        """
        return self.update(
            'members',
            {'foto_path': foto_path},
            {'codigo_membresia': codigo_membresia}
        )

    def update_member(self, codigo_membresia, nombre, dni, contacto, email, direccion):
        """
        Actualiza los datos de un miembro.
        
        Args:
            codigo_membresia: Código del miembro
            nombre: Nuevo nombre
            dni: Nuevo DNI
            contacto: Nuevo contacto
            email: Nuevo email
            direccion: Nueva dirección
            
        Returns:
            bool: True si se actualizó correctamente
        """
        data = {
            'nombre': nombre,
            'dni': dni,
            'contacto': contacto,
            'email': email,
            'direccion': direccion
        }
        
        return self.update('members', data, {'codigo_membresia': codigo_membresia})

    def delete_member(self, codigo_membresia):
        """
        Elimina un miembro (soft delete - copia a tabla de respaldo).
        
        Args:
            codigo_membresia: Código del miembro a eliminar
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Copiar datos antes de eliminar
            cursor.execute(
                "SELECT * FROM members WHERE codigo_membresia = ?",
                (codigo_membresia,)
            )
            miembro = cursor.fetchone()
            
            if miembro:
                eliminado_en = datetime.now().strftime(Config.DATETIME_FORMAT)
                
                cursor.execute("""
                    INSERT OR IGNORE INTO members_eliminados
                    (id, nombre, dni, contacto, email, direccion, fecha_registro, 
                     codigo_membresia, foto_path, eliminado_en)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (*miembro, eliminado_en))

                # Eliminar de tabla principal (CASCADE eliminará relaciones)
                cursor.execute(
                    "DELETE FROM members WHERE codigo_membresia = ?",
                    (codigo_membresia,)
                )
                conn.commit()
                self.logger.info(f"Miembro {codigo_membresia} eliminado correctamente")
