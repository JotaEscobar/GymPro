# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para miembros
"""
import random
import string
from datetime import datetime
from models.member_model import MemberModel
from models.payment_model import PaymentModel  # 🔥 IMPORTAR PAYMENTMODEL
from core.config import Config
from core.logger import logger

class MemberService:
    """Servicio para gestión de miembros"""
    
    def __init__(self):
        self.model = MemberModel()
        self.payment_model = PaymentModel()  # 🔥 INSTANCIA PARA get_latest_expiry_date

    def _formatear_nombre(self, nombre):
        """
        Convierte el nombre a formato capitalizado por palabra.
        
        Args:
            nombre: Nombre a formatear
            
        Returns:
            str: Nombre formateado
        """
        return ' '.join(p.capitalize() for p in nombre.strip().split())

    def _generar_codigo(self, nombre, dni):
        """
        Genera un código único de membresía.
        Formato: [LetraInicial][UltimosDNI][Random2Chars]
        
        Args:
            nombre: Nombre del miembro
            dni: DNI del miembro
            
        Returns:
            str: Código único generado
            
        Raises:
            ValueError: Si no se puede generar código único después de 100 intentos
        """
        letra = nombre.strip()[0].upper() if nombre else "X"
        sufijo_dni = dni[-2:] if len(dni) >= 2 else dni.zfill(2)

        for intento in range(100):
            aleatorio = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=2)
            )
            codigo = f"{letra}{sufijo_dni}{aleatorio}"
            
            if not self.model.codigo_exists(codigo):
                logger.info(f"Código generado: {codigo} (intento {intento + 1})")
                return codigo

        raise ValueError(
            "No se pudo generar un código único después de 100 intentos. "
            "Intenta con otro nombre o DNI."
        )

    def register_member(self, nombre, dni, contacto, email, direccion, foto_path=None):
        """
        Registra un nuevo miembro en el sistema.
        
        Args:
            nombre: Nombre completo
            dni: DNI
            contacto: Teléfono de contacto
            email: Correo electrónico
            direccion: Dirección
            foto_path: Ruta de foto (opcional)
            
        Returns:
            dict: {"success": bool, "message": str, "codigo": str}
        """
        if not nombre or not dni:
            return {
                "success": False,
                "message": "Nombre y DNI son obligatorios"
            }

        try:
            nombre = self._formatear_nombre(nombre)
            codigo = self._generar_codigo(nombre, dni)
            
            miembro_id = self.model.insert_member(
                nombre, dni, contacto, email, direccion, codigo, foto_path
            )
            
            logger.info(
                f"Miembro registrado: ID={miembro_id}, Código={codigo}, Nombre={nombre}"
            )
            
            return {
                "success": True,
                "message": f"Miembro registrado con éxito. Código: {codigo}",
                "codigo": codigo,
                "miembro_id": miembro_id
            }
            
        except ValueError as ve:
            msg = str(ve)
            if "DNI ya está registrado" in msg:
                return {
                    "success": False,
                    "message": "El DNI ya se encuentra registrado"
                }
            return {
                "success": False,
                "message": msg
            }

    def get_all_members_with_status(self):
        """
        Obtiene todos los miembros con el estado de su membresía.
        🔥 USA PaymentModel.get_latest_expiry_date() - ÚNICA FUENTE
        
        Returns:
            list: Lista de tuplas (id, nombre, dni, contacto, codigo, estado)
        """
        miembros = self.model.get_all_members()
        resultado = []

        for miembro in miembros:
            miembro_id, nombre, dni, contacto, codigo = miembro
            
            # 🔥 USAR PAYMENTMODEL PARA CONSISTENCIA
            fecha_vencimiento = self.payment_model.get_latest_expiry_date(miembro_id)

            if fecha_vencimiento:
                try:
                    vencimiento = datetime.strptime(
                        fecha_vencimiento, 
                        Config.DATE_FORMAT
                    ).date()
                    hoy = datetime.now().date()
                    dias = (vencimiento - hoy).days
                    
                    if dias < 0:
                        estado = f"Vencida ({fecha_vencimiento})"
                    else:
                        estado = f"Válida hasta {fecha_vencimiento}"
                except:
                    estado = "Fecha inválida"
            else:
                estado = "Sin plan"

            resultado.append((miembro_id, nombre, dni, contacto, codigo, estado))

        return resultado

    def find_member_by_identifier(self, identifier):
        """
        Busca un miembro por DNI o código y retorna info con estado de membresía.
        🔥 USA PaymentModel.get_latest_expiry_date() - ÚNICA FUENTE
        
        Args:
            identifier: DNI o código de membresía
            
        Returns:
            tuple: (id, nombre, dni, contacto, email, direccion, codigo, estado, foto_path)
                   o None si no se encuentra
        """
        miembro = self.model.find_member_by_identifier(identifier)
        
        if not miembro:
            return None

        miembro_id, nombre, dni, contacto, email, direccion, codigo, foto_path = miembro
        
        # 🔥 USAR PAYMENTMODEL PARA CONSISTENCIA
        fecha_vencimiento = self.payment_model.get_latest_expiry_date(miembro_id)

        if fecha_vencimiento:
            try:
                vencimiento = datetime.strptime(
                    fecha_vencimiento, 
                    Config.DATE_FORMAT
                ).date()
                hoy = datetime.now().date()
                dias = (vencimiento - hoy).days
                estado = Config.STATUS_ACTIVE if dias >= 0 else Config.STATUS_EXPIRED
            except:
                estado = Config.STATUS_UNKNOWN
        else:
            estado = Config.STATUS_EXPIRED

        return (
            miembro_id,
            nombre,
            dni,
            contacto,
            email,
            direccion,
            codigo,
            estado,
            foto_path
        )
    
    def update_member_photo(self, codigo_membresia, foto_path):
        """Actualiza la foto de un miembro"""
        self.model.update_foto_path(codigo_membresia, foto_path)
        logger.info(f"Foto actualizada para miembro {codigo_membresia}")

    def update_member_profile(self, codigo, nombre, dni, contacto, email, direccion):
        """Actualiza el perfil de un miembro"""
        nombre = self._formatear_nombre(nombre)
        self.model.update_member(codigo, nombre, dni, contacto, email, direccion)
        logger.info(f"Perfil actualizado para miembro {codigo}")

    def delete_member(self, codigo):
        """Elimina un miembro (soft delete)"""
        self.model.delete_member(codigo)
        logger.info(f"Miembro {codigo} eliminado")
