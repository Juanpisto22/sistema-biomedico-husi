"""
Vistas principales del módulo de rondas biomédicas.

Este módulo contiene las vistas para el registro, visualización,
edición y eliminación de rondas hospitalarias.
"""
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, date

from .forms import RoundEntryForm, OncologyRoundEntryForm, DailySurgeryRoundForm
from .models import RoundEntry, DailySurgeryRecord
from .festivos_colombia import obtener_dia_rondas, es_dia_festivo
from .helpers import (
    is_oncology_service,
    horario_valido_panel,
    horario_visible_historial,
    surgery_available_today,
    get_services_by_day
)
from .exports import exportar_historial_pdf, exportar_historial_excel
from .utils import (
    PRIORITARIOS,
    SEDES_EXTERNAS,
    SURGERY_ROOMS,
    SURGERY_EQUIPMENT,
    SURGERY_DAYS,
    SURGERY_AVAILABLE_DAYS,
    ROUND_STRUCTURE,
    SPANISH_WEEKDAYS,
)


@login_required
@permission_required('rondas.delete_roundentry', raise_exception=True)
@require_POST
def eliminar_registro(request, registro_id):
    """Elimina un registro de ronda."""
    try:
        registro = get_object_or_404(RoundEntry, id=registro_id)
        nombre_registro = f"{registro.get_categoria_display()} - {registro.subservicio}"
        registro.delete()
        
        messages.success(request, f"Registro '{nombre_registro}' eliminado correctamente.")
        return JsonResponse({'success': True, 'message': 'Registro eliminado correctamente'})
    except Exception as e:
        messages.error(request, f"Error al eliminar el registro: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@permission_required('rondas.delete_dailysurgeryrecord', raise_exception=True)
@require_POST
def eliminar_registro_cirugia(request, registro_id):
    """Vista para eliminar un registro de cirugía diario (solo administradores)"""
    try:
        registro = get_object_or_404(DailySurgeryRecord, id=registro_id)
        fecha_registro = registro.fecha.strftime('%d/%m/%Y')
        registro.delete()
        
        messages.success(request, f"Registro de cirugía del {fecha_registro} eliminado correctamente.")
        return JsonResponse({'success': True, 'message': 'Registro de cirugía eliminado correctamente'})
    except Exception as e:
        messages.error(request, f"Error al eliminar el registro de cirugía: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def editar_registro(request, registro_id):
    """Permite editar un registro existente."""
    registro = get_object_or_404(RoundEntry, id=registro_id)

    if registro.usuario != request.user and not request.user.has_perm('rondas.change_roundentry'):
        messages.error(request, 'No tienes permisos para editar este registro. Solo puedes editar los registros que tú creaste o usuarios con permiso de edición pueden hacerlo.')
        return redirect('historial_servicios')

    if request.method == 'POST':
        form = RoundEntryForm(request.POST, instance=registro)
        if form.is_valid():
            registro_actualizado = form.save(commit=False)
            registro_actualizado.usuario = registro.usuario
            registro_actualizado.save()

            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('historial_servicios')
        else:
            messages.error(request, 'Error al actualizar el registro. Revise los datos.')
    else:
        form = RoundEntryForm(instance=registro)

    return render(request, 'rondas/editar_registro.html', {
        'form': form,
        'registro': registro,
        'tipo': 'servicio'
    })


@login_required
def editar_registro_cirugia(request, registro_id):
    """Vista para editar un registro de cirugía diario.

    Se permite editar si el usuario es el creador del registro O si tiene
    el permiso 'rondas.change_dailysurgeryrecord' (administrador).
    """
    registro = get_object_or_404(DailySurgeryRecord, id=registro_id)

    if registro.usuario != request.user and not request.user.has_perm('rondas.change_dailysurgeryrecord'):
        messages.error(request, 'No tienes permisos para editar este registro. Solo puedes editar los registros que tú creaste o usuarios con permiso de edición pueden hacerlo.')
        return redirect('historial_servicios')

    if request.method == 'POST':
        form = DailySurgeryRoundForm(request.POST, instance=registro)
        if form.is_valid():
            registro_actualizado = form.save(commit=False)
            registro_actualizado.usuario = registro.usuario
            registro_actualizado.save()

            messages.success(request, 'Registro de cirugía actualizado correctamente.')
            return redirect('historial_servicios')
        else:
            messages.error(request, 'Error al actualizar el registro de cirugía. Revise los datos.')
    else:
        form = DailySurgeryRoundForm(instance=registro)

    return render(request, 'rondas/editar_registro.html', {
        'form': form,
        'registro': registro,
        'tipo': 'cirugia'
    })


def logout_redirect(request):
    """
    Cierra la sesión del usuario y redirige al login.
    
    Args:
        request: Objeto HttpRequest
        
    Returns:
        HttpResponse: Redirección a la página de login
    """
    if request.method not in ("GET", "POST"):
        return HttpResponseNotAllowed(["GET", "POST"])
    logout(request)
    return redirect("http://127.0.0.1:8000/")


@login_required
def panel_principal(request):
    """
    Panel principal para registrar rondas biomédicas.
    - Muestra servicios según el día de la semana
    - Maneja ajustes por días festivos
    - Permite registro entre 7:00 AM y 11:59 PM
    """
    ahora = timezone.localtime()
    if not horario_valido_panel(ahora):
        return render(request, "rondas/fuera_horario.html", {"ahora": ahora})

    # Verificar si hoy es festivo y ajustar el día de las rondas
    fecha_hoy = ahora.date()
    fecha_rondas, dia_ajustado = obtener_dia_rondas(fecha_hoy)
    
    # Verificar si ayer fue festivo
    fecha_ayer = fecha_hoy - timezone.timedelta(days=1)
    ayer_fue_festivo = es_dia_festivo(fecha_ayer)
    
    # Si el día fue ajustado por festivo, usar el día de la semana ajustado
    if dia_ajustado:
        day = fecha_rondas.weekday()
        dia_actual = f"{SPANISH_WEEKDAYS[ahora.weekday()]} (trasladado por festivo a {SPANISH_WEEKDAYS[day]})"
        es_dia_festivo_hoy = True
    elif ayer_fue_festivo:
        # Si ayer fue festivo, mostrar los servicios de ayer también
        day_anterior = fecha_ayer.weekday()
        day = ahora.weekday()
        dia_actual = f"{SPANISH_WEEKDAYS[day]} (incluye servicios del {SPANISH_WEEKDAYS[day_anterior]} festivo)"
        es_dia_festivo_hoy = False
        # Combinar servicios del día actual y del día festivo anterior
        servicios = get_services_by_day(day)
        servicios_ayer = get_services_by_day(day_anterior)
        # Combinar las listas sin duplicados
        for key in ["ronda_diaria", "servicio_salas", "laboratorio_clinico"]:
            if key in servicios and key in servicios_ayer:
                servicios[key] = list(set(servicios[key] + servicios_ayer[key]))
    else:
        day = ahora.weekday()
        dia_actual = SPANISH_WEEKDAYS[ahora.weekday()]
        es_dia_festivo_hoy = False
    
    if not (dia_ajustado or ayer_fue_festivo):
        servicios = get_services_by_day(day)

    # Formularios y lógica original
    posted_key: tuple[str, str] | None = None
    posted_form: RoundEntryForm | None = None
    if request.method == "POST":
        tipo_formulario = request.POST.get("tipo_formulario")
        if tipo_formulario == "ronda":
            posted_key = (
                request.POST.get("categoria", ""),
                request.POST.get("subservicio", ""),
            )
            
            # Usar formulario correcto según el servicio
            subservicio = request.POST.get("subservicio", "")
            if is_oncology_service(subservicio):
                round_form = OncologyRoundEntryForm(request.POST)
            else:
                round_form = RoundEntryForm(request.POST)
            
            if round_form.is_valid():
                registro = round_form.save(commit=False)
                registro.usuario = request.user
                
                try:
                    registro.save()
                    messages.success(request, "Registro guardado correctamente.")
                    return redirect("panel_principal")
                except Exception as e:
                    messages.error(request, f"Error al guardar: {str(e)}")
            else:
                messages.error(request, "Por favor, corrija los errores en el formulario.")
            posted_form = round_form
        else:
            messages.error(request, "No se pudo identificar el formulario enviado.")

    # Salas de cirugía - Registros diarios individuales
    surgery_layout = []
    current_day_name = None
    
    if servicios.get("surgery_available", False):
        current_day_name = SURGERY_DAYS[datetime.now().weekday()]
        
        for sala in SURGERY_ROOMS:
            equipos = [
                equipo
                for equipo in SURGERY_EQUIPMENT
                if not (equipo == "Microscopio" and sala != "1")
            ]
            surgery_layout.append({"sala": sala, "equipos": equipos})

    # Crear estructura de categorías para el template
    categories = []
    
    # Servicios prioritarios (siempre disponibles)
    if PRIORITARIOS:
        prioritarios_forms = []
        for servicio in PRIORITARIOS:
            form_key = ("prioritarios", servicio)
            form = RoundEntryForm(initial={"categoria": "prioritarios", "subservicio": servicio})
            if posted_key == form_key and posted_form:
                form = posted_form
            prioritarios_forms.append({"nombre": servicio, "form": form})
        
        categories.append({
            "clave": "prioritarios",
            "titulo": "🚨 Servicios Prioritarios (Siempre disponibles)",
            "subservicios": prioritarios_forms
        })
    
    # Rondas diarias (según día)
    if servicios.get("ronda_diaria"):
        ronda_diaria_forms = []
        for servicio in servicios["ronda_diaria"]:
            form_key = ("ronda_diaria", servicio)
            # Usar formulario especial para Oncología
            if is_oncology_service(servicio):
                form = OncologyRoundEntryForm(initial={"categoria": "ronda_diaria", "subservicio": servicio})
            else:
                form = RoundEntryForm(initial={"categoria": "ronda_diaria", "subservicio": servicio})
            if posted_key == form_key and posted_form:
                form = posted_form
            ronda_diaria_forms.append({"nombre": servicio, "form": form, "is_oncology": is_oncology_service(servicio)})
        
        categories.append({
            "clave": "ronda_diaria",
            "titulo": f"📅 Ronda Diaria - {dia_actual}",
            "subservicios": ronda_diaria_forms
        })
    
    # Servicios de salas (según día)
    if servicios.get("servicio_salas"):
        servicio_salas_forms = []
        for servicio in servicios["servicio_salas"]:
            form_key = ("servicio_salas", servicio)
            # Usar formulario especial para Oncología
            if is_oncology_service(servicio):
                form = OncologyRoundEntryForm(initial={"categoria": "servicio_salas", "subservicio": servicio})
            else:
                form = RoundEntryForm(initial={"categoria": "servicio_salas", "subservicio": servicio})
            if posted_key == form_key and posted_form:
                form = posted_form
            servicio_salas_forms.append({"nombre": servicio, "form": form, "is_oncology": is_oncology_service(servicio)})
        
        categories.append({
            "clave": "servicio_salas",
            "titulo": f"🏥 Servicio de Salas - {dia_actual}",
            "subservicios": servicio_salas_forms
        })
    
    # Laboratorio clínico (solo lunes)
    if servicios.get("laboratorio_clinico"):
        lab_forms = []
        for servicio in servicios["laboratorio_clinico"]:
            form_key = ("laboratorio_clinico", servicio)
            # Usar formulario especial para Oncología
            if is_oncology_service(servicio):
                form = OncologyRoundEntryForm(initial={"categoria": "laboratorio_clinico", "subservicio": servicio})
            else:
                form = RoundEntryForm(initial={"categoria": "laboratorio_clinico", "subservicio": servicio})
            if posted_key == form_key and posted_form:
                form = posted_form
            lab_forms.append({"nombre": servicio, "form": form, "is_oncology": is_oncology_service(servicio)})
        
        categories.append({
            "clave": "laboratorio_clinico",
            "titulo": "🧪 Laboratorio Clínico (Solo Lunes)",
            "subservicios": lab_forms
        })
    
    # Sedes externas (siempre disponibles)
    if SEDES_EXTERNAS:
        sedes_forms = []
        for servicio in SEDES_EXTERNAS:
            form_key = ("sedes_externas", servicio)
            # Usar formulario especial para Oncología
            if is_oncology_service(servicio):
                form = OncologyRoundEntryForm(initial={"categoria": "sedes_externas", "subservicio": servicio})
            else:
                form = RoundEntryForm(initial={"categoria": "sedes_externas", "subservicio": servicio})
            if posted_key == form_key and posted_form:
                form = posted_form
            sedes_forms.append({"nombre": servicio, "form": form, "is_oncology": is_oncology_service(servicio)})
        
        categories.append({
            "clave": "sedes_externas",
            "titulo": "🏢 Sedes Externas (Siempre disponibles)",
            "subservicios": sedes_forms
        })

    contexto = {
        "dia_actual": dia_actual,
        "ahora": ahora,
        "es_dia_festivo": es_dia_festivo_hoy,
        "fecha_rondas": fecha_rondas,
        "fecha_original": fecha_hoy,
        "categories": categories,
        "surgery_days": [current_day_name] if current_day_name else [],
        "current_day_name": current_day_name,
        "surgery_layout": surgery_layout,
        "surgery_available": servicios.get("surgery_available", False) and day in SURGERY_AVAILABLE_DAYS,
        "surgery_available_days": [SPANISH_WEEKDAYS[day] for day in SURGERY_AVAILABLE_DAYS],
    }
    return render(request, "rondas/panel.html", contexto)


@login_required
def historial_servicios(request):
    """
    Muestra el historial de rondas registradas.
    - Filtra registros entre 5:00 AM y 6:00 PM
    - Combina rondas de servicios regulares y cirugías
    - Permite filtrar por categoría y subservicio
    """
    from itertools import chain
    from operator import attrgetter
    import json
    
    # Obtener registros de servicios
    registros_servicios = RoundEntry.objects.select_related("usuario")
    categoria = request.GET.get("categoria")
    if categoria:
        registros_servicios = registros_servicios.filter(categoria=categoria)
    subservicio = request.GET.get("subservicio")
    if subservicio:
        registros_servicios = registros_servicios.filter(subservicio__icontains=subservicio)
    
    # Obtener registros de cirugías diarias
    registros_cirugias = DailySurgeryRecord.objects.select_related("usuario")
    
    # Filtrar registros por horario (5am a 6pm)
    from django.utils import timezone
    registros_servicios_filtrados = [
        r for r in registros_servicios 
        if horario_visible_historial(timezone.localtime(r.fecha_creacion))
    ]
    registros_cirugias_filtrados = [
        r for r in registros_cirugias 
        if horario_visible_historial(timezone.localtime(r.fecha_creacion))
    ]
    
    # Combinar ambos tipos de registros y ordenar por fecha
    registros_combinados = list(chain(registros_servicios_filtrados, registros_cirugias_filtrados))
    registros = sorted(registros_combinados, key=attrgetter('fecha_creacion'), reverse=True)

    # Para soportar hasta 4 firmas de jefes (Oncología/CJO) almacenadas en
    # el campo `firma_servicio` como JSON (lista de dicts {"name":..., "img":...}).
    # Normalizamos añadiendo un atributo dinámico `jefe_firmas` a cada registro
    for r in registros:
        r.jefe_firmas = None
        try:
            if r.firma_servicio and isinstance(r.firma_servicio, str) and r.firma_servicio.strip().startswith('['):
                parsed = json.loads(r.firma_servicio)
                if isinstance(parsed, list) and parsed:
                    # Cada item esperado: {'name': 'Jefe 1', 'img': 'data:image/png;base64,...'}
                    r.jefe_firmas = parsed[:4]
        except Exception:
            # Si no es JSON válido, ignorar y dejar jefe_firmas = None
            r.jefe_firmas = None

    # Agregar categorías adicionales que no están en ROUND_STRUCTURE
    categorias_completas = ROUND_STRUCTURE.copy()
    categorias_completas["prioritarios"] = {
        "titulo": "Servicios Prioritarios",
        "descripcion": "Servicios críticos siempre disponibles"
    }
    categorias_completas["sedes_externas"] = {
        "titulo": "Sedes Externas", 
        "descripcion": "Servicios en sedes externas"
    }
    categorias_completas["cirugia"] = {
        "titulo": "Cirugías",
        "descripcion": "Registros de rondas de cirugía"
    }
    
    return render(
        request,
        "rondas/historial.html",
        {
            "registros": registros,
            "categorias": categorias_completas,
        },
    )


@login_required
def indicadores(request):
    totales = list(
        RoundEntry.objects.values("categoria")
        .annotate(total=Count("id"), con_novedad=Count("id"))
        .order_by("categoria")
    )

    resumen = [
        {
            "clave": item["categoria"],
            "titulo": ROUND_STRUCTURE.get(item["categoria"], {}).get("titulo", item["categoria"].title()),
            "total": item["total"],
            "con_novedad": item["con_novedad"],
        }
        for item in totales
    ]

    # Indicadores adicionales
    equipos_fuera_servicio = RoundEntry.objects.filter(
        fuera_de_servicio=True
    ).count()
    
    eventos_seguridad = RoundEntry.objects.filter(
        tiene_eventos_seguridad=True
    ).count()
    
    # Top 5 servicios con más equipos fuera de servicio
    top_fuera_servicio = list(
        RoundEntry.objects.filter(fuera_de_servicio=True)
        .values("subservicio", "categoria")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    
    # Top 5 servicios con más eventos de seguridad
    top_eventos_seguridad = list(
        RoundEntry.objects.filter(tiene_eventos_seguridad=True)
        .values("subservicio", "categoria")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    # Registros diarios de cirugía agrupados por fecha
    semanal_cirugia = (
        DailySurgeryRecord.objects.values("fecha")
        .annotate(total=Count("id"))
        .order_by("-fecha")[:12]
    )

    return render(
        request,
        "rondas/indicadores.html",
        {
            "resumen": resumen,
            "semanal_cirugia": semanal_cirugia,
            "equipos_fuera_servicio": equipos_fuera_servicio,
            "eventos_seguridad": eventos_seguridad,
            "top_fuera_servicio": top_fuera_servicio,
            "top_eventos_seguridad": top_eventos_seguridad,
        },
    )


# Funciones de exportación definidas en rondas/exports.py
