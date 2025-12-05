import json
from django import forms

from .models import RoundEntry, DailySurgeryRecord


class RoundEntryForm(forms.ModelForm):
    """Form para crear/editar registros de ronda."""
    
    class Meta:
        model = RoundEntry
        fields = [
            "categoria",
            "subservicio",
            "hallazgo",
            "placa_equipo",
            "orden_trabajo",
            "tiene_eventos_seguridad",
            "eventos_seguridad",
            "fuera_de_servicio",
            "nombre_encargado_servicio",
            "firma_servicio",
            "nombre_encargado_ronda",
            "firma_ronda",
        ]
        widgets = {
            "categoria": forms.HiddenInput(),
            "subservicio": forms.HiddenInput(),
            "hallazgo": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "placa_equipo": forms.TextInput(attrs={"class": "form-control"}),
            "orden_trabajo": forms.TextInput(attrs={"class": "form-control"}),
            "tiene_eventos_seguridad": forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            "eventos_seguridad": forms.Textarea(attrs={"rows": 2, "class": "form-control", "disabled": True}),
            "fuera_de_servicio": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_encargado_servicio": forms.TextInput(attrs={"class": "form-control"}),
            "firma_servicio": forms.TextInput(attrs={"type": "hidden"}),
            "nombre_encargado_ronda": forms.TextInput(attrs={"class": "form-control"}),
            "firma_ronda": forms.TextInput(attrs={"type": "hidden"}),
        }

    def clean(self):
        """Validación adicional del formulario."""
        cleaned_data = super().clean()
        
        nombre_servicio = cleaned_data.get('nombre_encargado_servicio')
        nombre_ronda = cleaned_data.get('nombre_encargado_ronda')
        
        if not nombre_servicio:
            self.add_error('nombre_encargado_servicio', 'Este campo es requerido.')
        if not nombre_ronda:
            self.add_error('nombre_encargado_ronda', 'Este campo es requerido.')
        
        return cleaned_data


class OncologyRoundEntryForm(forms.ModelForm):
    """Form especial para Oncología con 3 firmas de personal del servicio."""
    
    class Meta:
        model = RoundEntry
        fields = [
            "categoria",
            "subservicio",
            "hallazgo",
            "placa_equipo",
            "orden_trabajo",
            "tiene_eventos_seguridad",
            "eventos_seguridad",
            "fuera_de_servicio",
            "nombre_encargado_servicio",
            "firma_servicio",
            "nombre_encargado_servicio_2",
            "firma_servicio_2",
            "nombre_encargado_servicio_3",
            "firma_servicio_3",
            "nombre_encargado_ronda",
            "firma_ronda",
        ]
        widgets = {
            "categoria": forms.HiddenInput(),
            "subservicio": forms.HiddenInput(),
            "hallazgo": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "placa_equipo": forms.TextInput(attrs={"class": "form-control"}),
            "orden_trabajo": forms.TextInput(attrs={"class": "form-control"}),
            "tiene_eventos_seguridad": forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            "eventos_seguridad": forms.Textarea(attrs={"rows": 2, "class": "form-control", "disabled": True}),
            "fuera_de_servicio": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_encargado_servicio": forms.TextInput(attrs={"class": "form-control", "placeholder": "Personal del servicio 1"}),
            "firma_servicio": forms.TextInput(attrs={"type": "hidden"}),
            "nombre_encargado_servicio_2": forms.TextInput(attrs={"class": "form-control", "placeholder": "Personal del servicio 2"}),
            "firma_servicio_2": forms.TextInput(attrs={"type": "hidden"}),
            "nombre_encargado_servicio_3": forms.TextInput(attrs={"class": "form-control", "placeholder": "Personal del servicio 3"}),
            "firma_servicio_3": forms.TextInput(attrs={"type": "hidden"}),
            "nombre_encargado_ronda": forms.TextInput(attrs={"class": "form-control"}),
            "firma_ronda": forms.TextInput(attrs={"type": "hidden"}),
        }

    def clean(self):
        """Validación adicional del formulario."""
        cleaned_data = super().clean()
        
        nombre_servicio_1 = cleaned_data.get('nombre_encargado_servicio')
        nombre_servicio_2 = cleaned_data.get('nombre_encargado_servicio_2')
        nombre_servicio_3 = cleaned_data.get('nombre_encargado_servicio_3')
        nombre_ronda = cleaned_data.get('nombre_encargado_ronda')
        
        if not nombre_servicio_1:
            self.add_error('nombre_encargado_servicio', 'Personal del servicio 1 es requerido.')
        if not nombre_servicio_2:
            self.add_error('nombre_encargado_servicio_2', 'Personal del servicio 2 es requerido.')
        if not nombre_servicio_3:
            self.add_error('nombre_encargado_servicio_3', 'Personal del servicio 3 es requerido.')
        if not nombre_ronda:
            self.add_error('nombre_encargado_ronda', 'Este campo es requerido.')
        
        return cleaned_data


# NOTA: SurgeryRoundForm ELIMINADO - ahora se usa DailySurgeryRoundForm
# Los registros semanales se manejan como múltiples registros diarios


class DailySurgeryRoundForm(forms.ModelForm):
    """Formulario para registros diarios de cirugía por sala y equipo"""
    
    class Meta:
        model = DailySurgeryRecord
        fields = [
            "fecha",
            "dia_semana",
            "sala",
            "equipo",
            "equipo_en_uso",
            "estado_equipo",
            "observaciones",
            "nombre_encargado_servicio",
            "nombre_encargado_ronda",
            "firma_servicio",
            "firma_ronda",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "dia_semana": forms.TextInput(attrs={"class": "form-control", "readonly": True}),
            "sala": forms.TextInput(attrs={"class": "form-control", "readonly": True}),
            "equipo": forms.TextInput(attrs={"class": "form-control", "readonly": True}),
            "equipo_en_uso": forms.CheckboxInput(attrs={"class": "form-check-input", "onchange": "toggleEquipoFields(this)"}),
            "estado_equipo": forms.Select(attrs={"class": "form-select"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "nombre_encargado_servicio": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_encargado_ronda": forms.TextInput(attrs={"class": "form-control"}),
            "firma_servicio": forms.HiddenInput(),
            "firma_ronda": forms.HiddenInput(),
        }

    def clean(self):
        """Validación: si equipo está en uso, campos son obligatorios"""
        cleaned_data = super().clean()
        equipo_en_uso = cleaned_data.get('equipo_en_uso')
        
        if equipo_en_uso:
            # Si el equipo está en uso, los demás campos son requeridos
            estado_equipo = cleaned_data.get('estado_equipo')
            nombre_servicio = cleaned_data.get('nombre_encargado_servicio')
            nombre_ronda = cleaned_data.get('nombre_encargado_ronda')
            
            if not estado_equipo:
                self.add_error('estado_equipo', "Debe seleccionar el estado del equipo cuando está en uso.")
            if not nombre_servicio:
                self.add_error('nombre_encargado_servicio', "Debe ingresar el nombre del encargado del servicio.")
            if not nombre_ronda:
                self.add_error('nombre_encargado_ronda', "Debe ingresar el nombre del encargado de la ronda.")
        
        return cleaned_data
