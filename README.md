# 🏥 Sistema de Gestión Biomédica - Hospital Universitario San Ignacio

Sistema web para gestión de rondas biomédicas con firmas digitales, reportes PDF/Excel y control de acceso por roles.

## 🚀 Despliegue en Railway

### Paso 1: Preparar Repository
1. Crear cuenta en [GitHub](https://github.com)
2. Crear nuevo repositorio público
3. Subir este código al repositorio

### Paso 2: Desplegar en Railway
1. Crear cuenta en [Railway](https://railway.app)
2. Conectar cuenta de GitHub
3. Seleccionar "Deploy from GitHub repo"
4. Elegir el repositorio creado
5. Railway detectará automáticamente que es un proyecto Django

### Paso 3: Configurar Base de Datos
1. En Railway, agregar servicio PostgreSQL
2. Las variables de entorno se configuran automáticamente

### Paso 4: Configurar Variables de Entorno (Opcional)
- `SECRET_KEY`: Clave secreta de Django (se genera automáticamente)
- `DEBUG`: Establecer en `False` para producción

## 🔐 Credenciales por Defecto

### Administrador Principal
- **Usuario:** Husi2025
- **Contraseña:** BahiaSolano123

### Usuarios Normales
- biomedico1 / bio123
- biomedico2 / bio123  
- biomedico3 / bio123
- supervisor / super123

## 📱 Funcionalidades

- ✅ Rondas de servicios biomédicos
- ✅ Rondas de cirugía con programación semanal
- ✅ Firmas digitales con canvas HTML5
- ✅ Exportación PDF/Excel
- ✅ Control de acceso por roles
- ✅ Historial completo con filtros
- ✅ Indicadores y estadísticas
- ✅ Responsivo (móviles/tablets)

## 🛠️ Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear usuarios
python manage.py crear_usuarios

# Ejecutar servidor
python manage.py runserver
```

## 📄 Licencia

Desarrollado para Hospital Universitario San Ignacio - 2025