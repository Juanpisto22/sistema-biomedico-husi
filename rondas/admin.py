"""
Configuración del panel de administración de Django para rondas biomédicas.

Este módulo registra los modelos en el panel de administración,
permitiendo gestionar los datos desde la interfaz web de Django.
"""
from django.contrib import admin
from .models import RoundEntry, DailySurgeryRecord, Service, Room, Equipment


@admin.register(RoundEntry)
class RoundEntryAdmin(admin.ModelAdmin):
    """Administración de registros de rondas"""
    list_display = ['id', 'categoria', 'subservicio', 'usuario', 'fecha_creacion', 'tiene_eventos_seguridad']
    list_filter = ['categoria', 'tiene_eventos_seguridad', 'fecha_creacion']
    search_fields = ['subservicio', 'hallazgo', 'placa_equipo']
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion']


@admin.register(DailySurgeryRecord)
class DailySurgeryRecordAdmin(admin.ModelAdmin):
    """Administración de registros diarios de cirugía"""
    list_display = ['id', 'fecha', 'dia_semana', 'sala', 'equipo', 'estado_equipo', 'equipo_en_uso', 'usuario']
    list_filter = ['fecha', 'dia_semana', 'sala', 'estado_equipo', 'equipo_en_uso']
    search_fields = ['sala', 'equipo', 'observaciones']
    date_hierarchy = 'fecha'
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Administración de servicios hospitalarios"""
    list_display = ['id', 'nombre', 'categoria', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Administración de salas"""
    list_display = ['id', 'numero', 'nombre', 'tipo_sala', 'servicio', 'activo']
    list_filter = ['tipo_sala', 'servicio', 'activo']
    search_fields = ['numero', 'nombre']
    ordering = ['numero']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Administración de equipos médicos"""
    list_display = ['id', 'nombre', 'numero_placa', 'sala', 'servicio', 'estado', 'activo']
    list_filter = ['estado', 'servicio', 'activo']
    search_fields = ['nombre', 'numero_placa']
    ordering = ['nombre']
