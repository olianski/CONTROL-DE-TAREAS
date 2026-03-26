from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_sistema_tareas'

# Archivo para persistencia de datos
DATA_FILE = 'data.json'

@app.route('/static/evidencias/<path:filename>')
def serve_evidencia(filename):
    return send_from_directory('static/evidencias', filename)

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'admin_maestro': {
            'usuario': 'admin',
            'password': 'superadmin123',
            'email': 'admin@sistema.com',
            'nombre': 'Administrador del Sistema'
        },
        'empresas': {},
        'global_config': {
            'modo_mantenimiento': False,
            'version': '2.0.0',
            'nombre_sistema': 'TaskFlow Pro',
            'moneda': 'USD'
        },
        'planes_suscripcion': {
            'basico': {
                'nombre': 'Plan Básico',
                'precio': 10,
                'max_usuarios': 5,
                'max_tareas': 50,
                'caracteristicas': ['Hasta 5 empleados', 'Hasta 50 tareas', 'Soporte por email']
            },
            'profesional': {
                'nombre': 'Plan Profesional',
                'precio': 25,
                'max_usuarios': 20,
                'max_tareas': 200,
                'caracteristicas': ['Hasta 20 empleados', 'Hasta 200 tareas', 'Soporte prioritario', 'Reportes avanzados']
            },
            'enterprise': {
                'nombre': 'Plan Enterprise',
                'precio': 50,
                'max_usuarios': 100,
                'max_tareas': 1000,
                'caracteristicas': ['Hasta 100 empleados', 'Tareas ilimitadas', 'Soporte 24/7', 'API access', 'Personalización']
            }
        },
        'pagos': [],
        'notificaciones': []
    }

