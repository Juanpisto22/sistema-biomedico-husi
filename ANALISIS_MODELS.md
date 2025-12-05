# Análisis de Modelos - Sistema de Rondas Biomédicas

## Estado Actual (Problemas Identificados)

### 1. Redundancia de Modelos
- **SurgeryRound**: Registro semanal con datos en JSONField
- **DailySurgeryRecord**: Registro diario con campos explícitos
- **Problema**: Ambos registran lo mismo (equipos de cirugía), causando confusión y duplicación de datos

### 2. Firmas Repetidas
Cada modelo repite los mismos campos de firma:
- `nombre_encargado_servicio` + `firma_servicio`
- `nombre_encargado_servicio_2` + `firma_servicio_2` (solo RoundEntry para Oncología)
- `nombre_encargado_servicio_3` + `firma_servicio_3` (solo RoundEntry para Oncología)
- `nombre_encargado_ronda` + `firma_ronda`

**Impacto**: 8 campos en RoundEntry solo para firmas (16 incluyendo nombres)

### 3. Inconsistencia de Nomenclatura
- Modelos Service, Room, Equipment usan **inglés**: `name`, `plate_number`
- RoundEntry, SurgeryRound usan **español**: `nombre_encargado_servicio`, `firma_servicio`
- **Problema**: Código inconsistente dificulta mantenimiento

### 4. JSONFields sin Validación
- `SurgeryRound.datos`: Sin estructura definida
- `Service.day_rules`: Sin validación de formato
- `Equipment.tags`: Sin validación de tipos
- **Problema**: Datos no validados pueden causar errores en runtime

### 5. Campos de Equipo Repetidos en RoundEntry
No existen en el modelo actual pero se mencionaban en análisis previo:
- `equipo_1`, `equipo_2`, `equipo_3`
- `estado_equipo_1`, `estado_equipo_2`, `estado_equipo_3`
(Verificar si existen en versión anterior o si fueron removidos)

## Propuesta de Optimización

### Opción 1: Normalización Completa (Recomendada)

#### Modelo: Signature (Nuevo)
```python
class Signature(models.Model):
    """Firma digital capturada durante una ronda"""
    nombre_firmante = models.CharField(max_length=100)
    rol_firmante = models.CharField(choices=[
        ("servicio", "Personal del Servicio"),
        ("ronda", "Encargado de Ronda"),
    ])
    firma_imagen = models.TextField()  # Base64
    fecha_firma = models.DateTimeField(auto_now_add=True)
    
    # Relación genérica para usar con cualquier modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
```

#### Modelo: RoundEntry (Simplificado)
```python
class RoundEntry(models.Model):
    usuario = models.ForeignKey(...)
    categoria = models.CharField(...)
    subservicio = models.CharField(...)
    hallazgo = models.TextField(...)
    placa_equipo = models.CharField(...)
    orden_trabajo = models.CharField(...)
    tiene_eventos_seguridad = models.BooleanField(...)
    eventos_seguridad = models.TextField(...)
    fuera_de_servicio = models.BooleanField(...)
    fecha_creacion = models.DateTimeField(...)
    
    # Las firmas ahora son relaciones inversas:
    # self.signatures.filter(rol_firmante="servicio")
    # self.signatures.filter(rol_firmante="ronda")
```

#### Modelo: SurgeryRecord (Consolidado - reemplaza SurgeryRound + DailySurgeryRecord)
```python
class SurgeryRecord(models.Model):
    """Registro de equipos de cirugía (puede ser diario o semanal)"""
    usuario = models.ForeignKey(...)
    fecha_inicio = models.DateField()  # Para registros diarios: ese día. Para semanales: lunes
    fecha_fin = models.DateField(null=True)  # Para semanales: viernes. Para diarios: None
    tipo_registro = models.CharField(choices=[("diario", "Diario"), ("semanal", "Semanal")])
    sala = models.CharField(...)
    equipo = models.CharField(...)
    estado_equipo = models.CharField(...)
    observaciones = models.TextField(...)
    fecha_creacion = models.DateTimeField(...)
    
    # Firmas también como relaciones
```

**Ventajas**:
- Elimina 6+ campos de firma de cada modelo
- Firmas normalizadas y reutilizables
- Fácil agregar más firmas sin cambiar estructura
- Consolida SurgeryRound + DailySurgeryRecord en uno

**Desventajas**:
- Requiere migración compleja
- Queries más complejas (JOIN adicional)
- Cambio mayor en código existente

---

