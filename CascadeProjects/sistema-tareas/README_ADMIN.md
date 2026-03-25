# 🔧 Panel de Administrador Maestro

## 🎯 Descripción General

El sistema ahora incluye un **panel de administrador maestro** separado que permite gestionar múltiples empresas de forma independiente. Cada empresa tiene su propio conjunto de usuarios y tareas, con acceso individualizado.

## 🏗️ Arquitectura Multi-Empresa

### Estructura de Datos
```
data.json
├── admin_maestro          # Credenciales del administrador
├── empresas              # Contenedor de todas las empresas
│   ├── emp_1            # Empresa 1
│   │   ├── nombre        # Datos de la empresa
│   │   ├── nit
│   │   ├── usuarios      # Usuarios de esta empresa
│   │   └── tareas        # Tareas de esta empresa
│   └── emp_2            # Empresa 2
└── global_config          # Configuración global del sistema
```

## 🔑 Acceso al Sistema

### 1. Administrador Maestro
- **URL:** `http://localhost:5000/admin`
- **Credenciales por defecto:**
  - Usuario: `admin`
  - Contraseña: `superadmin123`

### 2. Empresas (Acceso Individual)
- **URL:** `http://localhost:5000/empresa/[ID]/login`
- Cada empresa tiene su propia página de login personalizada

## 🎛️ Funcionalidades del Administrador

### Dashboard Principal
- **Estadísticas generales:** Total empresas, activas, usuarios, tareas
- **Tabla de empresas:** Vista completa con todos los datos
- **Acciones rápidas:** Crear nueva empresa

### Gestión de Empresas
- **Crear empresa:** Formulario completo con datos básicos
- **Ver detalles:** Información completa de empresa, usuarios y tareas
- **Suspender/Activar:** Control de acceso de empresas
- **Eliminar:** Remoción permanente con confirmación

### Creación de Empresas con Pruebas
- **Opción automática:** Checkbox para crear usuarios de prueba
- **Usuarios de prueba:** 2 empleados con credenciales predefinidas
- **Tarea de prueba:** 1 tarea asignada para demostración
- **Credenciales de prueba:**
  - Usuario: `emp_prueba1`, Contraseña: `test123`
  - Usuario: `emp_prueba2`, Contraseña: `test123`

## 📊 Características Técnicas

### Multi-Tenant
- **Aislamiento completo:** Cada empresa opera independientemente
- **URLs únicas:** Cada empresa tiene su propio acceso
- **Datos separados:** Usuarios y tareas no se mezclan entre empresas
- **Gestión centralizada:** El administrador controla todo desde un panel

### Seguridad
- **Roles jerárquicos:** Admin maestro > Jefe > Empleado
- **Sesiones segregadas:** Por empresa y usuario
- **Validaciones:** Protección contra accesos no autorizados
- **Control de estado:** Empresas pueden ser suspendidas

### Funcionalidades
- **Estadísticas en tiempo real:** Contadores de uso
- **Copiar URLs:** Acceso rápido para compartir credenciales
- **Exportación de datos:** Estructura JSON para migraciones
- **Logging:** Registro de acciones importantes

## 🚀 Flujo de Trabajo

### Para el Administrador
1. **Iniciar sesión** en `/admin` con credenciales de administrador
2. **Crear empresas** desde el dashboard
3. **Configurar usuarios** de prueba para validación
4. **Compartir URLs** de acceso con los jefes de cada empresa
5. **Monitorear** el uso y estado de todas las empresas

### Para los Jefes de Empresa
1. **Recibir URL** específica de su empresa: `/empresa/[ID]/login`
2. **Iniciar sesión** con credenciales proporcionadas
3. **Gestionar empleados** y tareas de su empresa únicamente
4. **Operar independientemente** de otras empresas

## 🎯 Ventajas del Sistema

### Para el Administrador
- **Control centralizado:** Todas las empresas desde un panel
- **Gestión masiva:** Crear múltiples empresas rápidamente
- **Monitoreo global:** Visión completa del uso del sistema
- **Pruebas automatizadas:** Creación de entornos de prueba con un clic

### Para las Empresas
- **Aislamiento:** Seguridad y privacidad de datos
- **Acceso dedicado:** URL propia y personalizada
- **Independencia:** Operación sin interferencias
- **Escalabilidad:** Fácil añadir más empresas

## 🔧 Configuración Técnica

### Base de Datos
```json
{
  "admin_maestro": {
    "usuario": "admin",
    "password": "superadmin123"
  },
  "empresas": {
    "emp_1": {
      "nombre": "Empresa A",
      "nit": "123.456.789-0",
      "estado": "activo",
      "usuarios": {...},
      "tareas": [...]
    }
  },
  "global_config": {
    "modo_mantenimiento": false,
    "version": "1.0.0"
  }
}
```

### URLs del Sistema
- **Principal:** `http://localhost:5000/`
- **Administrador:** `http://localhost:5000/admin`
- **Empresa:** `http://localhost:5000/empresa/[ID]/login`

## 📱 Acceso Móvil

- **Diseño responsivo:** Compatible con dispositivos móviles
- **URLs compartibles:** Las URLs de empresa funcionan en móviles
- **Panel admin:** Accesible desde tabletas y móviles

## 🔮 Funcionalidades Futuras

- **Edición de empresas:** Modificar datos básicos
- **Respaldo automático:** Copias de seguridad programadas
- **Notificaciones:** Alertas para administradores
- **API REST:** Integración con sistemas externos
- **Multi-idioma:** Soporte para diferentes idiomas

---
**Sistema Multi-Empresa Profesional y Escalable** 🚀
