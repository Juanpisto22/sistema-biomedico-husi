"""
Constantes y utilidades de configuración para el módulo de rondas.

Este módulo contiene todas las constantes globales, estructuras de datos
de configuración y funciones auxiliares utilizadas en el sistema de rondas.
"""
import base64
import io
import uuid
from django.core.files.base import ContentFile
from PIL import Image


# ============================================================================
# SERVICIOS HOSPITALARIOS - CATEGORÍAS
# ============================================================================

PRIORITARIOS = [
    "UNIDAD DE RECIÉN NACIDOS (CUIDADOS INTERMEDIOS)",
    "UNIDAD DE RECIÉN NACIDOS (CUIDADOS INTENSIVOS)",
    "UNIDAD DE CUIDADOS INTENSIVOS",
    "UNIDAD DE CUIDADO INTENSIVO PEDIÁTRICO",
]

SEDES_EXTERNAS = [
    "Cuidados Paliativos",
    "Intelectus",
]


# ============================================================================
# SERVICIOS POR DÍA DE LA SEMANA (0=Lunes, 6=Domingo)
# ============================================================================

RONDA_DIARIA = {
    0: ["Urgencias", "Salud Mental", "Trasplante de Médula"],
    1: ["Oftalmología", "Neurociencias", "Patología", "Radiología", "Hospitalización Aislamiento", "Sexto Centro", "Medicina Nuclear"],
    2: ["Urgencias", "Oncología", "Hemato-Oncología", "Gastroenterología"],
    3: ["Neumología", "Nefrología", "Cardiología", "Medicina Interna", "Neurología", "Otorrino"],
    4: ["Urgencias", "Consulta Externa", "Pediatría", "9 Piso"],
}

SERVICIO_SALAS = {
    0: ["Hospitalización Cirugía", "Lactario", "Central de Esterilización", "SIPE"],
    2: ["Central de Esterilización", "Neurociencias", "SIPE"],
    4: ["Central de Esterilización", "SIPE"],
}

LABORATORIO_CLINICO = {
    0: [  # Lunes - todos los servicios
        "LC - ALMACÉN", "LC - MICROBIOLOGÍA", "LC - BIOLOGÍA MOLECULAR", "LC - CITOMETRÍA DE FLUJO",
        "LC - INMUNOLOGÍA", "LC - HEMATOLOGÍA", "LC - QUÍMICA", "LC - TAMIZAJE",
        "LC - REFERENCIA Y CONTRAREFERENCIA", "LC - SERVICIO TRANSFUSIONAL", "LC - TOMA DE MUESTRAS", "LC - ERRORES INNATOS"
    ],
    1: [  # Martes - solo errores innatos
        "LC - ERRORES INNATOS"
    ]
}


# ============================================================================
# SALAS DE CIRUGÍA - CONFIGURACIÓN
# ============================================================================

SURGERY_ROOMS = [str(numero) for numero in range(1, 15)]  # Salas 1-14

SURGERY_EQUIPMENT = [
    "Máquina",
    "Presión bala de oxígeno (O₂)",
    "Monitor",
    "Mesa",
    "Lámpara",
    "Electrobisturí",
    "Microscopio",
    "Otros",
]

SURGERY_DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

# Días en que aparecen las salas de cirugía (0=Lunes, 5=Sábado)
SURGERY_AVAILABLE_DAYS = [0, 1, 2, 3, 4, 5]  # Lunes a Sábado


# ============================================================================
# DÍAS DE LA SEMANA EN ESPAÑOL
# ============================================================================

SPANISH_WEEKDAYS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]


# ============================================================================
# ESTRUCTURA DE CATEGORÍAS PARA PLANTILLAS
# ============================================================================

ROUND_STRUCTURE = {
    "prioritarios": {
        "titulo": "Servicios Prioritarios",
        "descripcion": "Servicios prioritarios siempre disponibles"
    },
    "ronda_diaria": {
        "titulo": "Ronda Diaria",
        "descripcion": "Servicios de ronda diaria según día de la semana"
    },
    "servicio_salas": {
        "titulo": "Servicio de Salas", 
        "descripcion": "Servicios dependientes del día"
    },
    "laboratorio_clinico": {
        "titulo": "Laboratorio Clínico",
        "descripcion": "Solo disponible los lunes"
    },
    "sedes_externas": {
        "titulo": "Sedes Externas",
        "descripcion": "Siempre disponibles"
    },
}


