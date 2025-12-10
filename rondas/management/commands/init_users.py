from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from rondas.models import RoundEntry, DailySurgeryRecord



class Command(BaseCommand):
    help = 'Crear usuarios del sistema de gestión biomédica'

    def handle(self, *args, **options):
        # Crear grupos de usuarios
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        user_group, created = Group.objects.get_or_create(name='Usuarios')
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Grupos creados: Administradores, Usuarios')
            )
        
        # Obtener tipos de contenido
        round_entry_ct = ContentType.objects.get_for_model(RoundEntry)
        surgery_round_ct = ContentType.objects.get_for_model(DailySurgeryRecord)
        user_ct = ContentType.objects.get_for_model(User)
        
        # Permisos para administradores
        admin_permissions = [
            # Permisos de RoundEntry
            'add_roundentry', 'change_roundentry', 'delete_roundentry', 'view_roundentry',
            # Permisos de SurgeryRound
            'add_dailysurgeryrecord', 'change_dailysurgeryrecord', 'delete_dailysurgeryrecord', 'view_dailysurgeryrecord',
            # Permisos de usuarios
            'add_user', 'change_user', 'delete_user', 'view_user',
        ]
        
        for perm_codename in admin_permissions:
            try:
                if 'roundentry' in perm_codename:
                    perm = Permission.objects.get(codename=perm_codename, content_type=round_entry_ct)
                elif 'surgeryround' in perm_codename:
                    perm = Permission.objects.get(codename=perm_codename, content_type=surgery_round_ct)
                elif 'user' in perm_codename:
                    perm = Permission.objects.get(codename=perm_codename, content_type=user_ct)
                else:
                    continue
                admin_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permiso {perm_codename} no encontrado')
                )
        
        # Permisos para usuarios normales (solo agregar y ver)
        user_permissions = [
            'add_roundentry', 'view_roundentry',
             'add_dailysurgeryrecord', 'view_dailysurgeryrecord',
        ]
        
        for perm_codename in user_permissions:
            try:
                if 'roundentry' in perm_codename:
                    perm = Permission.objects.get(codename=perm_codename, content_type=round_entry_ct)
                elif 'surgeryround' in perm_codename:
                    perm = Permission.objects.get(codename=perm_codename, content_type=surgery_round_ct)
                else:
                    continue
                user_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permiso {perm_codename} no encontrado')
                )
        
        # Crear usuario administrador principal
        if not User.objects.filter(username='Husi2025').exists():
            admin_user = User.objects.create_user(
                username='Husi2025',
                email='admin@sanignacio.edu.co',
                password='BahiaSolano123',
                first_name='Administrador',
                last_name='Sistema',
                is_staff=True,
                is_superuser=True
            )
            admin_user.groups.add(admin_group)
            self.stdout.write(
                self.style.SUCCESS('Usuario administrador creado: admin / admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Usuario admin ya existe')
            )
        
        # Crear usuarios del personal biomédico
        usuarios_biomedicos = [
            {
                'username': 'biomedico1',
                'email': 'biomedico1@sanignacio.edu.co', 
                'password': 'bio123',
                'first_name': 'María',
                'last_name': 'González',
            },
            {
                'username': 'biomedico2',
                'email': 'biomedico2@sanignacio.edu.co',
                'password': 'bio123', 
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
            },
            {
                'username': 'biomedico3',
                'email': 'biomedico3@sanignacio.edu.co',
                'password': 'bio123',
                'first_name': 'Ana',
                'last_name': 'Martínez',
            },
            {
                'username': 'supervisor',
                'email': 'supervisor@sanignacio.edu.co',
                'password': 'super123',
                'first_name': 'Luis',
                'last_name': 'Supervisor',
            }
        ]
        
        for user_data in usuarios_biomedicos:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(**user_data)
                if user_data['username'] == 'supervisor':
                    user.groups.add(admin_group)  # Supervisor tiene permisos de admin
                else:
                    user.groups.add(user_group)   # Personal biomédico normal
                
                self.stdout.write(
                    self.style.SUCCESS(f'Usuario creado: {user_data["username"]} / {user_data["password"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Usuario {user_data["username"]} ya existe')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== USUARIOS CREADOS ===')
        )
        self.stdout.write('👑 ADMINISTRADORES (pueden eliminar y descargar):')
        self.stdout.write('  • Husi2025 / BahiaSolano123 (Super administrador)')
        self.stdout.write('  • supervisor / super123 (Supervisor biomédico)')
        self.stdout.write('\n👤 USUARIOS NORMALES (solo crear y ver rondas):')
        self.stdout.write('  • biomedico1 / bio123 (María González)')
        self.stdout.write('  • biomedico2 / bio123 (Carlos Rodríguez)')
        self.stdout.write('  • biomedico3 / bio123 (Ana Martínez)')
        self.stdout.write(
            self.style.SUCCESS('\n✅ Sistema de usuarios configurado correctamente')
        )