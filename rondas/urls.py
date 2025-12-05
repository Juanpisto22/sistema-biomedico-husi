from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel_principal, name="panel_principal"),
    path("historial/", views.historial_servicios, name="historial_servicios"),
    path("historial/export/excel/", views.exportar_historial_excel, name="exportar_historial_excel"),
    path("historial/export/pdf/", views.exportar_historial_pdf, name="exportar_historial_pdf"),
    path("indicadores/", views.indicadores, name="indicadores"),
    path("eliminar/registro/<int:registro_id>/", views.eliminar_registro, name="eliminar_registro"),
    path("eliminar/cirugia/<int:registro_id>/", views.eliminar_registro_cirugia, name="eliminar_registro_cirugia"),
    path("editar/registro/<int:registro_id>/", views.editar_registro, name="editar_registro"),
    path("editar/cirugia/<int:registro_id>/", views.editar_registro_cirugia, name="editar_registro_cirugia"),
]