def guardar_datos(datos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    if 'admin_maestro' in session:
        return redirect(url_for('dashboard_admin'))
    
    if 'usuario' in session and 'empresa_id' in session:
        if session['rol'] == 'jefe':
            return redirect(url_for('dashboard_jefe'))
        else:
            return redirect(url_for('dashboard_empleado'))
    
    return render_template('inicio.html')

@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_auth():
    usuario = request.form['usuario']
    password = request.form['password']
    
    datos = cargar_datos()
    
    if (usuario == datos['admin_maestro']['usuario'] and 
        password == datos['admin_maestro']['password']):
        session['admin_maestro'] = True
        session['admin_usuario'] = usuario
        return redirect(url_for('dashboard_admin'))
    else:
        flash('Credenciales de administrador incorrectas')
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def dashboard_admin():
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    empresas = datos.get('empresas', {})
    
    # Calcular estadísticas mejoradas
    stats = {
        'total_empresas': len(empresas),
        'empresas_activas': len([e for e in empresas.values() if e.get('estado', 'activo') == 'activo']),
        'empresas_suspendidas': len([e for e in empresas.values() if e.get('estado') == 'suspendido']),
        'total_usuarios': sum(len(e.get('usuarios', {})) for e in empresas.values()),
        'total_tareas': sum(len(e.get('tareas', [])) for e in empresas.values()),
        'ingresos_mensuales': sum(e.get('suscripcion', {}).get('precio_mensual', 0) for e in empresas.values() if e.get('suscripcion', {}).get('estado') == 'activa'),
        'pagos_pendientes': len([p for p in datos.get('pagos', []) if p.get('estado') == 'pendiente']),
        'notificaciones_no_leidas': len([n for n in datos.get('notificaciones', []) if not n.get('leida', True)])
    }
    
    # Empresas con pagos próximos
    hoy = datetime.now()
    empresas_pago_proximo = []
    for emp_id, empresa in empresas.items():
        if 'suscripcion' in empresa:
            fecha_pago = datetime.strptime(empresa['suscripcion']['fecha_proximo_pago'], '%Y-%m-%d')
            dias_restantes = (fecha_pago - hoy).days
            if 0 <= dias_restantes <= 7:
                empresas_pago_proximo.append({
                    'id': emp_id,
                    'nombre': empresa['nombre'],
                    'dias_restantes': dias_restantes,
                    'monto': empresa['suscripcion']['precio_mensual']
                })
    
    return render_template('dashboard_admin.html', 
                         empresas=empresas, 
                         stats=stats,
                         admin_usuario=session.get('admin_usuario'),
                         empresas_pago_proximo=empresas_pago_proximo,
                         notificaciones=datos.get('notificaciones', [])[:5])

@app.route('/admin/crear_empresa', methods=['GET', 'POST'])
def crear_empresa():
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        datos = cargar_datos()
        empresa_id = f"emp_{len(datos['empresas']) + 1}"
        
        # Datos de la empresa con suscripción
        plan_seleccionado = request.form['plan_suscripcion']
        planes = cargar_datos()['planes_suscripcion']
        plan_info = planes.get(plan_seleccionado, planes['basico'])
        
        empresa = {
            'nombre': request.form['nombre_empresa'],
            'nit': request.form['nit'],
            'direccion': request.form['direccion'],
            'telefono': request.form['telefono'],
            'email': request.form['email'],
            'sector': request.form['sector'],
            'estado': 'activo',
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'creado_por': session.get('admin_usuario'),
            'suscripcion': {
                'plan': plan_seleccionado,
                'nombre_plan': plan_info['nombre'],
                'precio_mensual': plan_info['precio'],
                'max_usuarios': plan_info['max_usuarios'],
                'max_tareas': plan_info['max_tareas'],
                'fecha_inicio': datetime.now().strftime('%Y-%m-%d'),
                'fecha_proximo_pago': datetime.now().strftime('%Y-%m-%d'),
                'estado': 'activa',
                'metodo_pago': 'pendiente',
                'dias_gracia': 7
            },
            'usuarios': {},
            'tareas': [],
            'estadisticas': {
                'tareas_completadas': 0,
                'tareas_pendientes': 0,
                'ultima_actividad': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # Crear usuario jefe para la empresa
        jefe_usuario = request.form['jefe_usuario']
        empresa['usuarios'][jefe_usuario] = {
            'password': request.form['jefe_password'],
            'rol': 'jefe',
            'nombre': request.form['jefe_nombre'],
            'email': request.form.get('jefe_email', ''),
            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Crear usuarios de prueba si se solicita
        if request.form.get('crear_prueba') == 'si':
            # Empleado de prueba 1
            empresa['usuarios']['emp_prueba1'] = {
                'password': 'test123',
                'rol': 'empleado',
                'nombre': 'Empleado Prueba 1',
                'email': 'test1@empresa.com',
                'departamento': 'Pruebas',
                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'es_prueba': True
            }
            
            # Empleado de prueba 2
            empresa['usuarios']['emp_prueba2'] = {
                'password': 'test123',
                'rol': 'empleado',
                'nombre': 'Empleado Prueba 2',
                'email': 'test2@empresa.com',
                'departamento': 'Calidad',
                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'es_prueba': True
            }
            
            # Tarea de prueba
            empresa['tareas'].append({
                'id': 1,
                'titulo': 'Tarea de Prueba - Configuración del Sistema',
                'descripcion': 'Esta es una tarea de prueba para verificar el funcionamiento del sistema. Por favor, actualiza el progreso y marca como completada.',
                'asignado_a': 'emp_prueba1',
                'prioridad': 'media',
                'estado': 'pendiente',
                'progreso': 0,
                'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'fecha_limite': '',
                'comentarios': [],
                'es_prueba': True
            })
        
        datos['empresas'][empresa_id] = empresa
        
        # Registrar pago inicial
        pago = {
            'id': len(datos.get('pagos', [])) + 1,
            'empresa_id': empresa_id,
            'empresa_nombre': empresa['nombre'],
            'monto': plan_info['precio'],
            'concepto': f'Suscripción inicial - {plan_info["nombre"]}',
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metodo': 'pendiente',
            'estado': 'pendiente',
            'periodo': f'{datetime.now().strftime("%Y-%m")}'
        }
        
        if 'pagos' not in datos:
            datos['pagos'] = []
        datos['pagos'].append(pago)
        
        # Crear notificación para el admin
        notificacion = {
            'id': len(datos.get('notificaciones', [])) + 1,
            'titulo': f'Nueva empresa registrada: {empresa["nombre"]}',
            'mensaje': f'Se ha registrado una nueva empresa con plan {plan_info["nombre"]}. Esperando pago de ${plan_info["precio"]} USD.',
            'tipo': 'nueva_empresa',
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'leida': False,
            'empresa_id': empresa_id
        }
        
        if 'notificaciones' not in datos:
            datos['notificaciones'] = []
        datos['notificaciones'].append(notificacion)
        
        guardar_datos(datos)
        
        flash(f'Empresa "{empresa["nombre"]}" creada exitosamente')
        return redirect(url_for('dashboard_admin'))
    
    return render_template('crear_empresa.html')

@app.route('/admin/gestion_pagos')
def gestion_pagos():
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    pagos = datos.get('pagos', [])
    empresas = datos.get('empresas', {})
    
    # Filtrar pagos por estado
    pagos_pendientes = [p for p in pagos if p.get('estado') == 'pendiente']
    pagos_completados = [p for p in pagos if p.get('estado') == 'completado']
    
    return render_template('gestion_pagos.html', 
                         pagos=pagos,
                         pagos_pendientes=pagos_pendientes,
                         pagos_completados=pagos_completados,
                         empresas=empresas)

@app.route('/admin/confirmar_pago/<pago_id>', methods=['POST'])
def confirmar_pago(pago_id):
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    pago = next((p for p in datos.get('pagos', []) if str(p['id']) == pago_id), None)
    
    if pago:
        pago['estado'] = 'completado'
        pago['metodo'] = request.form.get('metodo_pago', 'transferencia')
        pago['fecha_confirmacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Actualizar estado de suscripción de la empresa
        empresa_id = pago['empresa_id']
        if empresa_id in datos['empresas']:
            empresa = datos['empresas'][empresa_id]
            empresa['suscripcion']['estado'] = 'activa'
            empresa['suscripcion']['metodo_pago'] = pago['metodo']
            
            # Actualizar fecha del próximo pago
            fecha_actual = datetime.now()
            # Simple: agregar 30 días al pago actual
            from datetime import timedelta
            proximo_pago = fecha_actual + timedelta(days=30)
            empresa['suscripcion']['fecha_proximo_pago'] = proximo_pago.strftime('%Y-%m-%d')
            
            # Reactivar empresa si estaba suspendida
            if empresa.get('estado') == 'suspendido':
                empresa['estado'] = 'activo'
        
        guardar_datos(datos)
        flash('Pago confirmado exitosamente')
    
    return redirect(url_for('gestion_pagos'))

@app.route('/admin/acceder_empresa/<empresa_id>')
def acceder_empresa(empresa_id):
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    if empresa_id not in datos['empresas']:
        flash('Empresa no encontrada')
        return redirect(url_for('dashboard_admin'))
    
    empresa = datos['empresas'][empresa_id]
    
    # Encontrar al usuario jefe de la empresa
    jefe_usuario = None
    for usuario, datos_usuario in empresa['usuarios'].items():
        if datos_usuario.get('rol') == 'jefe':
            jefe_usuario = usuario
            break
    
    if jefe_usuario:
        # Crear sesión como el jefe (modo supervisor)
        session['usuario'] = jefe_usuario
        session['rol'] = 'jefe'
        session['nombre'] = empresa['usuarios'][jefe_usuario]['nombre']
        session['empresa_id'] = empresa_id
        session['empresa_nombre'] = empresa['nombre']
        session['modo_supervisor'] = True  # Indicador que es admin en modo supervisor
        
        flash(f'Accediendo como supervisor a: {empresa["nombre"]}')
        return redirect(url_for('dashboard_jefe'))
    
    flash('No se encontró un usuario jefe en esta empresa')
    return redirect(url_for('dashboard_admin'))

def verificar_suscripciones():
    """Función para verificar y suspender empresas con pagos vencidos"""
    datos = cargar_datos()
    hoy = datetime.now()
    empresas_suspendidas = []
    
    for empresa_id, empresa in datos['empresas'].items():
        if 'suscripcion' in empresa and empresa.get('estado') != 'suspendido':
            fecha_pago = datetime.strptime(empresa['suscripcion']['fecha_proximo_pago'], '%Y-%m-%d')
            dias_vencidos = (hoy - fecha_pago).days
            
            if dias_vencidos > 0:
                if dias_vencidos <= empresa['suscripcion']['dias_gracia']:
                    # Aún en período de gracia
                    empresa['suscripcion']['estado'] = 'gracia'
                else:
                    # Suspender por no pago
                    empresa['estado'] = 'suspendido'
                    empresa['suscripcion']['estado'] = 'vencida'
                    empresas_suspendidas.append(empresa['nombre'])
                    
                    # Crear notificación
                    notificacion = {
                        'id': len(datos.get('notificaciones', [])) + 1,
                        'titulo': f'Empresa suspendida: {empresa["nombre"]}',
                        'mensaje': f'La empresa ha sido suspendida por falta de pago. Hace {dias_vencidos} días vencida.',
                        'tipo': 'suspension_auto',
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'leida': False,
                        'empresa_id': empresa_id
                    }
                    
                    if 'notificaciones' not in datos:
                        datos['notificaciones'] = []
                    datos['notificaciones'].append(notificacion)
    
    if empresas_suspendidas:
        guardar_datos(datos)
    
    return empresas_suspendidas

@app.route('/admin/verificar_suscripciones')
def verificar_suscripciones_route():
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    suspendidas = verificar_suscripciones()
    
    if suspendidas:
        flash(f'Se han suspendido {len(suspendidas)} empresas por falta de pago: {", ".join(suspendidas)}')
    else:
        flash('No hay empresas con pagos vencidos')
    
    return redirect(url_for('dashboard_admin'))

def verificar_fechas_vencidas():
    """Función para verificar tareas con fechas límite vencidas y generar alertas"""
    datos = cargar_datos()
    hoy = datetime.now()
    alertas_generadas = []
    
    for empresa_id, empresa in datos['empresas'].items():
        if empresa.get('estado') != 'activo':
            continue
            
        # Inicializar notificaciones si no existen
        if 'notificaciones' not in empresa:
            empresa['notificaciones'] = []
            
        for tarea in empresa.get('tareas', []):
            if not tarea.get('fecha_limite'):
                continue
                
            try:
                fecha_limite = datetime.strptime(tarea['fecha_limite'], '%Y-%m-%d')
                
                # Verificar si la tarea está vencida y no está completada
                if fecha_limite < hoy and tarea['estado'] not in ['completada', 'cancelada']:
                    # Generar alerta para el empleado
                    alerta_empleado = {
                        'id': len(empresa['notificaciones']) + 1,
                        'tipo': 'tarea_vencida',
                        'titulo': f'⚠️ Tarea Vencida: {tarea["titulo"]}',
                        'mensaje': f'La tarea "{tarea["titulo"]}" debía completarse el {tarea["fecha_limite"]}. Contacta a tu supervisor.',
                        'tarea_id': tarea['id'],
                        'usuario_destino': tarea['asignado_a'],
                        'fecha': hoy.strftime('%Y-%m-%d %H:%M:%S'),
                        'leida': False,
                        'urgencia': 'alta'
                    }
                    
                    # Verificar si ya existe una alerta similar para esta tarea
                    alerta_existente = any(
                        n for n in empresa['notificaciones'] 
                        if n['tipo'] == 'tarea_vencida' and 
                           n['tarea_id'] == tarea['id'] and 
                           n['usuario_destino'] == tarea['asignado_a'] and
                           not n['leida']
                    )
                    
                    if not alerta_existente:
                        empresa['notificaciones'].append(alerta_empleado)
                        alertas_generadas.append(f"{empresa['nombre']} - {tarea['titulo']}")
                    
                    # Generar notificación para el jefe
                    alerta_jefe = {
                        'id': len(empresa['notificaciones']) + 2,
                        'tipo': 'tarea_empleado_vencida',
                        'titulo': f'🚨 Tarea de Empleado Vencida',
                        'mensaje': f'La tarea "{tarea["titulo"]}" asignada a {empresa["usuarios"][tarea["asignado_a"]]["nombre"]} está vencida desde {tarea["fecha_limite"]}.',
                        'tarea_id': tarea['id'],
                        'usuario_destino': 'jefe',
                        'fecha': hoy.strftime('%Y-%m-%d %H:%M:%S'),
                        'leida': False,
                        'urgencia': 'alta'
                    }
                    
                    # Verificar si ya existe notificación para el jefe
                    jefe_notificacion_existente = any(
                        n for n in empresa['notificaciones'] 
                        if n['tipo'] == 'tarea_empleado_vencida' and 
                           n['tarea_id'] == tarea['id'] and 
                           n['usuario_destino'] == 'jefe' and
                           not n['leida']
                    )
                    
                    if not jefe_notificacion_existente:
                        empresa['notificaciones'].append(alerta_jefe)
                        
                # Verificar tareas próximas a vencer (2 días antes)
                elif fecha_limite - timedelta(days=2) <= hoy < fecha_limite and tarea['estado'] not in ['completada', 'cancelada']:
                    # Generar alerta de proximidad para el empleado
                    alerta_proximidad = {
                        'id': len(empresa['notificaciones']) + 3,
                        'tipo': 'tarea_por_vencer',
                        'titulo': f'⏰ Tarea por Vencer: {tarea["titulo"]}',
                        'mensaje': f'La tarea "{tarea["titulo"]}" vence el {tarea["fecha_limite"]}. ¡Apúrate a completarla!',
                        'tarea_id': tarea['id'],
                        'usuario_destino': tarea['asignado_a'],
                        'fecha': hoy.strftime('%Y-%m-%d %H:%M:%S'),
                        'leida': False,
                        'urgencia': 'media'
                    }
                    
                    # Verificar si ya existe alerta de proximidad
                    proximidad_existente = any(
                        n for n in empresa['notificaciones'] 
                        if n['tipo'] == 'tarea_por_vencer' and 
                           n['tarea_id'] == tarea['id'] and 
                           n['usuario_destino'] == tarea['asignado_a'] and
                           not n['leida']
                    )
                    
                    if not proximidad_existente:
                        empresa['notificaciones'].append(alerta_proximidad)
                        
            except ValueError:
                continue
    
    if alertas_generadas:
        guardar_datos(datos)
    
    return alertas_generadas

def verificar_tareas_empleado(empresa_id, empleado_id):
    """Función para verificar el estado de tareas de un empleado y generar alertas para el jefe"""
    datos = cargar_datos()
    empresa = datos['empresas'].get(empresa_id)
    if not empresa:
        return []
    
    hoy = datetime.now()
    alertas_jefe = []
    
    # Inicializar notificaciones si no existen
    if 'notificaciones' not in empresa:
        empresa['notificaciones'] = []
    
    # Obtener tareas del empleado
    tareas_empleado = [t for t in empresa.get('tareas', []) if t['asignado_a'] == empleado_id]
    
    # Verificar si tiene muchas tareas pendientes (más de 5)
    tareas_pendientes = [t for t in tareas_empleado if t['estado'] not in ['completada', 'cancelada']]
    if len(tareas_pendientes) > 5:
        alerta_acumulacion = {
            'id': len(empresa['notificaciones']) + 1,
            'tipo': 'acumulacion_tareas',
            'titulo': f'📊 Acumulación de Tareas',
            'mensaje': f'El empleado {empresa["usuarios"][empleado_id]["nombre"]} tiene {len(tareas_pendientes)} tareas pendientes.',
            'empleado_id': empleado_id,
            'usuario_destino': 'jefe',
            'fecha': hoy.strftime('%Y-%m-%d %H:%M:%S'),
            'leida': False,
            'urgencia': 'media'
        }
        
        # Verificar si ya existe alerta de acumulación
        acumulacion_existente = any(
            n for n in empresa['notificaciones'] 
            if n['tipo'] == 'acumulacion_tareas' and 
               n['empleado_id'] == empleado_id and 
               n['usuario_destino'] == 'jefe' and
               not n['leida']
        )
        
        if not acumulacion_existente:
            empresa['notificaciones'].append(alerta_acumulacion)
            alertas_jefe.append(f"Acumulación de tareas: {empresa['usuarios'][empleado_id]['nombre']}")
    
    # Verificar tareas vencidas del empleado
    tareas_vencidas = [
        t for t in tareas_empleado 
        if t.get('fecha_limite') and 
           datetime.strptime(t['fecha_limite'], '%Y-%m-%d') < hoy and 
           t['estado'] not in ['completada', 'cancelada']
    ]
    
    if tareas_vencidas:
        alerta_vencidas = {
            'id': len(empresa['notificaciones']) + 2,
            'tipo': 'tareas_vencidas_empleado',
            'titulo': f'🚨 Tareas Vencidas del Empleado',
            'mensaje': f'El empleado {empresa["usuarios"][empleado_id]["nombre"]} tiene {len(tareas_vencidas)} tareas vencidas.',
            'empleado_id': empleado_id,
            'usuario_destino': 'jefe',
            'fecha': hoy.strftime('%Y-%m-%d %H:%M:%S'),
            'leida': False,
            'urgencia': 'alta'
        }
        
        # Verificar si ya existe alerta de tareas vencidas
        vencidas_existente = any(
            n for n in empresa['notificaciones'] 
            if n['tipo'] == 'tareas_vencidas_empleado' and 
               n['empleado_id'] == empleado_id and 
               n['usuario_destino'] == 'jefe' and
               not n['leida']
        )
        
        if not vencidas_existente:
            empresa['notificaciones'].append(alerta_vencidas)
            alertas_jefe.append(f"Tareas vencidas: {empresa['usuarios'][empleado_id]['nombre']}")
    
    if alertas_jefe:
        guardar_datos(datos)
    
    return alertas_jefe

@app.route('/admin/suspender_empresa/<empresa_id>')
def suspender_empresa(empresa_id):
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    if empresa_id in datos['empresas']:
        datos['empresas'][empresa_id]['estado'] = 'suspendido'
        guardar_datos(datos)
        flash('Empresa suspendida exitosamente')
    
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/activar_empresa/<empresa_id>')
def activar_empresa(empresa_id):
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    if empresa_id in datos['empresas']:
        datos['empresas'][empresa_id]['estado'] = 'activo'
        guardar_datos(datos)
        flash('Empresa activada exitosamente')
    
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/eliminar_empresa/<empresa_id>')
def eliminar_empresa(empresa_id):
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    if empresa_id in datos['empresas']:
        nombre_empresa = datos['empresas'][empresa_id]['nombre']
        del datos['empresas'][empresa_id]
        guardar_datos(datos)
        flash(f'Empresa "{nombre_empresa}" eliminada exitosamente')
    
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/empresa/<empresa_id>/login', methods=['GET', 'POST'])
def empresa_login(empresa_id):
    datos = cargar_datos()
    
    if empresa_id not in datos['empresas']:
        flash('Empresa no encontrada')
        return redirect(url_for('index'))
    
    empresa = datos['empresas'][empresa_id]
    
    if empresa.get('estado') != 'activo':
        flash('Esta empresa está suspendida. Contacte al administrador.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        if usuario in empresa['usuarios'] and empresa['usuarios'][usuario]['password'] == password:
            session['usuario'] = usuario
            session['rol'] = empresa['usuarios'][usuario]['rol']
            session['nombre'] = empresa['usuarios'][usuario]['nombre']
            session['empresa_id'] = empresa_id
            session['empresa_nombre'] = empresa['nombre']
            
            if session['rol'] == 'jefe':
                return redirect(url_for('dashboard_jefe'))
            else:
                return redirect(url_for('dashboard_empleado'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('empresa_login.html', empresa=empresa, empresa_id=empresa_id)

@app.route('/login')
def login():
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Si está en modo supervisor, volver al panel de admin
    if session.get('modo_supervisor'):
        session.clear()
        session['admin_maestro'] = True
        session['admin_usuario'] = 'admin'
        return redirect(url_for('dashboard_admin'))
    
    # Guardar información de la empresa antes de limpiar la sesión
    empresa_id = session.get('empresa_id')
    session.clear()
    
    # Si venía de una empresa, redirigir al login de esa empresa
    if empresa_id:
        return redirect(url_for('empresa_login', empresa_id=empresa_id))
    
    # Si no, redirigir a la página principal
    return redirect(url_for('index'))

@app.route('/admin/volver_panel')
def volver_panel_admin():
    """Volver al panel de administrador desde modo supervisor"""
    session.clear()
    session['admin_maestro'] = True
    session['admin_usuario'] = 'admin'
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/notificaciones')
def notificaciones_admin():
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    notificaciones = datos.get('notificaciones', [])
    
    # Marcar todas como leídas
    for notif in notificaciones:
        notif['leida'] = True
    
    guardar_datos(datos)
    
    return render_template('notificaciones_admin.html', 
                         notificaciones=notificaciones,
                         admin_usuario=session.get('admin_usuario'))

@app.route('/dashboard_jefe')
def dashboard_jefe():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'jefe':
        return redirect(url_for('index'))
    
    # Ejecutar verificación automática de fechas vencidas
    verificar_fechas_vencidas()
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    tareas = empresa['tareas']
    usuarios = {k: v for k, v in empresa['usuarios'].items() if v['rol'] == 'empleado'}
    
    # Verificar límites del plan
    suscripcion = empresa.get('suscripcion', {})
    limite_usuarios = suscripcion.get('max_usuarios', 5)
    limite_tareas = suscripcion.get('max_tareas', 50)
    
    # Asegurar que las estadísticas existan
    if 'estadisticas' not in empresa:
        empresa['estadisticas'] = {
            'tareas_pendientes': 0,
            'tareas_en_progreso': 0,
            'tareas_completadas': 0,
            'usuarios_activos': 0,
            'ultima_actividad': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        guardar_datos(datos)
    
    # Filtros
    filtro_estado = request.args.get('filtro_estado', '')
    filtro_prioridad = request.args.get('filtro_prioridad', '')
    filtro_empleado = request.args.get('filtro_empleado', '')
    
    # Aplicar filtros
    tareas_filtradas = tareas
    if filtro_estado:
        tareas_filtradas = [t for t in tareas_filtradas if t.get('estado') == filtro_estado]
    if filtro_prioridad:
        tareas_filtradas = [t for t in tareas_filtradas if t.get('prioridad') == filtro_prioridad]
    if filtro_empleado:
        tareas_filtradas = [t for t in tareas_filtradas if t.get('asignado_a') == filtro_empleado]
    
    # Estadísticas
    notificaciones_jefe = [
        n for n in empresa.get('notificaciones', []) 
        if n['usuario_destino'] == 'jefe' and not n['leida']
    ]
    
    stats = {
        'total_tareas': len(tareas),
        'tareas_pendientes': len([t for t in tareas if t.get('estado') == 'pendiente']),
        'tareas_en_progreso': len([t for t in tareas if t.get('estado') == 'en_progreso']),
        'tareas_completadas': len([t for t in tareas if t.get('estado') == 'completada']),
        'tareas_vencidas': len([t for t in tareas if t.get('estado') == 'vencida']),
        'usuarios_activos': len(usuarios),
        'notificaciones_no_leidas': len(notificaciones_jefe)
    }
    
    return render_template('dashboard_jefe.html', 
                         tareas=tareas_filtradas,
                         todas_tareas=tareas,
                         usuarios=usuarios,
                         stats=stats,
                         nombre=session['nombre'],
                         empresa_nombre=session['empresa_nombre'],
                         suscripcion=suscripcion,
                         limite_usuarios=limite_usuarios,
                         limite_tareas=limite_tareas,
                         filtro_estado=filtro_estado,
                         filtro_prioridad=filtro_prioridad,
                         filtro_empleado=filtro_empleado,
                         modo_supervisor=session.get('modo_supervisor', False))

@app.route('/notificaciones_jefe')
def notificaciones_jefe():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'jefe':
        return redirect(url_for('index'))
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    
    # Obtener notificaciones del jefe
    notificaciones_jefe = [
        n for n in empresa.get('notificaciones', []) 
        if n['usuario_destino'] == 'jefe'
    ]
    
    # Marcar notificaciones como leídas
    for notificacion in notificaciones_jefe:
        if not notificacion['leida']:
            notificacion['leida'] = True
    
    guardar_datos(datos)
    
    return render_template('notificaciones_jefe.html', 
                         notificaciones=notificaciones_jefe,
                         nombre=session['nombre'],
                         empresa_nombre=session['empresa_nombre'])

@app.route('/dashboard_empleado')
def dashboard_empleado():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'empleado':
        return redirect(url_for('index'))
    
    # Ejecutar verificación automática de fechas vencidas
    verificar_fechas_vencidas()
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    tareas_empleado = [t for t in empresa['tareas'] if t['asignado_a'] == session['usuario']]
    
    # Obtener notificaciones no leídas del empleado
    notificaciones_empleado = [
        n for n in empresa.get('notificaciones', []) 
        if n['usuario_destino'] == session['usuario'] and not n['leida']
    ]
    
    return render_template('dashboard_empleado.html', 
                         tareas=tareas_empleado,
                         nombre=session['nombre'],
                         empresa_nombre=session['empresa_nombre'],
                         notificaciones_no_leidas=len(notificaciones_empleado))

@app.route('/notificaciones_empleado')
def notificaciones_empleado():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'empleado':
        return redirect(url_for('index'))
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    
    # Obtener notificaciones del empleado
    notificaciones_empleado = [
        n for n in empresa.get('notificaciones', []) 
        if n['usuario_destino'] == session['usuario']
    ]
    
    # Marcar notificaciones como leídas
    for notificacion in notificaciones_empleado:
        if not notificacion['leida']:
            notificacion['leida'] = True
    
    guardar_datos(datos)
    
    return render_template('notificaciones_empleado.html', 
                         notificaciones=notificaciones_empleado,
                         nombre=session['nombre'],
                         empresa_nombre=session['empresa_nombre'])

@app.route('/crear_empleado', methods=['POST'])
def crear_empleado():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'jefe':
        return redirect(url_for('index'))
    
    usuario = request.form['usuario']
    password = request.form['password']
    nombre = request.form['nombre']
    email = request.form.get('email', '')
    departamento = request.form.get('departamento', '')
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    
    # Verificar límite de usuarios del plan
    suscripcion = empresa.get('suscripcion', {})
    max_usuarios = suscripcion.get('max_usuarios', 5)
    empleados_actuales = len([u for u in empresa['usuarios'].values() if u['rol'] == 'empleado'])
    
    if empleados_actuales >= max_usuarios:
        flash(f'Has alcanzado el límite de {max_usuarios} empleados de tu plan. Actualiza tu plan para agregar más.')
        return redirect(url_for('dashboard_jefe'))
    
    # Verificar si el usuario ya existe
    if usuario in empresa['usuarios']:
        flash('El nombre de usuario ya existe. Por favor, elige otro.')
        return redirect(url_for('dashboard_jefe'))
    
    # Crear nuevo empleado
    empresa['usuarios'][usuario] = {
        'password': password,
        'rol': 'empleado',
        'nombre': nombre,
        'email': email,
        'departamento': departamento,
        'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'creado_por': session['usuario']
    }
    
    # Actualizar estadísticas
    empresa['estadisticas']['ultima_actividad'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    guardar_datos(datos)
    flash(f'Empleado {nombre} creado exitosamente.')
    return redirect(url_for('dashboard_jefe'))

@app.route('/eliminar_empleado/<string:usuario>')
def eliminar_empleado(usuario):
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'jefe':
        return redirect(url_for('index'))
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    
    # No permitir eliminar al jefe
    if usuario in empresa['usuarios'] and empresa['usuarios'][usuario]['rol'] == 'jefe':
        flash('No se puede eliminar al usuario jefe.')
        return redirect(url_for('dashboard_jefe'))
    
    # Verificar si el empleado tiene tareas asignadas
    tareas_empleado = [t for t in empresa['tareas'] if t['asignado_a'] == usuario]
    if tareas_empleado:
        flash('No se puede eliminar al empleado porque tiene tareas asignadas.')
        return redirect(url_for('dashboard_jefe'))
    
    # Eliminar empleado
    if usuario in empresa['usuarios']:
        del empresa['usuarios'][usuario]
        guardar_datos(datos)
        flash('Empleado eliminado exitosamente.')
    
    return redirect(url_for('dashboard_jefe'))

@app.route('/crear_tarea', methods=['POST'])
def crear_tarea():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'jefe':
        return redirect(url_for('index'))
    
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    asignado_a = request.form['asignado_a']
    prioridad = request.form['prioridad']
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    
    # Verificar límite de tareas del plan
    suscripcion = empresa.get('suscripcion', {})
    max_tareas = suscripcion.get('max_tareas', 50)
    tareas_actuales = len(empresa['tareas'])
    
    if tareas_actuales >= max_tareas:
        flash(f'Has alcanzado el límite de {max_tareas} tareas de tu plan. Actualiza tu plan para crear más.')
        return redirect(url_for('dashboard_jefe'))
    
    nueva_tarea = {
        'id': len(empresa['tareas']) + 1,
        'titulo': titulo,
        'descripcion': descripcion,
        'asignado_a': asignado_a,
        'prioridad': prioridad,
        'estado': 'pendiente',
        'progreso': 0,
        'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'fecha_limite': request.form.get('fecha_limite', ''),
        'comentarios': [],
        'creado_por': session['usuario']
    }
    
    empresa['tareas'].append(nueva_tarea)
    
    # Asegurar que las estadísticas existan
    if 'estadisticas' not in empresa:
        empresa['estadisticas'] = {
            'tareas_pendientes': 0,
            'tareas_en_progreso': 0,
            'tareas_completadas': 0,
            'usuarios_activos': 0,
            'ultima_actividad': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # Actualizar estadísticas
    empresa['estadisticas']['tareas_pendientes'] = len([t for t in empresa['tareas'] if t['estado'] in ['pendiente', 'asignada']])
    empresa['estadisticas']['ultima_actividad'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    guardar_datos(datos)
    
    flash('Tarea creada exitosamente')
    return redirect(url_for('dashboard_jefe'))

@app.route('/actualizar_progreso', methods=['POST'])
def actualizar_progreso():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'empleado':
        return redirect(url_for('index'))
    
    tarea_id = int(request.form['tarea_id'])
    progreso = int(request.form['progreso'])
    estado = request.form['estado']
    comentario = request.form.get('comentario', '')
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    
    for tarea in empresa['tareas']:
        if tarea['id'] == tarea_id and tarea['asignado_a'] == session['usuario']:
            tarea['progreso'] = progreso
            tarea['estado'] = estado
            
            # Manejar evidencia si se subió un archivo
            if 'evidencia' in request.files:
                archivo = request.files['evidencia']
                if archivo.filename != '':
                    # Crear directorio de evidencias si no existe
                    empresa_id = session['empresa_id']
                    evidencias_dir = os.path.join('static', 'evidencias', empresa_id, str(tarea_id))
                    os.makedirs(evidencias_dir, exist_ok=True)
                    
                    # Guardar archivo con timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{archivo.filename}"
                    filepath = os.path.join(evidencias_dir, filename)
                    archivo.save(filepath)
                    
                    # Agregar información de evidencia a la tarea
                    if 'evidencias' not in tarea:
                        tarea['evidencias'] = []
                    
                    tarea['evidencias'].append({
                        'archivo': filename,
                        'ruta': filepath,
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'subido_por': session['nombre']
                    })
            
            # Agregar comentario si existe
            if comentario:
                tarea['comentarios'].append({
                    'texto': comentario,
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'autor': session['nombre']
                })
            
            # Si el progreso es 100%, marcar como completada automáticamente y generar notificación
            if progreso == 100 and estado != 'cancelada':
                estado_anterior = tarea['estado']
                tarea['estado'] = 'completada'
                
                # Generar notificación para el jefe solo si la tarea no estaba ya completada
                if estado_anterior != 'completada':
                    if 'notificaciones' not in empresa:
                        empresa['notificaciones'] = []
                    
                    notificacion_completada = {
                        'id': len(empresa['notificaciones']) + 1,
                        'tipo': 'tarea_completada',
                        'titulo': f'✅ Tarea Completada: {tarea["titulo"]}',
                        'mensaje': f'El empleado {empresa["usuarios"][session["usuario"]]["nombre"]} ha completado la tarea "{tarea["titulo"]}".',
                        'tarea_id': tarea['id'],
                        'empleado_id': session['usuario'],
                        'usuario_destino': 'jefe',
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'leida': False,
                        'urgencia': 'baja'
                    }
                    
                    empresa['notificaciones'].append(notificacion_completada)
            
            break
    
    guardar_datos(datos)
    flash('Progreso actualizado exitosamente')
    return redirect(url_for('dashboard_empleado'))

@app.route('/eliminar_tarea/<int:tarea_id>')
def eliminar_tarea(tarea_id):
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'jefe':
        return redirect(url_for('index'))
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    empresa['tareas'] = [t for t in empresa['tareas'] if t['id'] != tarea_id]
    guardar_datos(datos)
    
    flash('Tarea eliminada exitosamente')
    return redirect(url_for('dashboard_jefe'))

@app.route('/ver_tarea/<int:tarea_id>')
def ver_tarea(tarea_id):
    if 'usuario' not in session or 'empresa_id' not in session:
        return redirect(url_for('index'))
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    tarea = next((t for t in empresa['tareas'] if t['id'] == tarea_id), None)
    
    if not tarea:
        flash('Tarea no encontrada')
        return redirect(url_for('dashboard_jefe' if session['rol'] == 'jefe' else 'dashboard_empleado'))
    
    # Verificar permisos
    if session['rol'] == 'empleado' and tarea['asignado_a'] != session['usuario']:
        flash('No tienes permiso para ver esta tarea')
        return redirect(url_for('dashboard_empleado'))
    
    return render_template('ver_tarea.html', 
                         tarea=tarea, 
                         nombre=session['nombre'],
                         empresa_nombre=session['empresa_nombre'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
