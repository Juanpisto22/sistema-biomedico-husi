from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Inicializar la base de datos para producción'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Inicializando base de datos para producción...')
        
        # Aplicar migraciones
        self.stdout.write('📋 Aplicando migraciones...')
        call_command('migrate', '--noinput')
        
        # Crear superusuario si no existe
        if not User.objects.filter(username='Husi2025').exists():
            self.stdout.write('👑 Creando usuarios del sistema...')
            call_command('crear_usuarios')
        else:
            self.stdout.write('✅ Los usuarios ya existen')
        
        # Recopilar archivos estáticos
        self.stdout.write('📁 Recopilando archivos estáticos...')
        call_command('collectstatic', '--noinput')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Base de datos inicializada correctamente')
        )
        self.stdout.write('🔐 Credenciales de administrador:')
        self.stdout.write('   Usuario: Husi2025')
        self.stdout.write('   Contraseña: BahiaSolano123')