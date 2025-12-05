"""
Módulo para manejo de días festivos en Colombia
"""
from datetime import datetime, date, timedelta
from typing import List, Tuple


class FestivosColombiaCalculator:
    """
    Calculadora de días festivos en Colombia según la ley colombiana.
    
    Implementa las reglas de la Ley 51 de 1983 que establece:
    1. Festivos FIJOS: Se celebran el día exacto sin importar qué día caiga
    2. Festivos TRASLADABLES: Si no caen en lunes, se trasladan al lunes siguiente
    3. Festivos MOVIBLES: Dependen de la fecha de Pascua (cálculo de Gauss)
    
    Uso en el sistema de rondas:
    - Si hoy es festivo, las rondas se trasladan al siguiente día hábil
    - Permite planificar correctamente los servicios hospitalarios
    """
    
    # Festivos FIJOS: Se celebran siempre en la fecha exacta
    FESTIVOS_FIJOS = [
        (1, 1),   # Año Nuevo - 1 de enero
        (5, 1),   # Día del Trabajo - 1 de mayo
        (7, 20),  # Día de la Independencia - 20 de julio
        (8, 7),   # Batalla de Boyacá - 7 de agosto
        (12, 8),  # Inmaculada Concepción - 8 de diciembre
        (12, 25), # Navidad - 25 de diciembre
    ]
    
    # Festivos TRASLADABLES: Se mueven al lunes siguiente si no caen en lunes
    FESTIVOS_TRASLADABLES = [
        (1, 6),   # Reyes Magos - 6 de enero
        (3, 19),  # San José - 19 de marzo
        (6, 29),  # San Pedro y San Pablo - 29 de junio
        (8, 15),  # Asunción de la Virgen - 15 de agosto
        (10, 12), # Día de la Raza - 12 de octubre
        (11, 1),  # Todos los Santos - 1 de noviembre
        (11, 11), # Independencia de Cartagena - 11 de noviembre
    ]

    @staticmethod
    def calcular_domingo_pascua(año: int) -> date:
        """
        Calcula la fecha del Domingo de Pascua usando el algoritmo de Gauss.
        
        El Domingo de Pascua es el primer domingo después de la primera luna llena
        que ocurre el 21 de marzo o después. Se utiliza el algoritmo matemático
        desarrollado por Carl Friedrich Gauss para calcularlo sin observación astronómica.
        
        Args:
            año: Año para el cual calcular la Pascua
            
        Returns:
            Fecha del Domingo de Pascua como objeto date
        """
        # Algoritmo de Gauss para calcular la Pascua
        # Variables intermedias del algoritmo
        a = año % 19  # Posición en el ciclo metónico (19 años)
        b = año // 100  # Siglo
        c = año % 100  # Año dentro del siglo
        d = b // 4  # Número de siglos bisiestos
        e = b % 4  # Residuo de siglos bisiestos
        f = (b + 8) // 25  # Corrección lunar
        g = (b - f + 1) // 3  # Corrección solar
        h = (19 * a + b - d - g + 15) % 30  # Epacta (edad de la luna)
        i = c // 4  # Número de años bisiestos en el siglo
        k = c % 4  # Residuo de años bisiestos
        l = (32 + 2 * e + 2 * i - h - k) % 7  # Día de la semana
        m = (a + 11 * h + 22 * l) // 451
        n = (h + l - 7 * m + 114) // 31
        p = (h + l - 7 * m + 114) % 31
        
        return date(año, n, p + 1)

    @classmethod
    def obtener_festivos_año(cls, año: int) -> List[date]:
        """
        Obtiene todos los días festivos para un año específico
        """
        festivos = []
        
        # Festivos fijos
        for mes, dia in cls.FESTIVOS_FIJOS:
            festivos.append(date(año, mes, dia))
        
        # Festivos trasladables al lunes
        for mes, dia in cls.FESTIVOS_TRASLADABLES:
            fecha_original = date(año, mes, dia)
            # Si no es lunes, trasladar al siguiente lunes
            if fecha_original.weekday() != 0:  # 0 = lunes
                dias_hasta_lunes = (7 - fecha_original.weekday()) % 7
                if dias_hasta_lunes == 0:
                    dias_hasta_lunes = 7
                fecha_festivo = fecha_original + timedelta(days=dias_hasta_lunes)
            else:
                fecha_festivo = fecha_original
            festivos.append(fecha_festivo)
        
        # Festivos relacionados con la Pascua
        domingo_pascua = cls.calcular_domingo_pascua(año)
        
        # Jueves Santo (3 días antes del domingo de pascua)
        jueves_santo = domingo_pascua - timedelta(days=3)
        festivos.append(jueves_santo)
        
        # Viernes Santo (2 días antes del domingo de pascua)
        viernes_santo = domingo_pascua - timedelta(days=2)
        festivos.append(viernes_santo)
        
        # Ascensión del Señor (39 días después de pascua, trasladado al lunes)
        ascension = domingo_pascua + timedelta(days=39)
        if ascension.weekday() != 0:  # Si no es lunes
            dias_hasta_lunes = (7 - ascension.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            ascension = ascension + timedelta(days=dias_hasta_lunes)
        festivos.append(ascension)
        
        # Corpus Christi (60 días después de pascua, trasladado al lunes)
        corpus_christi = domingo_pascua + timedelta(days=60)
        if corpus_christi.weekday() != 0:  # Si no es lunes
            dias_hasta_lunes = (7 - corpus_christi.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            corpus_christi = corpus_christi + timedelta(days=dias_hasta_lunes)
        festivos.append(corpus_christi)
        
        # Sagrado Corazón de Jesús (68 días después de pascua, trasladado al lunes)
        sagrado_corazon = domingo_pascua + timedelta(days=68)
        if sagrado_corazon.weekday() != 0:  # Si no es lunes
            dias_hasta_lunes = (7 - sagrado_corazon.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            sagrado_corazon = sagrado_corazon + timedelta(days=dias_hasta_lunes)
        festivos.append(sagrado_corazon)
        
        return sorted(festivos)

    @classmethod
    def es_festivo(cls, fecha: date) -> bool:
        """
        Verifica si una fecha específica es día festivo en Colombia.
        
        Args:
            fecha: Fecha a verificar
            
        Returns:
            True si es festivo, False si es día hábil
        """
        festivos_año = cls.obtener_festivos_año(fecha.year)
        return fecha in festivos_año

    @classmethod
    def obtener_siguiente_dia_habil(cls, fecha: date) -> date:
        """
        Encuentra el siguiente día hábil (lunes a viernes, no festivo).
        
        Importante para las rondas: Si un servicio cae en festivo o fin de semana,
        se programa para el siguiente día hábil disponible.
        
        Args:
            fecha: Fecha desde la cual buscar
            
        Returns:
            Fecha del siguiente día hábil
        """
        siguiente_dia = fecha
        
        while True:
            siguiente_dia += timedelta(days=1)
            # Verificar: no es fin de semana (sábado=5, domingo=6) y no es festivo
            if siguiente_dia.weekday() < 5 and not cls.es_festivo(siguiente_dia):
                break
                
        return siguiente_dia

    @classmethod
    def ajustar_dia_rondas(cls, fecha: date) -> Tuple[date, bool]:
        """
        Ajusta el día de las rondas hospitalarias si cae en festivo o fin de semana.
        
        Lógica de negocio:
        - Si la fecha es festivo o fin de semana, las rondas se trasladan al siguiente día hábil
        - Si la fecha es día hábil normal, las rondas son ese mismo día
        
        Args:
            fecha: Fecha a evaluar
            
        Returns:
            Tupla (fecha_ajustada, fue_ajustado)
            - fecha_ajustada: Día en que deben realizarse las rondas
            - fue_ajustado: True si se trasladó, False si es el mismo día
        """
        if cls.es_festivo(fecha) or fecha.weekday() >= 5:  # Festivo o fin de semana
            fecha_ajustada = cls.obtener_siguiente_dia_habil(fecha)
            return fecha_ajustada, True
        
        return fecha, False


def es_dia_festivo(fecha: date = None) -> bool:
    """
    Verifica si hoy (o una fecha específica) es día festivo en Colombia.
    
    Función de acceso rápido que se usa en las vistas para validar
    si el personal debe trabajar o si las rondas se trasladan.
    
    Args:
        fecha: Fecha a verificar. Si es None, usa la fecha actual.
        
    Returns:
        True si es festivo oficial colombiano, False en caso contrario
        
    Ejemplo:
        >>> es_dia_festivo(date(2025, 1, 1))  # Año Nuevo
        True
        >>> es_dia_festivo(date(2025, 1, 2))  # Día normal
        False
    """
    if fecha is None:
        fecha = date.today()
    
    return FestivosColombiaCalculator.es_festivo(fecha)


def obtener_dia_rondas(fecha: date = None) -> Tuple[date, bool]:
    """
    Calcula qué día deben realizarse las rondas hospitalarias.
    
    Función principal usada en panel_principal() para determinar
    qué servicios mostrar cada día.
    
    Args:
        fecha: Fecha a evaluar. Si es None, usa la fecha actual.
        
    Returns:
        Tupla (fecha_rondas, fue_ajustada):
        - fecha_rondas: Día en que deben hacerse las rondas
        - fue_ajustada: True si se trasladó por festivo/fin de semana
        
    Ejemplo:
        >>> obtener_dia_rondas(date(2025, 1, 1))  # Año Nuevo (festivo)
        (date(2025, 1, 2), True)  # Se traslada al siguiente hábil
        >>> obtener_dia_rondas(date(2025, 1, 6))  # Lunes normal
        (date(2025, 1, 6), False)  # Mismo día
    """
    if fecha is None:
        fecha = date.today()
    
    return FestivosColombiaCalculator.ajustar_dia_rondas(fecha)


def obtener_festivos_mes(año: int, mes: int) -> List[date]:
    """
    Obtiene todos los festivos de un mes específico
    """
    festivos_año = FestivosColombiaCalculator.obtener_festivos_año(año)
    return [f for f in festivos_año if f.month == mes]


if __name__ == "__main__":
    # Ejemplo de uso
    hoy = date.today()
    print(f"Hoy ({hoy}) es festivo: {es_dia_festivo(hoy)}")
    
    dia_rondas, fue_ajustado = obtener_dia_rondas(hoy)
    if fue_ajustado:
        print(f"Las rondas se trasladaron al: {dia_rondas}")
    else:
        print(f"Las rondas son hoy: {dia_rondas}")
    
    # Mostrar festivos del año actual
    festivos = FestivosColombiaCalculator.obtener_festivos_año(hoy.year)
    print(f"\nFestivos {hoy.year}:")
    for festivo in festivos:
        print(f"  {festivo.strftime('%A, %d de %B')}")