# Sistema de Gestión de Tareas

Un sistema web para que los jefes puedan asignar tareas a empleados y monitorear su progreso en tiempo real.

## Características

### Para Jefes:
- Configurar empresa y crear cuenta de administrador
- Crear y gestionar cuentas de empleados
- Crear y asignar tareas a empleados específicos
- Establecer prioridades (alta, media, baja) y fechas límite
- Ver el progreso de todas las tareas asignadas
- Eliminar tareas y empleados
- Ver comentarios y actualizaciones de los empleados

### Para Empleados:
- Ver sus tareas asignadas en un dashboard personalizado
- Actualizar progreso de cada tarea (0-100% con slider visual)
- Cambiar estado (pendiente, en progreso, completada)
- Agregar comentarios sobre su progreso
- Ver detalles completos de cada tarea

## Instalación

1. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

3. Abrir el navegador en `http://localhost:5000`

## Flujo de Configuración

### 1. Configuración Inicial de Empresa
- **Nombre de la Empresa**: Nombre completo de tu empresa
- **NIT**: Número de Identificación Tributaria (ej: 123.456.789-0)
- **Dirección**: Dirección física
- **Teléfono**: Número de contacto (ej: +57 1 234 5678 o 300 123 4567)
- **Email**: Email de contacto de la empresa
- **Sector**: Seleccionar el sector económico correspondiente

### 2. Creación de Cuenta de Jefe
- **Nombre Completo**: Tu nombre personal
- **Email Personal**: Tu email personal
- **Usuario**: Nombre de usuario para ingresar al sistema
- **Contraseña**: Contraseña segura (mínimo 6 caracteres)

## Sectores Disponibles

- Tecnología y Software
- Servicios Profesionales
- Manufactura
- Comercio y Retail
- Construcción
- Salud y Medicina
- Educación
- Alimentos y Bebidas
- Textil y Confecciones
- Transporte y Logística
- Servicios Financieros
- Agroindustria
- Turismo y Hotelería
- Minería y Energía
- Telecomunicaciones
- Inmobiliaria
- Consultoría
- Otros

## Gestión de Empleados

Desde el dashboard del jefe puedes:
- **Crear empleados**: Nombre, usuario, contraseña, email, departamento
- **Ver lista de empleados**: Todos los empleados activos con sus datos
- **Eliminar empleados**: Con validación de seguridad (no se pueden eliminar si tienen tareas asignadas)

## Flujo de Trabajo

1. **Configuración inicial**: El jefe configura la empresa y crea su cuenta
2. **Creación de empleados**: El jefe agrega a los empleados al sistema
3. **Asignación de tareas**: El jefe crea y asigna tareas a empleados específicos
4. **Seguimiento**: Los empleados actualizan su progreso y el jefe monitorea en tiempo real
5. **Completación**: Las tareas se marcan como completadas al llegar al 100%

## Acceso Multiusuario

- **Para uso local**: En la misma red WiFi/oficina
- **URL para empleados**: `http://[tu-ip-local]:5000`
- **Acceso móvil**: Compatible con navegadores móviles

## Datos Técnicos

- **Framework**: Flask (Python)
- **Frontend**: Bootstrap 5 + Font Awesome
- **Base de datos**: JSON local (data.json)
- **Autenticación**: Sesiones seguras de Flask
- **Persistencia**: Datos guardados localmente

## Estructura del Proyecto

```
sistema-tareas/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── data.json             # Base de datos local (se crea automáticamente)
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── configurar_empresa.html # Configuración inicial
│   ├── login.html        # Página de login
│   ├── dashboard_jefe.html    # Dashboard del jefe
│   ├── dashboard_empleado.html # Dashboard del empleado
│   ├── ver_tarea.html    # Vista detallada de tarea
│   └── inicio.html       # Página de inicio
├── iniciar_sistema.bat   # Acceso directo para iniciar
├── acceso_empleado.url   # Acceso directo para empleados
├── generar_qr.py        # Generador de QR para acceso móvil
└── README.md           # Este archivo
```

## Notas Importantes

- Los datos se guardan en `data.json` - no elimines este archivo si quieres conservar la información
- El sistema está diseñado para ser simple y fácil de personalizar
- Para producción, considera migrar a una base de datos más robusta como PostgreSQL o MySQL
- El formato NIT y los sectores están configurados para el contexto local

---
**Sistema profesional de gestión de tareas para tu empresa**
