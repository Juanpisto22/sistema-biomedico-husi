from django.conf import settings
from django.db import models


class RoundEntry(models.Model):
    """
    Modelo para los registros de rondas biomédicas diarias.
    
    Representa una ronda realizada por el personal de biomedicina
    en los diferentes servicios del hospital.
    
    Características:
    - Registra hallazgos y eventos de seguridad
    - Captura firmas digitales del personal (hasta 3 para Oncología)
    - Asociado a un usuario autenticado
    - Ordenado por fecha de creación descendente
    """

    # Categorías de servicios hospitalarios
    CATEGORIAS = [
        ("prioritarios", "Prioritarios"),  # Servicios críticos 24/7
        ("ronda_diaria", "Ronda diaria"),  # Rondas rutinarias diarias
        ("servicio_salas", "Servicio de salas"),  # Salas de hospitalización
        ("laboratorio_clinico", "Laboratorio clínico"),  # Laboratorios
        ("sedes_externas", "Sedes externas"),  # Sedes fuera del hospital principal
    ]

    # Usuario que registra la ronda (tecnólogo o administrador)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rondas_registradas",
    )
    
    # Información del servicio
    categoria = models.CharField(max_length=32, choices=CATEGORIAS)  # Tipo de servicio
    subservicio = models.CharField(max_length=100)  # Nombre específico del servicio
    
    # Detalles del registro
    hallazgo = models.TextField(blank=True)  # Observaciones encontradas
    placa_equipo = models.CharField(max_length=100, blank=True)  # Número de placa del equipo
    orden_trabajo = models.CharField(max_length=100, blank=True)  # Número de orden de trabajo
    
    # Eventos de seguridad
    tiene_eventos_seguridad = models.BooleanField(default=False, verbose_name="¿Hay eventos de seguridad?")
    eventos_seguridad = models.TextField(blank=True, verbose_name="Descripción de eventos de seguridad")
    
    # Estado del equipo
    fuera_de_servicio = models.BooleanField(default=False, verbose_name="¿Equipo fuera de servicio?")
    # Firma del encargado del servicio (firma 1 - obligatoria)
    nombre_encargado_servicio = models.CharField(max_length=100, default='Sin especificar')
    firma_servicio = models.TextField(blank=True, null=True, verbose_name="Firma del encargado del servicio")
    
    # Campos adicionales para servicios con múltiples encargados (ej: Oncología con 3 pisos)
    nombre_encargado_servicio_2 = models.CharField(max_length=100, blank=True, default='')
    firma_servicio_2 = models.TextField(blank=True, null=True, verbose_name="Firma del encargado del servicio 2")
    nombre_encargado_servicio_3 = models.CharField(max_length=100, blank=True, default='')
    firma_servicio_3 = models.TextField(blank=True, null=True, verbose_name="Firma del encargado del servicio 3")
    
    # Firma del tecnólogo o supervisor que realiza la ronda (obligatoria)
    nombre_encargado_ronda = models.CharField(max_length=100, default='Sin especificar')
    firma_ronda = models.TextField(blank=True, null=True, verbose_name="Firma del encargado de la ronda")
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha y hora de registro automática

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Registro de ronda"
        verbose_name_plural = "Registros de rondas"

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.subservicio}"


# NOTA: Modelo SurgeryRound ELIMINADO - Consolidado en DailySurgeryRecord
# Los registros semanales ahora se manejan como múltiples registros diarios


class Service(models.Model):
    """
    Catálogo de servicios del hospital.
    
    Define los servicios disponibles y sus reglas de programación
    (qué días de la semana aplican).
    """
    CATEGORIAS = [
        ("PRIORITARIO", "Prioritario"),  # Servicios críticos
        ("DIARIA", "Ronda diaria"),  # Rondas diarias programadas
        ("SALAS", "Servicio de salas"),  # Áreas de hospitalización
        ("LAB", "Laboratorio clínico"),  # Laboratorios
        ("SEDES", "Sedes externas"),  # Sedes externas al hospital
    ]
    
    # Campos en español para consistencia
    nombre = models.CharField(max_length=200, default='Sin especificar', verbose_name="Nombre del servicio")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='DIARIA', verbose_name="Categoría")
    reglas_dias = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Reglas de días",
        help_text='Formato: {"lunes": true, "martes": false, ...}'
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["nombre"]
    
    def __str__(self):
        return self.nombre
    
    def clean(self):
        """Validar formato del JSONField reglas_dias"""
        from django.core.exceptions import ValidationError
        if self.reglas_dias and not isinstance(self.reglas_dias, dict):
            raise ValidationError("Las reglas de días deben ser un diccionario")


