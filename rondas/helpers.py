"""
Funciones auxiliares y utilidades para el módulo de rondas.

Este módulo contiene funciones helper que son utilizadas
en diferentes partes del sistema de rondas.
"""
from datetime import datetime


def is_oncology_service(servicio):
    """
    Verifica si un servicio pertenece a oncología.
    
    Los servicios de oncología requieren hasta 3 firmas del personal
    del servicio, mientras que los servicios normales solo requieren 1.
    
    Args:
        servicio (str): Nombre del servicio a verificar
        
    Returns:
        bool: True si es un servicio de oncología, False en caso contrario
        
    Example:
        >>> is_oncology_service("Oncología")
        True
        >>> is_oncology_service("Urgencias")
        False
    """
    return servicio.lower() in ["oncología", "hemato-oncología", "oncologia", "hemato-oncologia"]


def horario_valido_panel(moment) -> bool:
    """
    Valida si el horario es válido para registrar rondas.
    
    El sistema permite registrar rondas únicamente durante el horario
    diurno establecido (5:00 AM a 6:00 PM).
    
    Args:
        moment (datetime): Momento a validar
        
    Returns:
        bool: True si está dentro del horario permitido, False en caso contrario
        
    Example:
        >>> from datetime import datetime
        >>> horario_valido_panel(datetime(2025, 1, 1, 8, 0))  # 8 AM
        True
        >>> horario_valido_panel(datetime(2025, 1, 1, 20, 0))  # 8 PM
        False
    """
    hora = moment.hour
    return 5 <= hora < 18


def horario_visible_historial(fecha_creacion) -> bool:
    """
    Valida si una ronda debe mostrarse en el historial.
    
    El historial filtra y muestra únicamente las rondas registradas
    durante el horario establecido (5:00 AM a 6:00 PM).
    
    Args:
        fecha_creacion (datetime): Fecha de creación del registro
        
    Returns:
        bool: True si debe mostrarse en el historial, False en caso contrario
    """
    hora = fecha_creacion.hour
    return 5 <= hora < 18


def surgery_available_today(day_number):
    """
    Determina si el servicio de cirugía está disponible en un día específico.
    
    Args:
        day_number (int): Número del día de la semana (0=Lunes, 6=Domingo)
        
    Returns:
        bool: True si cirugía está disponible ese día, False en caso contrario
        
    Example:
        >>> surgery_available_today(0)  # Lunes
        True
        >>> surgery_available_today(6)  # Domingo
        False
    """
    from .utils import SURGERY_AVAILABLE_DAYS
    return day_number in SURGERY_AVAILABLE_DAYS


def get_services_by_day(day_number):
    """
    Obtiene los servicios disponibles según el día de la semana.
    
    Esta función determina qué servicios están activos en un día específico,
    considerando los horarios de operación de cada área del hospital.
    
    Args:
        day_number (int): Número del día de la semana (0=Lunes, 6=Domingo)
        
    Returns:
        dict: Diccionario con los servicios organizados por categoría
        
    Example:
        >>> servicios = get_services_by_day(0)  # Lunes
        >>> print(servicios["ronda_diaria"])
        ["Urgencias", "Salud Mental", "Trasplante de Médula"]
    """
    from .utils import get_services_for_day
    return get_services_for_day(day_number)