### Opción 2: Optimización Moderada (Más Simple)

#### Mantener estructura básica, pero:

1. **Consolidar SurgeryRound + DailySurgeryRecord**
   - Eliminar uno de los dos
   - Si se elimina SurgeryRound: migrar datos JSON a DailySurgeryRecord expandido
   - Si se elimina DailySurgeryRecord: estandarizar uso de JSONField en SurgeryRound

2. **Estandarizar nombres a español**
   ```python
   # Service
   nombre = models.CharField(...)  # antes: name
   categoria = models.CharField(...)  # antes: category
   reglas_dias = models.JSONField(...)  # antes: day_rules
   activo = models.BooleanField(...)  # antes: active
   ```

3. **Agregar validación a JSONFields**
   ```python
   def clean(self):
       if self.day_rules and not isinstance(self.day_rules, dict):
           raise ValidationError("day_rules debe ser un diccionario")
   ```

4. **Mantener campos de firma como están**
   - Más simple de implementar
   - Sin cambios en vistas/formularios

**Ventajas**:
- Migración más sencilla
- Menos cambios en código existente
- Rápido de implementar

**Desventajas**:
- Sigue teniendo campos repetidos de firmas
- No tan escalable

---

## Recomendación Final

**Implementar Opción 2 (Optimización Moderada)** por las siguientes razones:

1. ✅ **Menor riesgo**: Cambios incrementales, más fácil de revertir
2. ✅ **Compilación garantizada**: Menos cambios = menos errores
3. ✅ **Mantiene funcionalidad**: Sistema sigue trabajando igual
4. ✅ **Cumple objetivo del usuario**: "limpia el codigo para que se permita compilarlo"

### Pasos de Implementación:

1. ✅ **Consolidar modelos de cirugía**
   - Mantener `DailySurgeryRecord` (más explícito)
   - Eliminar `SurgeryRound` (JSON menos claro)
   - Migrar datos existentes

2. ✅ **Estandarizar nombres a español**
   - Service: name → nombre
   - Room: number → numero, name → nombre
   - Equipment: name → nombre, plate_number → numero_placa

3. ✅ **Agregar validación a JSONFields**
   - Service.day_rules
   - Equipment.tags
   
4. ✅ **Agregar __str__ y Meta faltantes**
   - Mejorar representaciones legibles

5. ⚠️ **Mantener campos de firma como están**
   - Aunque no es ideal, evita refactorización masiva
   - Puede mejorarse en versión futura

---

## Migración de Datos

### Consolidación SurgeryRound → DailySurgeryRecord

```python
# Script de migración
for surgery_round in SurgeryRound.objects.all():
    datos = surgery_round.datos  # JSONField
    
    # Extraer datos del JSON y crear registros diarios
    for dia, salas in datos.items():
        fecha = calcular_fecha_desde_semana(surgery_round.semana_inicio, dia)
        
        for sala, equipos in salas.items():
            for equipo, estado in equipos.items():
                DailySurgeryRecord.objects.create(
                    usuario=surgery_round.usuario,
                    fecha=fecha,
                    dia_semana=dia,
                    sala=sala,
                    equipo=equipo,
                    estado_equipo=estado.get("estado"),
                    observaciones=surgery_round.observaciones,
                    nombre_encargado_servicio=surgery_round.nombre_encargado_servicio,
                    nombre_encargado_ronda=surgery_round.nombre_encargado_ronda,
                    firma_servicio=surgery_round.firma_servicio,
                    firma_ronda=surgery_round.firma_ronda,
                )
```

### Renombrar campos (requiere migración Django)

```python
# En migration file
operations = [
    migrations.RenameField('Service', 'name', 'nombre'),
    migrations.RenameField('Service', 'category', 'categoria'),
    # ...
]
```

---

## Estado Final Esperado

### Modelos Optimizados:

1. **RoundEntry**: Sin cambios mayores (mantener firmas inline por simplicidad)
2. **DailySurgeryRecord**: Modelo único para cirugía (SurgeryRound eliminado)
3. **Service**: Campos en español, JSONField validado
4. **Room**: Campos en español
5. **Equipment**: Campos en español, JSONField validado

### Archivos Afectados:
- `models.py` - Cambios principales
- `views.py` - Actualizar referencias a SurgeryRound
- `forms.py` - Eliminar SurgeryRoundForm
- `admin.py` - Actualizar registros de modelos
- `urls.py` - Verificar rutas de cirugía
- Templates - Actualizar referencias de campos

### Verificación Post-Migración:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py test
```