# ============================================================================
# FUNCIONES AUXILIARES PARA PROCESAMIENTO DE DATOS
# ============================================================================


def base64_to_image_file(base64_string, filename_prefix="firma"):
    """
    Convierte una imagen base64 a un archivo Django que puede ser guardado en ImageField
    """
    if not base64_string or not base64_string.startswith('data:image'):
        return None
    
    try:
        # Extraer el formato y los datos
        format_info, base64_data = base64_string.split(';base64,')
        image_format = format_info.split('/')[-1].lower()
        
        # Decodificar base64
        image_data = base64.b64decode(base64_data)
        
        # Crear archivo en memoria
        image_io = io.BytesIO(image_data)
        
        # Abrir con PIL para procesar
        image = Image.open(image_io)
        
        # Convertir a RGB si es necesario (para PNG con transparencia)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Redimensionar si es muy grande (máximo 800x600)
        max_size = (800, 600)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Guardar en BytesIO como JPEG para reducir tamaño
        output_io = io.BytesIO()
        image.save(output_io, format='JPEG', quality=85, optimize=True)
        output_io.seek(0)
        
        # Crear archivo Django
        filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.jpg"
        django_file = ContentFile(output_io.getvalue(), name=filename)
        
        return django_file
        
    except Exception as e:
        print(f"Error procesando imagen base64: {e}")
        return None


def process_signature_data(form_data):
    """
    Procesa los datos de firma del formulario y convierte base64 a archivos
    """
    processed_data = form_data.copy()
    
    # Procesar firma del servicio
    if 'firma_servicio' in processed_data and processed_data['firma_servicio']:
        firma_servicio_file = base64_to_image_file(
            processed_data['firma_servicio'], 
            "firma_servicio"
        )
        if firma_servicio_file:
            processed_data['firma_servicio'] = firma_servicio_file
    
    # Procesar firma de la ronda
    if 'firma_ronda' in processed_data and processed_data['firma_ronda']:
        firma_ronda_file = base64_to_image_file(
            processed_data['firma_ronda'], 
            "firma_ronda"
        )
        if firma_ronda_file:
            processed_data['firma_ronda'] = firma_ronda_file
    
    return processed_data


def get_services_for_day(day_number):
    """
    Obtiene todos los servicios disponibles para un día específico.
    
    Args:
        day_number (int): Número del día (0=Lunes, 6=Domingo)
        
    Returns:
        dict: Diccionario con todos los servicios organizados por categoría
        
    Example:
        >>> servicios = get_services_for_day(0)  # Lunes
        >>> print(servicios["ronda_diaria"])
        ["Urgencias", "Salud Mental", "Trasplante de Médula"]
    """
    servicios = {
        "ronda_diaria": RONDA_DIARIA.get(day_number, []),
        "servicio_salas": SERVICIO_SALAS.get(day_number, []),
        "laboratorio_clinico": LABORATORIO_CLINICO.get(day_number, []),
        "surgery_available": day_number in SURGERY_AVAILABLE_DAYS,
    }
    
    # Agregar todos los servicios disponibles (para mostrar opciones en el frontend)
    todos_ronda_diaria = set()
    todos_servicio_salas = set()
    
    for servicios_dia in RONDA_DIARIA.values():
        todos_ronda_diaria.update(servicios_dia)
    for servicios_dia in SERVICIO_SALAS.values():
        todos_servicio_salas.update(servicios_dia)
    
    servicios["todos_ronda_diaria"] = sorted(list(todos_ronda_diaria))
    servicios["todos_servicio_salas"] = sorted(list(todos_servicio_salas))
    servicios["todos_laboratorio_clinico"] = LABORATORIO_CLINICO[0]  # Todos los servicios de laboratorio
    
    return servicios