class Room(models.Model):
    """Salas o habitaciones del hospital."""
    TIPOS = [
        ("sala_cirugia", "Sala de cirugía"),
        ("habitacion", "Habitación"),
        ("consulta", "Consulta"),
        ("laboratorio", "Laboratorio"),
        ("otro", "Otro"),
    ]
    
    # Campos en español para consistencia
    numero = models.CharField(max_length=50, default='0', verbose_name="Número")
    nombre = models.CharField(max_length=200, blank=True, default='', verbose_name="Nombre")
    tipo_sala = models.CharField(max_length=20, choices=TIPOS, default="otro", verbose_name="Tipo de sala")
    servicio = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="salas", verbose_name="Servicio", null=True, blank=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
        ordering = ["numero"]
    
    def __str__(self):
        return f"{self.numero} - {self.nombre or self.servicio.nombre}"


class Equipment(models.Model):
    """
    Catálogo de equipos médicos del hospital.
    
    Registra los equipos disponibles, su ubicación y estado operativo.
    Permite el seguimiento de equipos críticos durante las rondas.
    """
    # Estados posibles del equipo
    ESTADOS = [
        ("operativo_completo", "Operativo completo"),  # Funcionando perfectamente
        ("operativo_parcial", "Operativo parcial"),  # Funcional con limitaciones
        ("fuera_de_servicio", "Fuera de servicio"),  # No operativo
    ]
    
    # Campos en español para consistencia
    nombre = models.CharField(max_length=200, default='Equipo sin nombre', verbose_name="Nombre del equipo")
    numero_placa = models.CharField(max_length=100, blank=True, default='', verbose_name="Número de placa")
    sala = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name="equipos", 
        null=True, 
        blank=True,
        verbose_name="Sala"
    )
    servicio = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name="equipos",
        verbose_name="Servicio",
        null=True,
        blank=True
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default="operativo_completo", verbose_name="Estado")
    etiquetas = models.JSONField(
        default=list, 
        blank=True,
        verbose_name="Etiquetas",
        help_text='Lista de etiquetas: ["crítico", "calibración", ...]'
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ["nombre"]
    
    def __str__(self):
        return f"{self.nombre} - {self.numero_placa or 'Sin placa'}"
    
    def clean(self):
        """Validar formato del JSONField etiquetas"""
        from django.core.exceptions import ValidationError
        if self.etiquetas and not isinstance(self.etiquetas, list):
            raise ValidationError("Las etiquetas deben ser una lista")


class DailySurgeryRecord(models.Model):
    """Registro diario de equipos de cirugía"""
    ESTADOS = [
        ("operativo_completo", "Operativo completo"),
        ("operativo_parcial", "Operativo parcial"),
        ("fuera_de_servicio", "Fuera de servicio"),
    ]
    
    usuario = models.ForeignKey("auth.User", on_delete=models.CASCADE, verbose_name="Usuario")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha = models.DateField(verbose_name="Fecha del registro")
    dia_semana = models.CharField(max_length=20, verbose_name="Día de la semana")
    sala = models.CharField(max_length=10, verbose_name="Sala")
    equipo = models.CharField(max_length=100, verbose_name="Equipo")
    equipo_en_uso = models.BooleanField(default=True, verbose_name="Equipo en uso")
    estado_equipo = models.CharField(max_length=20, choices=ESTADOS, blank=True, null=True, verbose_name="Estado del equipo")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    nombre_encargado_servicio = models.CharField(max_length=100, blank=True, verbose_name="Encargado del servicio")
    nombre_encargado_ronda = models.CharField(max_length=100, blank=True, verbose_name="Encargado de la ronda")
    firma_servicio = models.TextField(blank=True, verbose_name="Firma del encargado del servicio")
    firma_ronda = models.TextField(blank=True, verbose_name="Firma del encargado de la ronda")
    
    class Meta:
        verbose_name = "Registro Diario de Cirugía"
        verbose_name_plural = "Registros Diarios de Cirugía"
        unique_together = [["fecha", "sala", "equipo"]]  # Un registro por día, sala y equipo
        ordering = ["-fecha_creacion"]
    
    def __str__(self):
        return f"{self.fecha} - Sala {self.sala} - {self.equipo}"
