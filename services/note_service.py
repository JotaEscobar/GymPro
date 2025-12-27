# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para notas
"""
from models.note_model import NoteModel
from core.logger import logger

class NoteService:
    """Servicio para gestión de notas de miembros"""
    
    def __init__(self):
        self.model = NoteModel()
    
    def add_note(self, miembro_id, texto):
        """
        Agrega una nueva nota a un miembro.
        
        Args:
            miembro_id: ID del miembro
            texto: Contenido de la nota
            
        Returns:
            dict: {"success": bool, "message": str, "note_id": int}
        """
        if not texto or not texto.strip():
            return {
                "success": False,
                "message": "La nota no puede estar vacía"
            }
        
        try:
            note_id = self.model.insert_note(miembro_id, texto.strip())
            logger.info(f"Nota agregada: ID={note_id}, Miembro={miembro_id}")
            
            return {
                "success": True,
                "message": "Nota agregada correctamente",
                "note_id": note_id
            }
        except Exception as e:
            logger.error(f"Error al agregar nota: {e}")
            return {
                "success": False,
                "message": f"Error al agregar nota: {str(e)}"
            }
    
    def get_notes(self, miembro_id):
        """
        Obtiene todas las notas de un miembro.
        
        Args:
            miembro_id: ID del miembro
            
        Returns:
            list: Lista de tuplas (id, fecha_hora, nota)
        """
        return self.model.get_member_notes(miembro_id)
    
    def delete_note(self, note_id):
        """
        Elimina una nota por ID.
        
        Args:
            note_id: ID de la nota
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            deleted = self.model.delete_note(note_id)
            
            if deleted:
                logger.info(f"Nota eliminada: ID={note_id}")
                return {
                    "success": True,
                    "message": "Nota eliminada correctamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontró la nota"
                }
        except Exception as e:
            logger.error(f"Error al eliminar nota: {e}")
            return {
                "success": False,
                "message": f"Error al eliminar nota: {str(e)}"
            }
