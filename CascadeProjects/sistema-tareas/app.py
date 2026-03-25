from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_sistema_tareas'

# Archivo para persistencia de datos
DATA_FILE = 'data.json'

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'admin_maestro': {
            'usuario': 'admin',
            'password': 'superadmin123'
        },
        'empresas': {},
        'global_config': {
            'modo_mantenimiento': False,
            'version': '1.0.0'
        }
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
    
    # Calcular estadísticas
    stats = {
        'total_empresas': len(empresas),
        'empresas_activas': len([e for e in empresas.values() if e.get('estado', 'activo') == 'activo']),
        'total_usuarios': sum(len(e.get('usuarios', {})) for e in empresas.values()),
        'total_tareas': sum(len(e.get('tareas', [])) for e in empresas.values())
    }
    
    return render_template('dashboard_admin.html', 
                         empresas=empresas, 
                         stats=stats,
                         admin_usuario=session.get('admin_usuario'))

@app.route('/admin/crear_empresa', methods=['GET', 'POST'])
def crear_empresa():
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        datos = cargar_datos()
        empresa_id = f"emp_{len(datos['empresas']) + 1}"
        
        # Datos de la empresa
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
            'usuarios': {},
            'tareas': []
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
        guardar_datos(datos)
        
        flash(f'Empresa "{empresa["nombre"]}" creada exitosamente')
        return redirect(url_for('dashboard_admin'))
    
    return render_template('crear_empresa.html')

@app.route('/admin/ver_empresa/<empresa_id>')
def ver_empresa(empresa_id):
    if 'admin_maestro' not in session:
        return redirect(url_for('admin_login'))
    
    datos = cargar_datos()
    if empresa_id not in datos['empresas']:
        flash('Empresa no encontrada')
        return redirect(url_for('dashboard_admin'))
    
    empresa = datos['empresas'][empresa_id]
    return render_template('ver_empresa.html', empresa=empresa, empresa_id=empresa_id)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard_jefe')
def dashboard_jefe():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'jefe':
        return redirect(url_for('index'))
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    tareas = empresa['tareas']
    usuarios = {k: v for k, v in empresa['usuarios'].items() if v['rol'] == 'empleado'}
    
    return render_template('dashboard_jefe.html', 
                         tareas=tareas, 
                         usuarios=usuarios,
                         nombre=session['nombre'],
                         empresa_nombre=session['empresa_nombre'])

@app.route('/dashboard_empleado')
def dashboard_empleado():
    if 'usuario' not in session or 'empresa_id' not in session or session['rol'] != 'empleado':
        return redirect(url_for('index'))
    
    datos = cargar_datos()
    empresa = datos['empresas'][session['empresa_id']]
    tareas_empleado = [t for t in empresa['tareas'] if t['asignado_a'] == session['usuario']]
    
    return render_template('dashboard_empleado.html', 
                         tareas=tareas_empleado,
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
        'comentarios': []
    }
    
    empresa['tareas'].append(nueva_tarea)
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
            
            if comentario:
                tarea['comentarios'].append({
                    'texto': comentario,
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'autor': session['nombre']
                })
            
            if progreso == 100:
                tarea['estado'] = 'completada'
            
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
