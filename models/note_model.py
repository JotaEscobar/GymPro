# -*- coding: utf-8 -*-
"""
Modelo para gestión de notas
"""
from datetime import datetime
from core.base_model import BaseModel
from core.config import Config

class NoteModel(BaseModel):
    """Modelo para operaciones CRUD de notas"""
    
    def insert_note(self, miembro_id, nota):
        """
        Inserta una nueva nota.
        
        Args:
            miembro_id: ID del miembro
            nota: Texto de la nota
            
        Returns:
            int: ID de la nota insertada
        """
        data = {
            'miembro_id': miembro_id,
            'fecha_hora': datetime.now().strftime(Config.DATETIME_FORMAT),
            'nota': nota
        }
        return self.insert('notes', data)
    
    def get_member_notes(self, miembro_id):
        """
        Obtiene todas las notas de un miembro ordenadas por fecha DESC.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            list: Lista de tuplas (id, fecha_hora, nota)
        """
        query = """
            SELECT id, fecha_hora, nota
            FROM notes
            WHERE miembro_id = ?
            ORDER BY fecha_hora DESC
        """
        return self.execute_query(query, (miembro_id,))
    
    def delete_note(self, note_id):
        """
        Elimina una nota por ID.
        
        Args:
            note_id: ID de la nota
            
        Returns:
            bool: True si se eliminó, False si no existe
        """
        return self.delete('notes', {'id': note_id})
