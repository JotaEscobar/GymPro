# -*- coding: utf-8 -*-
"""
Mensajes centralizados de la aplicación
Facilita mantenimiento y futura internacionalización (i18n)
"""

class Messages:
    """Mensajes de la aplicación (preparado para i18n)"""
    
    # ========== TÍTULOS ==========
    TITLE_SUCCESS = "Éxito"
    TITLE_ERROR = "Error"
    TITLE_WARNING = "Advertencia"
    TITLE_CONFIRM = "Confirmar"
    TITLE_INFO = "Información"
    
    # ========== MIEMBROS ==========
    MEMBER_REGISTERED = "Miembro registrado correctamente"
    MEMBER_UPDATED = "Datos del miembro actualizados"
    MEMBER_DELETED = "Miembro eliminado correctamente"
    MEMBER_NOT_FOUND = "Miembro no encontrado"
    MEMBER_SELECT_REQUIRED = "Por favor, seleccione un miembro"
    MEMBER_DNI_EXISTS = "El DNI ya se encuentra registrado"
    MEMBER_CODE_EXISTS = "El código de membresía ya existe"
    MEMBER_CONFIRM_DELETE = "¿Está seguro de eliminar este miembro?\nEsta acción no se puede deshacer."
    
    # ========== PAGOS ==========
    PAYMENT_SUCCESS = "Pago registrado correctamente"
    PAYMENT_ERROR = "Error al registrar pago"
    PAYMENT_SELECT_PLAN = "Debe seleccionar un plan válido"
    PAYMENT_INVALID_AMOUNT = "El monto debe ser un número positivo"
    PAYMENT_DELETED = "Pago eliminado (extornado) correctamente"
    PAYMENT_NOT_FOUND = "No se encontró el pago"
    PAYMENT_CONFIRM_DELETE = "¿Está seguro de eliminar (extornar) este pago?"
    
    # ========== PLANES ==========
    PLAN_CREATED = "Plan creado correctamente"
    PLAN_UPDATED = "Plan actualizado correctamente"
    PLAN_DELETED = "Plan eliminado correctamente"
    PLAN_NOT_FOUND = "No se encontró el plan"
    PLAN_HAS_PAYMENTS = "No se puede eliminar: El plan tiene {count} pagos asociados. Cámbielo a inactivo en su lugar."
    PLAN_NAME_EXISTS = "Ya existe un plan con ese nombre"
    PLAN_SELECT_REQUIRED = "Por favor, seleccione un plan"
    PLAN_CONFIRM_DELETE = "¿Está seguro de eliminar el plan '{name}'?"
    
    # ========== ASISTENCIAS ==========
    ATTENDANCE_SUCCESS = "Acceso concedido. Bienvenido(a) {name}"
    ATTENDANCE_DENIED_EXPIRED = "Acceso denegado. Membresía vencida el {date}"
    ATTENDANCE_DENIED_NO_PLAN = "Acceso denegado. No tiene un plan activo"
    ATTENDANCE_ALREADY_MARKED = "Ya registró asistencia hoy"
    ATTENDANCE_DELETED = "Entrada eliminada correctamente"
    ATTENDANCE_NOT_FOUND = "No se encontró entrada para eliminar"
    ATTENDANCE_SELECT_REQUIRED = "Seleccione una fila para eliminar la entrada"
    ATTENDANCE_CONFIRM_DELETE = "¿Eliminar la última entrada registrada para el miembro con código {code}?"
    ATTENDANCE_MEMBER_NOT_FOUND = "Miembro no encontrado por DNI o Código"
    ATTENDANCE_INPUT_REQUIRED = "Por favor, ingrese un DNI o Código"
    
    # ========== NOTAS ==========
    NOTE_EMPTY = "La nota no puede estar vacía"
    NOTE_ADDED = "Nota agregada correctamente"
    NOTE_DELETED = "Nota eliminada correctamente"
    NOTE_NOT_FOUND = "No se encontró la nota"
    NOTE_SELECT_REQUIRED = "Por favor, seleccione una nota para eliminar"
    NOTE_CONFIRM_DELETE = "¿Está seguro de eliminar la nota:\n\n'{text}'?"
    
    # ========== VALIDACIONES ==========
    VALIDATION_EMPTY_FIELD = "El campo {field} no puede estar vacío"
    VALIDATION_INVALID_DNI = "DNI inválido. Debe tener 8 dígitos"
    VALIDATION_INVALID_EMAIL = "Formato de email inválido"
    VALIDATION_INVALID_PHONE = "Formato de teléfono inválido"
    VALIDATION_INVALID_PRICE = "El precio debe ser un número positivo"
    VALIDATION_INVALID_NUMBER = "Debe ingresar un número válido"
    
    # ========== ERRORES GENERALES ==========
    ERROR_UNEXPECTED = "Ocurrió un error inesperado:\n{error}"
    ERROR_DATABASE = "Error de base de datos:\n{error}"
    ERROR_CRITICAL = "Error crítico"
    ERROR_NO_SELECTION = "No hay ningún elemento seleccionado"
    
    # ========== MENSAJES DE ESTADO ==========
    STATUS_ACTIVE = "Activo"
    STATUS_EXPIRED = "Vencido"
    STATUS_NO_PLAN = "Sin Plan"
    STATUS_VALID_UNTIL = "Válida hasta {date}"
    STATUS_EXPIRED_ON = "Vencida ({date})"
    STATUS_ALERT_EXPIRING = "¡Alerta! Tu membresía vence en {days} días"
    STATUS_ALERT_EXPIRED_DAYS = "Membresía vencida hace {days} días"
    
    # ========== ACCIONES ==========
    ACTION_SAVE = "Guardar"
    ACTION_CANCEL = "Cancelar"
    ACTION_DELETE = "Eliminar"
    ACTION_EDIT = "Editar"
    ACTION_CREATE = "Crear"
    ACTION_SEARCH = "Buscar"
    ACTION_REFRESH = "Actualizar"
    
    @classmethod
    def format(cls, template: str, **kwargs) -> str:
        """
        Helper para mensajes con variables.
        
        Args:
            template: String con placeholders {variable}
            **kwargs: Valores para reemplazar
            
        Returns:
            str: Mensaje formateado
            
        Example:
            Messages.format(Messages.PLAN_HAS_PAYMENTS, count=5)
            # "No se puede eliminar: El plan tiene 5 pagos asociados..."
        """
        return template.format(**kwargs)
